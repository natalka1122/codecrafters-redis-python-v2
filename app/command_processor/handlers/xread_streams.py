from typing import Any

from app.redis_state import RedisState
from app.resp.array import Array
from app.resp.base import RESPType
from app.resp.error import Error


async def handle_xread_streams(
    args: list[str], redis_state: RedisState
) -> RESPType[Any]:
    """Handle XREAD STREAMS command."""
    if len(args) % 2 != 0:
        return Error(f"XREAD STREAMS: len(args) = {len(args)} args = {args}")
    result: list[Array] = []
    middle = len(args) // 2
    for index in range(middle):
        result.append(
            redis_state.redis_variables.xread_one_stream(
                args[index], args[middle + index]
            )
        )
    return Array(result)
