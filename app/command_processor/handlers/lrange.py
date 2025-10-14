from typing import Any

from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.array import Array
from app.resp.bulk_string import BulkString
from app.resp.error import Error


async def handle_lrange(args: list[str], redis_state: RedisState) -> RESPType[Any]:
    """Handle LRANGE command."""
    if len(args) != 3:
        return Error(f"LRANGE command should have only three arguments. args = {args}")
    try:
        return Array(
            list(
                map(
                    BulkString,
                    redis_state.redis_variables.lrange(
                        args[0], int(args[1]), int(args[2])
                    ),
                )
            )
        )
    except ValueError:
        return Error(f"LRANGE has wrong arguments. args = {args}")
