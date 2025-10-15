from typing import Any

from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.error import Error
from app.resp.simple_string import SimpleString


async def handle_xadd(args: list[str], redis_state: RedisState) -> RESPType[Any]:
    """Handle XADD command."""
    if not args or len(args) % 2 == 1:
        return Error(f"XADD: len(args) = {len(args)} args = {args}")
    return SimpleString(redis_state.redis_variables.xadd(args[0], args[1], args[2:]))
