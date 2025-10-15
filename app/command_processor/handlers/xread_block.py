from typing import Any

from app.exceptions import NoDataError
from app.redis_state import RedisState
from app.resp.array import Array, NullArray
from app.resp.base import RESPType
from app.resp.error import Error


async def handle_xread_block(args: list[str], redis_state: RedisState) -> RESPType[Any]:
    """Handle XREAD BLOCK command."""
    if len(args) != 4 or args[1].upper() != "STREAMS":
        return Error(f"XREAD BLOCK: len(args) = {len(args)} args = {args}")
    try:
        timeout = int(args[0])
    except ValueError:
        return Error(f"XREAD BLOCK: timeout is not a valid integer. args = {args}")
    try:
        result = await redis_state.redis_variables.xread_block(
            timeout, args[2], args[3]
        )
    except NoDataError:
        return NullArray([])
    return Array([result])
