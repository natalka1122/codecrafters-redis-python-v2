from typing import Any

from app.connection.connection import Connection
from app.logging_config import get_logger
from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.error import Error
from app.resp.simple_string import SimpleString

logger = get_logger(__name__)


async def handle_discard(
    args: list[str], redis_state: RedisState, connection: Connection
) -> tuple[bool, RESPType[Any]]:
    """Handle DISCARD command."""
    logger.error(f"DISCARD: Not Implemented len(args) = {len(args)} args = {args}")
    return False, SimpleString("OK")


async def handle_discard_no_multy(
    args: list[str], redis_state: RedisState
) -> RESPType[Any]:
    """Handle DISCARD command outside transaction"""
    return Error("ERR DISCARD without MULTI")
