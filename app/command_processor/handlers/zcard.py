from typing import Any

from app.connection.connection import Connection
from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.error import Error


async def handle_zcard(
    args: list[str], redis_state: RedisState, connection: Connection
) -> RESPType[Any]:
    """Handle ZCARD command."""
    if len(args) != 1:
        return Error(f"ZCARD command should have only one argument. args = {args}")
    return Error("ZCARD: NotImplementedError")
