from typing import Any

from app.connection.connection import Connection
from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.error import Error
from app.resp.integer import Integer


async def handle_wait(
    args: list[str], redis_state: RedisState, connection: Connection
) -> RESPType[Any]:
    """Handle WAIT command."""
    if len(args) != 2:
        return Error("ERR wrong number of arguments for 'wait' command")
    if not (args[0].isdigit() and args[1].isdigit()):
        return Error("ERR value is not an integer or out of range")
    numreplicas = int(args[0])
    timeout = int(args[1])

    if numreplicas == 0:
        return Integer(0)
    return Integer(-1)
