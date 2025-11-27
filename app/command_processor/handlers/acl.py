from typing import Any

from app.connection.connection import Connection
from app.redis_state import RedisState
from app.resp.array import Array
from app.resp.base import RESPType
from app.resp.bulk_string import BulkString, NullBulkString
from app.resp.error import Error


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
    try:
        flags = [BulkString(x) for x in redis_state.users[username].flags]
    except KeyError:
        return NullBulkString("")
    return Array([BulkString("flags"), Array(flags)])


async def handle_acl_setuser(
    args: list[str], redis_state: RedisState, connection: Connection
) -> RESPType[Any]:
    """Handle ACL SETUSER command."""
    if args:
        return Error(f"ACL SETUSER command should not have arguments. args = {args}")
    return BulkString("ACL SETUSER: NotImplementedError")
