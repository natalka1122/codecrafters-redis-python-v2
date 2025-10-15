from asyncio import StreamReader, StreamWriter

from app.connection.async_reader import AsyncReaderHandler
from app.connection.async_writer import AsyncWriterHandler
from app.exceptions import ReaderClosedError, WriterClosedError
from app.logging_config import get_logger
from app.resp.array import Array

logger = get_logger(__name__)


class Connection:  # noqa: WPS214
    def __init__(
        self,
        reader: StreamReader,
        writer: StreamWriter,
    ) -> None:
        self._writer = AsyncWriterHandler(writer)
        self.peername = self._writer.peername
        self._reader = AsyncReaderHandler(reader, peername=self.peername)
        self._closed = False
        self.is_transaction: bool = False
        logger.debug(f"{self}: New connection")

    def __repr__(self) -> str:
        return self.peername

    @property
    def is_closed(self) -> bool:
        return self._closed

    async def read(self) -> Array:
        try:
            return await self._reader.read()
        except ReaderClosedError:
            await self.close()
            raise

    async def write(self, data: bytes) -> None:
        try:
            await self._writer.write(data)
        except WriterClosedError:
            await self.close()
            raise

    async def close(self) -> None:
        """Close the connection and clean up resources."""
        if self._closed:
            return
        self._closed = True
        logger.debug(f"{self}: Closing connection")

        # Close writer first to stop new data
        await self._writer.close()

        # Close reader
        await self._reader.close()

        logger.info(f"{self}: Connection closed")
