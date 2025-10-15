from typing import Any

from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.error import Error


async def handle_xadd(args: list[str], redis_state: RedisState) -> RESPType[Any]:
    """Handle XADD command."""
    return Error(f"XADD: NON IMPLEMENTED len(args) = {len(args)} args = {args}")
