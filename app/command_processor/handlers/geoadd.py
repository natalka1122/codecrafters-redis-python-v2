from typing import Any

from app.connection.connection import Connection
from app.const import MAX_LATITUDE, MAX_LONGITUDE, MIN_LATITUDE, MIN_LONGITUDE
from app.exceptions import InvalidGeoError, ItemWrongTypeError
from app.geocode.encode import encode
from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.error import Error
from app.resp.integer import Integer


async def handle_geoadd(
    args: list[str], redis_state: RedisState, connection: Connection
) -> RESPType[Any]:
    """Handle GEOADD command."""
    if len(args) != 4:
        return Error(f"GEOADD command should have four arguments. args = {args}")
    key = args[0]
    try:
        score = _geo_validate_and_encode(args[1], args[2])
    except InvalidGeoError:
        return Error(f"ERR invalid longitude,latitude pair {args[1]},{args[2]}")
    member = args[3]
    try:
        return Integer(redis_state.redis_variables.zadd(key, score, member))
    except ItemWrongTypeError:
        return Error("WRONGTYPE Operation against a key holding the wrong kind of value")


def _geo_validate_and_encode(longitude_str: str, latitude_str: str) -> int:  # noqa: WPS238
    try:
        longitude = float(longitude_str)
    except ValueError:
        raise InvalidGeoError
    if longitude < MIN_LONGITUDE or longitude > MAX_LONGITUDE:
        raise InvalidGeoError
    try:
        latitude = float(latitude_str)
    except ValueError:
        raise InvalidGeoError
    if latitude < MIN_LATITUDE or latitude > MAX_LATITUDE:
        raise InvalidGeoError
    return encode(latitude=latitude, longitude=longitude)
