from typing import Any

from app.connection.connection import Connection
from app.redis_state import RedisState
from app.resp.array import Array
from app.resp.base import RESPType
from app.resp.bulk_string import BulkString, NullBulkString
from app.resp.error import Error
from app.resp.simple_string import SimpleString
from app.user import User


async def handle_acl_whoami(
    args: list[str], redis_state: RedisState, connection: Connection
) -> RESPType[Any]:
    """Handle ACL WHOAMI command."""
    if args:
        return Error(f"ACL WHOAMI command should not have arguments. args = {args}")
    return BulkString("default")


async def handle_acl_getuser(
    args: list[str], redis_state: RedisState, connection: Connection
) -> RESPType[Any]:
    """Handle ACL GETUSER command."""
    if len(args) != 1:
        return Error(f"ACL GETUSER command should have one argument. args = {args}")
    username = args[0]
    try:  # noqa: WPS229
        flags = [BulkString(x) for x in redis_state.users[username].flags]
        passwords = [BulkString(x) for x in redis_state.users[username].passwords]
    except KeyError:
        return NullBulkString("")
    return Array(  # noqa: WPS221
        [BulkString("flags"), Array(flags), BulkString("passwords"), Array(passwords)]
    )


async def handle_acl_setuser(
    args: list[str], redis_state: RedisState, connection: Connection
) -> RESPType[Any]:
    """Handle ACL SETUSER command."""
    if len(args) != 2:
        return Error(f"ACL SETUSER command should two arguments. args = {args}")
    username = args[0]
    if args[1][0] != ">":
        return Error("ACL SETUSER: NotImplementedError")
    password = args[1][1:]
    if username not in redis_state.users:
        redis_state.users[username] = User()
    redis_state.users[username].add_password(password)
    return SimpleString("OK")
