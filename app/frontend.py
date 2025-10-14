import asyncio

from app import const
from app.connection.connection import Connection
from app.exceptions import ReaderClosedError, WriterClosedError
from app.logging_config import get_logger
from app.processor import processor
from app.redis_state import RedisState

logger = get_logger(__name__)


async def master_redis(
    started_event: asyncio.Event, shutdown_event: asyncio.Event
) -> None:
    redis_state = RedisState()
    try:
        server = await asyncio.start_server(
            lambda reader, writer: handle_client(
                reader=reader,
                writer=writer,
                redis_state=redis_state,
            ),
            const.HOST,
            const.DEFAULT_PORT,
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
            # Cancel all active client handlers
            await asyncio.gather(
                *(
                    connection.close()
                    for connection in redis_state.connections.values()
                ),
                return_exceptions=True,  # Don't fail if one close() fails
            )


async def handle_client(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    redis_state: RedisState,
) -> None:
    connection = redis_state.add_new_connection(reader=reader, writer=writer)
    logger.debug(f"{connection.peername}: New connection")

    try:
        while True:  # noqa: WPS457
            data_parsed = await connection.read()
            logger.debug(f"{connection.peername}: Received command {data_parsed}")

            response = await processor(data_parsed, redis_state)
            await connection.write(response.to_bytes)
            logger.debug(f"{connection.peername}: Sent response {response!r}")

    except (ReaderClosedError, WriterClosedError):
        logger.debug(f"{connection.peername}: Client disconnected")
    except asyncio.CancelledError:
        logger.info(f"{connection.peername}: Connection handler cancelled.")
        raise  # Don't clean up - server will handle it
    except Exception as e:
        logger.error(f"{connection.peername}: Error in client handler: {e}")

    # Clean up the connection (only reached if not cancelled)
    await _close_connection(connection, redis_state)


async def _close_connection(connection: Connection, redis_state: RedisState) -> None:
    logger.info(f"{connection.peername}: Closing connection")
    await redis_state.purge_connection(connection)
    logger.debug(f"{connection.peername}: Connection closed")
