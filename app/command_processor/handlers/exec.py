from typing import Any

from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.error import Error


async def handle_exec(args: list[str], redis_state: RedisState) -> RESPType[Any]:
    """Handle EXEC command."""
    return Error(f"EXEC: len(args) = {len(args)} args = {args}")
