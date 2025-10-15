from typing import Any

from app.command_processor.command import Command
from app.command_processor.command_type import CommandType
from app.command_processor.default_exec import default_exec
from app.command_processor.handlers.discard import (
    handle_discard,
)
from app.command_processor.handlers.exec import handle_exec
from app.command_processor.handlers.multi import (
    handle_multi,
    handle_multi_inside_transaction,
    handle_queued,
)
from app.connection.connection import Connection
from app.logging_config import get_logger
from app.redis_state import RedisState
from app.resp.array import Array
from app.resp.base import RESPType

logger = get_logger(__name__)


async def processor(
    data_resp: Array, redis_state: RedisState, connection: Connection
) -> RESPType[Any]:
    """Process Redis commands and return appropriate responses."""
    command = Command(data_resp)
    # TODO: Rewrite later, maybe all normal handlers need connection too
    # But for now I just patch it
    if command.cmd_type == CommandType.MULTI:
        return await handle_multi(command.args, redis_state, connection)
    return await default_exec(command, redis_state, connection)


async def transaction(
    data_resp: Array, redis_state: RedisState, connection: Connection
) -> RESPType[Any]:
    """Record transaction"""
    command = Command(data_resp)
    # Direct mapping of command types to handlers
    handlers = {
        CommandType.MULTI: handle_multi_inside_transaction,
        CommandType.EXEC: handle_exec,
        CommandType.DISCARD: handle_discard,
    }

    handler = handlers.get(command.cmd_type, handle_queued)
    result = await handler(command, redis_state, connection)
    return result
