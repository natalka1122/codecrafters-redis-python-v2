import time
from typing import Optional

from app.exceptions import ItemNotFoundError, NotIntegerError


class ExpiringString:
    def __init__(self, data: str, expire_set_ms: Optional[int] = None) -> None:
        if expire_set_ms is None:
            self._expiration_ms = None
        elif expire_set_ms > 0:
            self._expiration_ms = expire_set_ms + int(time.time() * 1000)
        else:
            raise ItemNotFoundError
        self._data: str = data

    def get(self) -> str:
        if self._expiration_ms is None:
            return self._data

        now_ms = int(time.time() * 1000)
        if self._expiration_ms <= now_ms:
            raise ItemNotFoundError

        return self._data

    def incr(self) -> int:
        if self._expiration_ms is not None:
            now_ms = int(time.time() * 1000)
            if self._expiration_ms <= now_ms:
                self._data = "1"
                self._expiration_ms = None
                return 1
        if not self._data.isdigit():
            raise NotIntegerError
        result = int(self._data) + 1
        self._data = str(result)
        return result
