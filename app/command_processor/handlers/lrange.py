from typing import Any

from app.exceptions import ItemNotFoundError
from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.bulk_string import BulkString
from app.resp.error import Error


async def handle_lrange(args: list[str], redis_state: RedisState) -> RESPType[Any]:
    """Handle LRANGE command."""
    if len(args) != 3:
        return Error(f"LRANGE command should have only three argument. args = {args}")
    try:
        response = redis_state.redis_variables.get(args[0])
    except ItemNotFoundError:
        response = ""
    return BulkString(response)
