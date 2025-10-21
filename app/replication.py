import asyncio

from app import const
from app.connection.async_reader import AsyncReaderHandler
from app.connection.async_writer import AsyncWriterHandler
from app.exceptions import ReplicationFailedError
from app.logging_config import get_logger
from app.redis_state import RedisState
from app.resp.array import Array
from app.resp.bulk_string import BulkString
from app.resp.file_dump import FileDump
from app.resp.simple_string import SimpleString

logger = get_logger(__name__)


async def _retry_open_connection(
    host: str, port: int, max_retries: int = const.REPLICA_MAX_RETRIES
) -> tuple[asyncio.StreamReader, asyncio.StreamWriter]:
    if max_retries <= 0:
        raise ReplicationFailedError
    try:
        reader, writer = await asyncio.open_connection(host, port)
    except OSError:
        logger.error("Connection attempt failed, retrying...")
        await asyncio.sleep(0.1 * (1 + const.REPLICA_MAX_RETRIES - max_retries))
        return await _retry_open_connection(host, port, max_retries=max_retries - 1)
    return reader, writer


async def replica_redis(  # noqa: WPS210
    redis_state: RedisState,
    started_event: asyncio.Event,
    shutdown_event: asyncio.Event,
    name: str = "replica",
) -> None:
    master_host, master_port_str = redis_state.redis_config.replicaof.split(" ")
    master_port = int(master_port_str)
    logger.info(f"{name} Starting Replica")
    try:
        reader, writer = await _retry_open_connection(master_host, master_port)
    except ReplicationFailedError:
        logger.error(f"{name} Failed to connect after {const.REPLICA_MAX_RETRIES} attempts")
        started_event.set()
        return
    rw_closing_event = asyncio.Event()
    async_writer = AsyncWriterHandler(writer=writer, rw_closing_event=rw_closing_event)
    logger.info(f"{name} {async_writer.sockname}: Connected to {async_writer.peername}")
    async_reader = AsyncReaderHandler(
        reader=reader, peername=async_writer.peername, rw_closing_event=rw_closing_event
    )

    closing_event_task: asyncio.Task[None] = asyncio.create_task(
        closure_loop(rw_closing_event=rw_closing_event, shutdown_event=shutdown_event)
    )
    do_replica_task: asyncio.Task[None] = asyncio.create_task(
        do_replica(
            async_reader=async_reader,
            async_writer=async_writer,
            rw_closing_event=rw_closing_event,
            started_event=started_event,
            redis_state=redis_state,
        )
    )
    await asyncio.wait([do_replica_task, closing_event_task], return_when=asyncio.FIRST_COMPLETED)
    started_event.set()
    rw_closing_event.set()
    do_replica_task.cancel()


async def closure_loop(rw_closing_event: asyncio.Event, shutdown_event: asyncio.Event) -> None:
    tasks = [
        asyncio.create_task(rw_closing_event.wait()),
        asyncio.create_task(shutdown_event.wait()),
    ]
    await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
    rw_closing_event.set()


async def do_replica(
    async_reader: AsyncReaderHandler,
    async_writer: AsyncWriterHandler,
    rw_closing_event: asyncio.Event,
    started_event: asyncio.Event,
    redis_state: RedisState,
) -> None:
    try:
        handshake = await _perform_handshake(
            async_reader=async_reader, async_writer=async_writer, port=redis_state.redis_config.port
        )
    except asyncio.CancelledError:
        logger.info("Handshake cancelled")
        raise
    if not handshake:
        logger.info("It is not expected reply, replication failed")
        return
    logger.info("Reading file")
    file_dump = await async_reader.read(parser=FileDump.from_bytes)
    logger.debug(f"I have received {file_dump}")
    started_event.set()
    logger.info("Replication TODO")

    await rw_closing_event.wait()
    logger.info("Closing replication")


async def _perform_handshake(
    async_reader: AsyncReaderHandler,
    async_writer: AsyncWriterHandler,
    port: int,
) -> bool:
    """Perform Redis replication handshake. Returns True if successful."""
    messages: list[tuple[Array, str]] = [
        (Array([BulkString("PING")]), "PONG"),
        (
            Array(
                [
                    BulkString("REPLCONF"),
                    BulkString("listening-port"),
                    BulkString(str(port)),
                ]
            ),
            "OK",
        ),
        (
            Array(
                [
                    BulkString("REPLCONF"),
                    BulkString("capa"),
                    BulkString("psync2"),
                ]
            ),
            "OK",
        ),
        (Array([BulkString("PSYNC"), BulkString("?"), BulkString("1")]), "FULLRESYNC"),
    ]

    for message, expected_reply in messages:
        await async_writer.write(message.to_bytes)  # noqa: WPS476
        reply = await async_reader.read(parser=SimpleString.from_bytes)  # noqa: WPS476
        logger.debug(f"I have received {reply}")

        if not isinstance(reply, SimpleString):
            return False

        first_word = reply.data.split(" ")[0]
        if first_word != expected_reply:
            return False

    return True
