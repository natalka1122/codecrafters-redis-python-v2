from typing import Any

from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.error import Error


async def handle_xread_streams(args: list[str], redis_state: RedisState) -> RESPType[Any]:
    """Handle XREAD STREAMS command."""
    return Error(f"XREAD STREAMS: NON IMPLEMENTED len(args) = {len(args)} args = {args}")
