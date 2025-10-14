import time
from typing import Optional
from app.list import List
from app.exceptions import ItemNotFoundError


class ExpiringDict:
    def __init__(self) -> None:
        self._items: dict[str, str] = dict()
        self._expiration_ms: dict[str, int] = dict()
        self._lists: dict[str, List] = dict()

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

    def rpush(self, key: str, values: list[str]) -> int:
        if key not in self._lists:
            self._lists[key] = List()
        self._lists[key].rpush(values)
        return len(self._lists[key])

    def lrange(self, key: str, start_index: int, stop_index: int) -> list[str]:
        if key not in self._lists:
            return []
        the_list: List = self._lists[key]
        len_the_list = len(the_list)
        if start_index > len_the_list:
            return []
        if start_index < 0:
            start_index = max(0, len_the_list + start_index)

        if stop_index > len_the_list:
            stop_index = len_the_list - 1
        elif stop_index < 0:
            stop_index = max(0, len_the_list + stop_index)
        if start_index > stop_index:
            return []

        result = the_list[start_index : stop_index + 1]
        if isinstance(result, str):  # to pass type checks
            return [result]
        return result
