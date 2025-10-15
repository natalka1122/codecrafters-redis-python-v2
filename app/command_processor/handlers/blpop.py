from typing import Any

from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.error import Error


async def handle_blpop(args: list[str], redis_state: RedisState) -> RESPType[Any]:
    """Handle BLPOP command."""
    if len(args) != 2:
        return Error(f"BLPOP: len(args) = {len(args)} args = {args}")
    return Error(f"BLPOP has wrong arguments. args = {args}")
