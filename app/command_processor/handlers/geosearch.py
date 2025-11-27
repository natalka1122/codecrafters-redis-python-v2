from typing import Any

from app.connection.connection import Connection
from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.error import Error


async def handle_geosearch(
    args: list[str], redis_state: RedisState, connection: Connection
) -> RESPType[Any]:
    """Handle GEOSEARCH command."""
    if len(args) != 4:
        return Error(f"GEOSEARCH command should have four arguments. args = {args}")
    return Error("GEOSEARCH: NotImplementedError")
