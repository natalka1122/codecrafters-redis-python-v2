import asyncio
from typing import Optional

from app.connection.connection import Connection
from app.expiring_dict.expiring_dict import ExpiringDict
from app.logging_config import get_logger
from app.redis_config import RedisConfig

logger = get_logger(__name__)


class RedisState:
    def __init__(
        self,
        redis_config: Optional[RedisConfig] = None,
        redis_variables: Optional[ExpiringDict] = None,
    ) -> None:
        self.redis_config: RedisConfig = RedisConfig() if redis_config is None else redis_config
        self.redis_variables: ExpiringDict = (
            ExpiringDict() if redis_variables is None else redis_variables
        )
        self.connections: dict[str, Connection] = dict()
        self.replicas: dict[str, Connection] = dict()

    @property
    def is_master(self) -> bool:
        return len(self.redis_config.replicaof) == 0

    def add_new_connection(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> Connection:
        connection = Connection(reader=reader, writer=writer)
        peername = connection.peername

        # Handle potential duplicate connections
        if peername in self.connections:
            logger.warning(f"Replacing existing connection for {peername}")
            self.connections.pop(peername, None)

        self.connections[peername] = connection
        logger.debug(f"Added new connection {peername}")
        return connection

    async def purge_connection(self, connection: Connection) -> None:
        """Remove and close a connection."""
        peername = connection.peername

        self.replicas.pop(peername, None)
        removed_connection = self.connections.pop(peername, None)
        if removed_connection:
            logger.debug(f"Removed connection {peername}")
        else:
            logger.warning(f"Connection {peername} already removed")

        # Actually close the connection
        connection.closing.set()
        await connection.closed.wait()
