from typing import Any

from app.connection.connection import Connection
from app.logging_config import get_logger
from app.redis_state import RedisState
from app.resp.array import Array
from app.resp.base import RESPType
from app.resp.error import Error

logger = get_logger(__name__)


async def handle_exec(
    args: list[str], redis_state: RedisState, connection: Connection
) -> tuple[bool, RESPType[Any]]:
    """Handle EXEC command."""
    logger.error(f"EXEC: Not Implemented len(args) = {len(args)} args = {args}")
    return False, Array([])


async def handle_exec_no_multi(
    args: list[str], redis_state: RedisState
) -> RESPType[Any]:
    """Handle EXEC command outside transaction"""
    return Error("ERR EXEC without MULTI")
