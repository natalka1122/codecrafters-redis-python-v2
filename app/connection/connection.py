from asyncio import (
    CancelledError,
    Event,
    StreamReader,
    StreamWriter,
    Task,
    create_task,
    wait,
)
from typing import Any, Optional

from app.command_processor.command import Command
from app.connection.async_reader import AsyncReaderHandler, ParserType
from app.connection.async_writer import AsyncWriterHandler
from app.logging_config import get_logger
from app.resp.base import RESPType

logger = get_logger(__name__)


class Connection:
    def __init__(self, reader: StreamReader, writer: StreamWriter) -> None:
        self.closed = Event()
        self.closing = Event()
        self._writer = AsyncWriterHandler(writer, rw_closing_event=self.closing)
        self.sockname = self._writer.sockname
        self.peername = self._writer.peername
        self._reader = AsyncReaderHandler(
            reader, peername=self.peername, rw_closing_event=self.closing
        )
        self._is_transaction: bool = False
        self.transaction: list[Command] = []
        self.is_replica = False
        self._closure_task: Task[None] = create_task(
            self._closure_loop(), name="Connection._closure_loop"
        )
        logger.debug(f"{self}: New connection")

    def __repr__(self) -> str:
        return self.peername

    @property
    def is_transaction(self) -> bool:
        return self._is_transaction

    @is_transaction.setter
    def is_transaction(self, value: bool) -> None:
        if not value:
            self.transaction = []
        self._is_transaction = value

    async def read(self, parser: Optional[ParserType] = None) -> RESPType[Any]:
        try:
            result = await self._reader.read(parser=parser)
        except CancelledError:
            logger.info("Connection.read CancelledError")
            raise
        return result

    async def write(self, data: bytes) -> None:
        try:
            await self._writer.write(data)
        except CancelledError:
            logger.info("Connection.write CancelledError")
            raise

    async def _closure_loop(self) -> None:
        await self.closing.wait()
        logger.info(f"{self}: Closing connection")
        writer_closure_task = create_task(self._writer.closed.wait())
        reader_closure_task = create_task(self._reader.closed.wait())
        await wait([writer_closure_task, reader_closure_task])
        self.closed.set()
        logger.info(f"{self}: Connection closed")
