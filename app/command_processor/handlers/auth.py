from typing import Any

from app.connection.connection import Connection
from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.bulk_string import BulkString
from app.resp.error import Error


async def handle_auth(
    args: list[str], redis_state: RedisState, connection: Connection
) -> RESPType[Any]:
    """Handle AUTH command."""
    if args:
        return Error(f"AUTH command should not have arguments. args = {args}")
    return BulkString("AUTH: NotImplementedError")
