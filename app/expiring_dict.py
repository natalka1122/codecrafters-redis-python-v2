import time
from typing import Optional

from app.exceptions import ItemNotFoundError


class ExpiringDict:
    def __init__(self) -> None:
        self._items: dict[str, str] = dict()
        self._expiration_ms: dict[str, int] = dict()

    def set(
        self,
        key: str,
        value: str,
        expire_set_ms: Optional[int] = None,
    ) -> None:
        if expire_set_ms is None:
            self._expiration_ms.pop(key, None)
            self._items[key] = value
        elif expire_set_ms > 0:
            self._expiration_ms[key] = expire_set_ms + int(time.time() * 1000)
            self._items[key] = value
        else:
            self._expiration_ms.pop(key, None)
            self._items.pop(key, None)

    def get(self, key: str) -> str:
        if key not in self._items:
            raise ItemNotFoundError

        if key not in self._expiration_ms:
            return self._items[key]

        now_ms = int(time.time() * 1000)
        if self._expiration_ms[key] <= now_ms:
            self._expiration_ms.pop(key, None)
            self._items.pop(key, None)
            raise ItemNotFoundError
        return self._items[key]
