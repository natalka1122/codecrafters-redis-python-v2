from typing import Any

from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.error import Error


async def handle_multi(args: list[str], redis_state: RedisState) -> RESPType[Any]:
    """Handle MULTI command."""
    return Error(f"MULTI: len(args) = {len(args)} args = {args}")
