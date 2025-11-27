import hashlib
from enum import StrEnum
from typing import Optional


class Flags(StrEnum):
    NOPASS = "nopass"


class User:
    def __init__(self, flags: Optional[set[str]] = None) -> None:
        self.flags: set[str] = flags if flags else set()
        self.passwords: set[str] = set()

    def add_password(self, password: str) -> None:
        self.passwords.add(hashlib.sha256(password.encode("utf-8")).hexdigest())
        self.flags.discard(Flags.NOPASS)
