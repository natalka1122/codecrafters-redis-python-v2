from typing import Any

from app.connection.connection import Connection
from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.error import Error


async def handle_zrem(
    args: list[str], redis_state: RedisState, connection: Connection
) -> RESPType[Any]:
    """Handle ZREM command."""
    if len(args) != 1:
        return Error(f"ZREM command should have only one argument. args = {args}")
    return Error("ZREM: NotImplementedError")
