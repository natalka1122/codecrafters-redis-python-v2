from typing import Any

from app.connection.connection import Connection
from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.error import Error
from app.resp.simple_string import SimpleString


async def handle_replconf_lp(
    args: list[str], redis_state: RedisState, connection: Connection
) -> RESPType[Any]:
    """Handle REPLCONF LISTENING-PORT command."""
    if len(args) != 1:
        return Error(
            f"REPLCONF LISTENING-PORT command should have only one argument. args = {args}"
        )
    return SimpleString("OK")


async def handle_replconf_capa(
    args: list[str], redis_state: RedisState, connection: Connection
) -> RESPType[Any]:
    """Handle REPLCONF CAPA command."""
    if len(args) != 1:
        return Error(f"REPLCONF CAPA command should have 3 arguments. args = {args}")
    return SimpleString("OK")
