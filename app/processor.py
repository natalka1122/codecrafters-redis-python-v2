from enum import Enum
from typing import Any

from app.exceptions import ItemNotFoundError, WrongRESPFormatError
from app.redis_state import RedisState
from app.resp.array import Array
from app.resp.base import RESPType
from app.resp.bulk_string import BulkString
from app.resp.error import Error
from app.resp.simple_string import SimpleString


class CommandType(Enum):
    PING = "PING"
    ECHO = "ECHO"
    GET = "GET"
    SET = "SET"
    ERROR = "ERROR"


def resp_to_command(data_resp: RESPType[Any]) -> list[str]:
    if not isinstance(data_resp, Array):
        raise WrongRESPFormatError(
            f"Unsupported data type: {type(data_resp)} data_resp = {data_resp}"
        )
    if len(data_resp) == 0:
        raise WrongRESPFormatError(
            f"len(data_resp) = {len(data_resp)} data_resp = {data_resp}"
        )
    command: list[str] = []
    for token in data_resp:
        if not isinstance(token, BulkString):
            raise WrongRESPFormatError(
                f"token = {type(token)} {token} data_resp = {data_resp}"
            )
        command.append(token.data)
    return command


async def processor(data_resp: Array, redis_state: RedisState) -> RESPType[Any]:
    """Process Redis commands and return appropriate responses."""
    try:
        command = resp_to_command(data_resp)
    except WrongRESPFormatError as e:
        command = ["ERROR", str(e)]
    command_name = command[0].upper()

    # Handle each command type
    if command_name == "PING":
        handler = handle_ping
    elif command_name == "ECHO":
        handler = handle_echo
    elif command_name == "GET":
        handler = handle_get
    elif command_name == "SET":
        handler = handle_set
    else:
        handler = handle_error
    return await handler(command[1:], redis_state)


async def handle_ping(args: list[str], redis_state: RedisState) -> RESPType[Any]:
    """Handle PING command."""
    if args:
        return Error("PING command should not have arguments")
    return SimpleString("PONG")


async def handle_echo(args: list[str], redis_state: RedisState) -> RESPType[Any]:
    """Handle ECHO command."""
    if len(args) != 1:
        return Error(f"ECHO command should have only one argument. args = {args}")
    return BulkString(args[0])


async def handle_get(args: list[str], redis_state: RedisState) -> RESPType[Any]:
    """Handle GET command."""
    if len(args) != 1:
        return Error(f"GET command should have only one argument. args = {args}")
    try:
        response = redis_state.redis_variables.get(args[0])
    except ItemNotFoundError:
        response = ""
    return BulkString(response)


async def handle_set(args: list[str], redis_state: RedisState) -> RESPType[Any]:
    """Handle SET command."""
    expire_set_ms: int | None = None
    if len(args) == 4:
        if args[2].lower() != "px":
            return Error(f"SET: args[2] = {args[2]} args = {args}")
        try:
            expire_set_ms = int(args[3])
        except ValueError:
            return Error(f"SET: args[3] = {args[3]} args = {args}")
    elif len(args) != 2:
        return Error(f"SET: len(args) = {len(args)} args = {args}")
    redis_state.redis_variables.set(args[0], args[1], expire_set_ms=expire_set_ms)
    return SimpleString("OK")


async def handle_error(args: list[str], redis_state: RedisState) -> RESPType[Any]:
    """Handle ECHO command."""
    return Error(f"{args}")
