from typing import Any

from app.connection.connection import Connection
from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.error import Error
from app.resp.simple_string import SimpleString


async def handle_set(
    args: list[str], redis_state: RedisState, connection: Connection
) -> RESPType[Any]:
    """Handle SET command."""
    expire_set_ms: int | None = None
    if len(args) == 4:
        if args[2].lower() != "px":
            return Error(f"SET: args[2] = {args[2]} args = {args}")
        try:
            expire_set_ms = int(args[3])
        except ValueError:
            return Error(f"SET: args[3] = {args[3]} args = {args}")
    elif len(args) != 2:
        return Error(f"SET: len(args) = {len(args)} args = {args}")
    redis_state.redis_variables.set(args[0], args[1], expire_set_ms=expire_set_ms)
    return SimpleString("OK")
