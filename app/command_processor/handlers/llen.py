from typing import Any

from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.error import Error
from app.resp.integer import Integer


async def handle_llen(args: list[str], redis_state: RedisState) -> RESPType[Any]:
    """Handle LLEN command."""
    if len(args) != 1:
        return Error(f"LPUSH: len(args) = {len(args)} args = {args}")
    return Integer(redis_state.redis_variables.llen(args[0]))
