from typing import Any

from app.exceptions import ItemNotFoundError
from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.bulk_string import BulkString, NullBulkString
from app.resp.error import Error


async def handle_get(args: list[str], redis_state: RedisState) -> RESPType[Any]:
    """Handle GET command."""
    if len(args) != 1:
        return Error(f"GET command should have only one argument. args = {args}")
    try:
        response = redis_state.redis_variables.get(args[0])
    except ItemNotFoundError:
        return NullBulkString("")
    return BulkString(response)
