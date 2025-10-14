from asyncio import CancelledError, Queue, StreamReader, Task, create_task
from contextlib import suppress
from typing import Optional

from app.const import WINDOW_SIZE
from app.exceptions import NeedMoreBytesError, ReaderClosedError
from app.logging_config import get_logger
from app.resp.array import Array

logger = get_logger(__name__)


class AsyncReaderHandler:
    """Handles async read operations with proper error handling and queuing."""

    def __init__(self, reader: StreamReader, peername: str, max_queue_size: int = 10):
        self._reader = reader
        self._read_queue: Queue[Optional[Array]] = Queue(maxsize=max_queue_size)
        self._closed = False
        self._buffer: bytes = b""
        self.peername = peername
        self._reader_task: Task[None] = create_task(self._reader_loop())

    async def read(self) -> Array:
        """Get data for async reading."""
        if self._closed and self._read_queue.empty():
            raise ReaderClosedError

        result = await self._read_queue.get()

        # Check if we got a sentinel value (None) indicating closure
        if result is None:
            raise ReaderClosedError

        return result

    async def close(self) -> None:
        if self._closed:
            return
        self._closed = True
        if not self._reader_task.done():
            self._reader_task.cancel()
            with suppress(CancelledError):
                await self._reader_task
        if self._buffer:
            logger.warning(
                f"{self.peername}: Unused bytes in buffer at closure: {self._buffer!r}"
            )
        if not self._read_queue.empty():
            logger.warning(f"{self.peername}: Unused data in read queue at closure")
        logger.info(f"{self.peername}: Reader closed")

    async def _reader_loop(self) -> None:
        """Background task that processes read requests from the queue."""
        try:
            while not self._closed:
                data = await self._reader.read(WINDOW_SIZE)
                if not data:
                    logger.debug(f"{self.peername}: Connection closed by peer")
                    break
                self._buffer += data
                await self._process_buffer()

        except CancelledError:
            logger.debug(f"{self.peername}: Reader cancelled")
            raise
        except Exception as e:
            logger.error(f"{self.peername}: Reader error: {e}")
        finally:
            self._closed = True
            # Wake up waiting read() calls
            with suppress(Exception):
                self._read_queue.put_nowait(None)

    async def _process_buffer(self) -> None:
        """Process all available commands from the buffer."""
        while True:
            data_resp = self._try_parse_buffer()
            if not data_resp:
                break
            await self._read_queue.put(data_resp)

    def _try_parse_buffer(self) -> Array | None:
        """Try to parse a command from the current buffer."""
        try:
            new_buffer, data_resp = Array.from_bytes(self._buffer)
        except NeedMoreBytesError:
            return None

        self._buffer = new_buffer
        return data_resp
