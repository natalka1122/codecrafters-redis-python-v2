from typing import Any

from app.connection.connection import Connection
from app.redis_state import RedisState
from app.resp.array import Array
from app.resp.base import RESPType
from app.resp.bulk_string import BulkString
from app.resp.error import Error


async def handle_geosearch(
    args: list[str], redis_state: RedisState, connection: Connection
) -> RESPType[Any]:
    """Handle GEOSEARCH command."""
    if len(args) != 7:
        return Error(f"GEOSEARCH command should have seven arguments. args = {args}")
    if (
        args[1].upper() != "FROMLONLAT"  # noqa: WPS221
        or args[4].upper() != "BYRADIUS"
        or args[6].upper() != "M"
    ):
        return Error("GEOSEARCH: NotImplementedError")
    key = args[0]
    try:  # noqa: WPS229
        longitude = float(args[2])
        latitude = float(args[3])
        distance = float(args[5])
    except ValueError:
        return Error("ERR value is not an float or out of range")
    return Array(
        [
            BulkString(x)
            for x in redis_state.redis_variables.geosearch(key, longitude, latitude, distance)
        ]
    )
