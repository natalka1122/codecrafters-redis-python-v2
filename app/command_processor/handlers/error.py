"""Error command handler."""

from typing import Any

from app.connection.connection import Connection
from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.error import Error


async def handle_error(
    args: list[str], redis_state: RedisState, connection: Connection
) -> RESPType[Any]:
    """Handle ERROR command."""
    return Error(f"{args}")


async def handle_error_inside_subscription(
    args: list[str], redis_state: RedisState, connection: Connection
) -> RESPType[Any]:
    """Handle error command inside subcribed mode"""
    return Error("ERR Can't execute ''")
