from typing import Any

from app.command_processor.command import Command
from app.command_processor.command_type import CommandType
from app.command_processor.handlers.blpop import handle_blpop
from app.command_processor.handlers.discard import (
    handle_discard,
    handle_discard_no_multy,
)
from app.command_processor.handlers.echo import handle_echo
from app.command_processor.handlers.error import handle_error
from app.command_processor.handlers.exec import handle_exec, handle_exec_no_multi
from app.command_processor.handlers.get import handle_get
from app.command_processor.handlers.incr import handle_incr
from app.command_processor.handlers.llen import handle_llen
from app.command_processor.handlers.lpop import handle_lpop
from app.command_processor.handlers.lpush import handle_lpush
from app.command_processor.handlers.lrange import handle_lrange
from app.command_processor.handlers.multi import (
    handle_multi,
    handle_multi_inside_transaction,
    handle_queued,
)
from app.command_processor.handlers.ping import handle_ping
from app.command_processor.handlers.rpush import handle_rpush
from app.command_processor.handlers.set import handle_set
from app.command_processor.handlers.type import handle_type
from app.command_processor.handlers.xadd import handle_xadd
from app.command_processor.handlers.xrange import handle_xrange
from app.command_processor.handlers.xread_block import handle_xread_block
from app.command_processor.handlers.xread_streams import handle_xread_streams
from app.connection.connection import Connection
from app.logging_config import get_logger
from app.redis_state import RedisState
from app.resp.array import Array
from app.resp.base import RESPType

logger = get_logger(__name__)


async def processor(
    data_resp: Array, redis_state: RedisState, connection: Connection
) -> tuple[bool, RESPType[Any]]:
    """Process Redis commands and return appropriate responses."""
    command = Command(data_resp)
    # TODO: Rewrite later, maybe all normal handlers need connection too
    # But for now I just patch it
    if command.cmd_type == CommandType.MULTI:
        result = await handle_multi(command.args, redis_state, connection)
        return True, result

    # Direct mapping of command types to handlers
    handlers = {
        CommandType.PING: handle_ping,
        CommandType.ECHO: handle_echo,
        CommandType.GET: handle_get,
        CommandType.SET: handle_set,
        CommandType.RPUSH: handle_rpush,
        CommandType.LPUSH: handle_lpush,
        CommandType.LRANGE: handle_lrange,
        CommandType.LLEN: handle_llen,
        CommandType.LPOP: handle_lpop,
        CommandType.BLPOP: handle_blpop,
        CommandType.TYPE: handle_type,
        CommandType.XADD: handle_xadd,
        CommandType.XRANGE: handle_xrange,
        CommandType.XREAD_BLOCK: handle_xread_block,
        CommandType.XREAD_STREAMS: handle_xread_streams,
        CommandType.INCR: handle_incr,
        CommandType.EXEC: handle_exec_no_multi,
        CommandType.DISCARD: handle_discard_no_multy,
    }

    handler = handlers.get(command.cmd_type, handle_error)
    result = await handler(command.args, redis_state)
    return False, result


async def transaction(
    data_resp: Array, redis_state: RedisState, connection: Connection
) -> tuple[bool, RESPType[Any]]:
    """Record transaction"""
    command = Command(data_resp)
    # Direct mapping of command types to handlers
    handlers = {
        CommandType.MULTI: handle_multi_inside_transaction,
        CommandType.EXEC: handle_exec,
        CommandType.DISCARD: handle_discard,
    }

    handler = handlers.get(command.cmd_type, handle_queued)
    result = await handler(command.args, redis_state, connection)
    return result
