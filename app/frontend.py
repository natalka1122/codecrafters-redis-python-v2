import asyncio
import base64

from app.command_processor.processor import processor, transaction
from app.connection.connection import Connection
from app.const import EMPTY_RDB_B64, HOST
from app.exceptions import ReaderClosedError, WriterClosedError
from app.logging_config import get_logger
from app.redis_state import RedisState
from app.resp.file_dump import FileDump

logger = get_logger(__name__)


async def master_redis(
    redis_state: RedisState,
    started_event: asyncio.Event,
    shutdown_event: asyncio.Event,
) -> None:
    try:
        server = await asyncio.start_server(
            lambda reader, writer: handle_client(
                reader=reader,
                writer=writer,
                redis_state=redis_state,
            ),
            HOST,
            redis_state.redis_config.port,
        )
    except OSError as error:
        logger.error(f"Cannot start server: {error}")
        shutdown_event.set()
        started_event.set()
        return
    addrs = ", ".join(str(sock.getsockname()) for sock in server.sockets)
    logger.info(f"Server is serving on {addrs}")
    started_event.set()

    async with server:
        # Wait for shutdown or cancellation
        try:
            await shutdown_event.wait()  # instead of serve_forever()
        except asyncio.CancelledError:
            logger.info("Server cancelled, shutting down...")
            raise
        finally:
            logger.info("Closing server...")
            await close_connections(list(redis_state.connections.values()))


async def close_connections(connections: list[Connection]) -> None:
    if not connections:
        logger.info("Server closed")
        return
    tasks: list[asyncio.Task[bool]] = []
    for connection in connections:
        connection.closing.set()
        tasks.append(asyncio.create_task(connection.closed.wait()))
    done, pending = await asyncio.wait(tasks)
    len_pending = len(pending)
    if len_pending > 0:
        logger.info(f"Closed {len(done)} connections, {len_pending} connections left")
    else:
        logger.info(f"Closed all {len(done)} connections")


async def handle_client(  # noqa: WPS217
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    redis_state: RedisState,
) -> None:
    connection = redis_state.add_new_connection(reader=reader, writer=writer)
    logger.debug(f"{connection.peername}: New connection")

    try:
        while not connection.is_replica:  # noqa: WPS457
            data_parsed = await connection.read()
            logger.debug(f"{connection.peername}: Received command {data_parsed}")
            if connection.is_transaction:
                response = await transaction(data_parsed, redis_state, connection)
            else:
                response = await processor(data_parsed, redis_state, connection)
            await connection.write(response.to_bytes)
            logger.debug(f"{connection.peername}: Sent response {response!r}")

    except (ReaderClosedError, WriterClosedError):
        logger.debug(f"{connection.peername}: Client disconnected")
    except asyncio.CancelledError:
        logger.info(f"{connection.peername}: Connection handler cancelled.")
        raise  # Don't clean up - server will handle it
    except Exception as e:
        logger.error(f"{connection.peername}: Error in client handler: {e}")

    if connection.is_replica:
        await handle_replica(connection=connection, redis_state=redis_state)
    # Clean up the connection (only reached if not cancelled)
    await _close_connection(connection, redis_state)


async def handle_replica(connection: Connection, redis_state: RedisState) -> None:
    if not connection.is_replica:
        raise NotImplementedError

    file_dump = FileDump(base64.b64decode(EMPTY_RDB_B64)).to_bytes
    await connection.write(file_dump)
    logger.info(f"{connection.peername}: Sent FileDump")
    redis_state.replicas[connection.peername] = connection

    await connection.closed.wait()
    logger.info(f"{connection.peername}: Replica is done")


async def _close_connection(connection: Connection, redis_state: RedisState) -> None:
    logger.info(f"{connection.peername}: Closing connection")
    await redis_state.purge_connection(connection)
    logger.debug(f"{connection.peername}: Connection closed")
