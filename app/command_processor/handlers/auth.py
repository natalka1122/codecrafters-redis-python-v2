from typing import Any

from app.connection.connection import Connection
from app.redis_state import RedisState
from app.resp.base import RESPType
from app.resp.error import Error
from app.resp.simple_string import SimpleString
from app.user import Flags, password_to_hash


async def handle_auth(
    args: list[str], redis_state: RedisState, connection: Connection
) -> RESPType[Any]:
    """Handle AUTH command."""
    if len(args) != 2:
        return Error(f"AUTH command should have two arguments. args = {args}")
    username = args[0]
    password_hashed = password_to_hash(args[1])
    user = redis_state.users.get(username)
    if user is not None:
        if Flags.NOPASS in user.flags or password_hashed in user.passwords:
            connection.is_authenticated = True
            return SimpleString("OK")
    return Error("WRONGPASS invalid username-password pair or user is disabled.")
