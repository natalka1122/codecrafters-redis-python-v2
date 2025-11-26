from __future__ import annotations

import time
from abc import abstractmethod
from asyncio import AbstractEventLoop, TimerHandle
from typing import TYPE_CHECKING

from app.exceptions import ItemNotFoundError, NotIntegerError

if TYPE_CHECKING:
    from app.storage.storage import Storage  # Only imported for type checking


class BaseString:
    def __init__(self, data: str) -> None:
        self._data: str = data

    @abstractmethod
    def get(self) -> str: ...

    @abstractmethod
    def incr(self) -> int: ...


class EternalString(BaseString):
    def get(self) -> str:
        return self._data

    def incr(self) -> int:
        if not self._data.isdigit():
            raise NotIntegerError
        result = int(self._data) + 1
        self._data = str(result)
        return result


class ExpiringString(BaseString):
    def __init__(
        self,
        data: str,
        expire_set_ms: int,
        loop: AbstractEventLoop,
        storage: Storage,
        key: str,
    ) -> None:
        self._task: TimerHandle = loop.call_later(expire_set_ms, storage.delete, key)
        self._expiration_ms: int = expire_set_ms + int(time.time() * 1000)
        self._data: str = data

    def get(self) -> str:
        if self.is_expired:
            raise ItemNotFoundError
        return self._data

    def incr(self) -> int:
        if self.is_expired:
            raise ItemNotFoundError
        if not self._data.isdigit():
            raise NotIntegerError
        result = int(self._data) + 1
        self._data = str(result)
        return result

    def cancel_task(self) -> None:
        self._task.cancel()

    @property
    def is_expired(self) -> bool:
        now_ms = int(time.time() * 1000)
        return self._expiration_ms <= now_ms
