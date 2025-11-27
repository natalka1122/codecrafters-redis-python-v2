from typing import Any

from app.connection.connection import Connection
from app.exceptions import ItemWrongTypeError, NoDataError, NoKeyError
from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.bulk_string import BulkString, NullBulkString
from app.resp.error import Error


async def handle_geodist(
    args: list[str], redis_state: RedisState, connection: Connection
) -> RESPType[Any]:
    """Handle GEODIST command."""
    if len(args) != 3:
        return Error(f"GEODIST command should have three arguments. args = {args}")
    key = args[0]
    member1 = args[1]
    member2 = args[2]
    try:
        return BulkString(str(redis_state.redis_variables.geodist(key, member1, member2)))
    except ItemWrongTypeError:
        return Error("WRONGTYPE Operation against a key holding the wrong kind of value")
    except (NoDataError, NoKeyError):
        return NullBulkString("")
