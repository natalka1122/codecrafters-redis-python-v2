from typing import Any

from app.connection.connection import Connection
from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.error import Error
from app.resp.integer import Integer


async def handle_publish(
    args: list[str], redis_state: RedisState, connection: Connection
) -> RESPType[Any]:
    """Handle PUBLISH command."""
    if len(args) != 2:
        return Error("ERR wrong number of arguments for 'publish' command")
    result = len(redis_state.pubsub.get_by_pub(args[0]))
    return Integer(result)
