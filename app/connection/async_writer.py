from asyncio import CancelledError, StreamWriter

from app.exceptions import WriterClosedError
from app.logging_config import get_logger

logger = get_logger(__name__)


class AsyncWriterHandler:  # noqa: WPS214
    """Handles async write operations with proper error handling and queuing."""

    def __init__(self, writer: StreamWriter):
        self._writer = writer
        self._closed = False
        self.peername = str(writer.get_extra_info("peername"))

    async def write(self, data: bytes) -> None:
        """Write data to the stream."""
        if self._closed:
            raise WriterClosedError
        try:
            await self._perform_write(data)
        except CancelledError:
            logger.debug(f"{self.peername}: Writer loop cancelled")
            raise
        except Exception as e:
            logger.error(f"{self.peername}: Writer error: {e}")
            await self.close()
            raise WriterClosedError(f"Write failed: {e}") from e

    async def close(self) -> None:
        """Close the writer and clean up."""
        if self._closed:
            return
        self._closed = True
        try:
            if not self._writer.is_closing():
                self._writer.close()
        except Exception as exc:  # noqa: WPS110
            logger.debug(f"{self.peername}: Writer already closed: {exc}")
        await self._writer.wait_closed()

    async def _perform_write(self, data: bytes) -> None:
        """Perform the actual write and drain operations."""
        self._writer.write(data)
        await self._writer.drain()
