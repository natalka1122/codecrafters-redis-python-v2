"""Error command handler."""

from typing import Any

from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.error import Error


async def handle_error(args: list[str], redis_state: RedisState) -> RESPType[Any]:
    """Handle ERROR command."""
    return Error(f"{args}")
