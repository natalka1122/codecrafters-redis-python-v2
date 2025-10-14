from typing import Any

from app.redis_state import RedisState
from app.resp.array import Array
from app.resp.base import RESPType
from app.command_processor.command import Command
from app.command_processor.command_type import CommandType
from app.command_processor.handlers.echo import handle_echo
from app.command_processor.handlers.error import handle_error
from app.command_processor.handlers.get import handle_get
from app.command_processor.handlers.ping import handle_ping
from app.command_processor.handlers.set import handle_set
from app.command_processor.handlers.rpush import handle_rpush
from app.command_processor.handlers.lrange import handle_lrange
from app.logging_config import get_logger

logger = get_logger(__name__)


async def processor(data_resp: Array, redis_state: RedisState) -> RESPType[Any]:
    """Process Redis commands and return appropriate responses."""
    command = Command(data_resp)

    # Direct mapping of command types to handlers
    handlers = {
        CommandType.PING: handle_ping,
        CommandType.ECHO: handle_echo,
        CommandType.GET: handle_get,
        CommandType.SET: handle_set,
        CommandType.RPUSH: handle_rpush,
        CommandType.LRANGE: handle_lrange,
    }

    handler = handlers.get(command.cmd_type, handle_error)
    return await handler(command.args, redis_state)
