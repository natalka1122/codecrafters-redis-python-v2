from typing import Any

from app.connection.connection import Connection
from app.logging_config import get_logger
from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.error import Error
from app.resp.simple_string import SimpleString

logger = get_logger(__name__)


async def handle_multi(
    args: list[str], redis_state: RedisState, connection: Connection
) -> RESPType[Any]:
    """Handle MULTI command."""
    logger.error(f"MULTI: Not Implemented len(args) = {len(args)} args = {args}")
    return SimpleString("OK")


async def handle_multi_inside_transaction(
    args: list[str], redis_state: RedisState, connection: Connection
) -> tuple[bool, RESPType[Any]]:
    """Handle MULTI command inside transaction"""
    return True, Error("ERR MULTI inside MULTI")


async def handle_queued(
    args: list[str], redis_state: RedisState, connection: Connection
) -> tuple[bool, RESPType[Any]]:
    """Default handler inside transaction"""
    logger.error(f"QUEUED: Not Implemented len(args) = {len(args)} args = {args}")
    return True, SimpleString("QUEUED")
