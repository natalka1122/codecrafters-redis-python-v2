from typing import Any

from app.connection.connection import Connection
from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.error import Error
from app.resp.integer import Integer


async def handle_rpush(
    args: list[str], redis_state: RedisState, connection: Connection
) -> RESPType[Any]:
    """Handle RPUSH command."""
    if len(args) == 0:
        return Error(f"RPUSH: len(args) = {len(args)} args = {args}")
    result = await redis_state.redis_variables.rpush(args[0], args[1:])
    return Integer(result)
