"""PING command handler."""

from typing import Any

from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.error import Error
from app.resp.simple_string import SimpleString


async def handle_ping(args: list[str], redis_state: RedisState) -> RESPType[Any]:
    """Handle PING command."""
    if args:
        return Error("PING command should not have arguments")
    return SimpleString("PONG")
