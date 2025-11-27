from typing import Any

from app.command_processor.command import Command
from app.command_processor.command_type import CommandType
from app.command_processor.default_exec import default_exec
from app.command_processor.handlers.discard import (
    handle_discard,
)
from app.command_processor.handlers.error import handle_error_inside_subscription
from app.command_processor.handlers.exec import handle_exec
from app.command_processor.handlers.multi import (
    handle_multi_inside_transaction,
    handle_queued,
)
from app.command_processor.handlers.ping import handle_ping_inside_subscription
from app.command_processor.handlers.publish import handle_publish
from app.command_processor.handlers.subscribe import handle_subscribe
from app.command_processor.handlers.unsubscribe import handle_unsubscribe
from app.connection.connection import Connection
from app.logging_config import get_logger
from app.redis_state import RedisState
from app.resp.base import RESPType

logger = get_logger(__name__)


async def processor(
    data_resp: RESPType[Any], redis_state: RedisState, connection: Connection
) -> tuple[bool, bool, RESPType[Any]]:
    """Process Redis commands and return appropriate responses."""
    command = Command(data_resp)
    return (
        command.should_replicate,
        command.should_ack,
        await default_exec(command, redis_state, connection),
    )


async def transaction(
    data_resp: RESPType[Any], redis_state: RedisState, connection: Connection
) -> tuple[bool, bool, RESPType[Any]]:
    """Record transaction"""
    command = Command(data_resp)
    handlers = {
        CommandType.MULTI: handle_multi_inside_transaction,
        CommandType.EXEC: handle_exec,
        CommandType.DISCARD: handle_discard,
    }

    handler = handlers.get(command.cmd_type, handle_queued)
    return (
        command.should_replicate,
        command.should_ack,
        await handler(command, redis_state, connection),
    )


async def subscription(
    data_resp: RESPType[Any], redis_state: RedisState, connection: Connection
) -> tuple[bool, bool, RESPType[Any]]:
    """Subscribed mode"""
    command = Command(data_resp)
    handlers = {
        CommandType.SUBSCRIBE: handle_subscribe,
        CommandType.UNSUBSCRIBE: handle_unsubscribe,
        CommandType.PUBLISH: handle_publish,
        CommandType.PING: handle_ping_inside_subscription,
    }

    handler = handlers.get(command.cmd_type, handle_error_inside_subscription)
    return (
        command.should_replicate,
        command.should_ack,
        await handler(command.args, redis_state, connection),
    )
