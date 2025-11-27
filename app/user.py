import hashlib
from enum import StrEnum
from typing import Optional


class Flags(StrEnum):
    NOPASS = "nopass"


def password_to_hash(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class User:
    def __init__(self, flags: Optional[set[str]] = None) -> None:
        self.flags: set[str] = flags if flags else set()
        self.passwords: set[str] = set()

    def add_password(self, password: str) -> None:
        self.passwords.add(password_to_hash(password))
        self.flags.discard(Flags.NOPASS)
