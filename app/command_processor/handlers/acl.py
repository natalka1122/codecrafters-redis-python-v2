from typing import Any

from app.connection.connection import Connection
from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.bulk_string import BulkString
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
    if args:
        return Error(f"ACL GETUSER command should not have arguments. args = {args}")
    return BulkString("ACL GETUSER: NotImplementedError")


async def handle_acl_setuser(
    args: list[str], redis_state: RedisState, connection: Connection
) -> RESPType[Any]:
    """Handle ACL SETUSER command."""
    if args:
        return Error(f"ACL SETUSER command should not have arguments. args = {args}")
    return BulkString("ACL SETUSER: NotImplementedError")
