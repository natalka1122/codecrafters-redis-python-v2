from typing import Any

from app.exceptions import NotIntegerError
from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.error import Error
from app.resp.integer import Integer


async def handle_incr(args: list[str], redis_state: RedisState) -> RESPType[Any]:
    """Handle INCR command."""
    if len(args) != 1:
        return Error(f"INCR: len(args) = {len(args)} args = {args}")
    try:
        return Integer(redis_state.redis_variables.incr(args[0]))
    except NotIntegerError:
        return Error("ERR value is not an integer or out of range")
