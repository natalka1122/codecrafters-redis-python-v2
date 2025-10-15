from typing import Any

from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.error import Error


async def handle_discard(args: list[str], redis_state: RedisState) -> RESPType[Any]:
    """Handle DISCARD command."""
    return Error(f"DISCARD: len(args) = {len(args)} args = {args}")
