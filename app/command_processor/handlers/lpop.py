from typing import Any

from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.error import Error
from app.resp.bulk_string import BulkString, NullBulkString
from app.resp.array import Array


async def handle_lpop(args: list[str], redis_state: RedisState) -> RESPType[Any]:
    """Handle LPOP command."""
    if len(args) == 1:
        result = redis_state.redis_variables.lpop_one(args[0])
        if result is None:
            return NullBulkString("")
        return BulkString(result)
    if len(args) != 2:
        return Error(f"LPOP: len(args) = {len(args)} args = {args}")

    try:
        counter = int(args[1])
    except ValueError:
        return Error(f"LPOP has wrong arguments. args = {args}")
    results: list[BulkString] = []
    list_length = redis_state.redis_variables.llen(args[0])
    for _ in range(min(counter, list_length)):
        result = redis_state.redis_variables.lpop_one(args[0])
        if result is None:
            results.append(NullBulkString(""))
        else:
            results.append(BulkString(result))

    return Array(results)
