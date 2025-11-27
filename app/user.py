from typing import Optional


class User:
    def __init__(self, flags: Optional[set[str]] = None) -> None:
        self.flags: set[str] = flags if flags else set()
