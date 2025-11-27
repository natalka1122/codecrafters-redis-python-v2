from typing import Any

from app.connection.connection import Connection
from app.exceptions import ItemWrongTypeError, NoDataError, NoKeyError
from app.redis_state import RedisState
from app.resp.array import Array, NullArray
from app.resp.base import RESPType
from app.resp.bulk_string import BulkString
from app.resp.error import Error


async def handle_geopos(  # noqa: WPS210
    args: list[str], redis_state: RedisState, connection: Connection
) -> RESPType[Any]:
    """Handle GEOPOS command."""
    if len(args) < 2:
        return Error(f"GEOPOS command should have at least two arguments. args = {args}")
    key = args[0]
    result: list[Array] = []
    for member in args[1:]:
        try:
            latitude, longitude = redis_state.redis_variables.geopos(key, member)
        except ItemWrongTypeError:
            return Error("WRONGTYPE Operation against a key holding the wrong kind of value")
        except (NoDataError, NoKeyError):
            result.append(NullArray([]))
        else:
            item = [BulkString(str(longitude)), BulkString(str(latitude))]
            result.append(Array(item))
    return Array(result)
