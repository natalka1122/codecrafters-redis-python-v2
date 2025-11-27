from typing import Any

from app.connection.connection import Connection
from app.exceptions import InvalidGeoError, ItemWrongTypeError
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
        score = _geo_validate(args[1], args[2])
    except InvalidGeoError:
        return Error(f"ERR invalid longitude,latitude pair {args[1]},{args[2]}")
    member = args[3]
    try:
        return Integer(redis_state.redis_variables.zadd(key, score, member))
    except ItemWrongTypeError:
        return Error("WRONGTYPE Operation against a key holding the wrong kind of value")


def _geo_validate(a: str, b: str) -> int:
    return 0
