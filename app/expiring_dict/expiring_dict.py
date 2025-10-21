import time
from collections import defaultdict
from typing import Optional

from app.exceptions import ItemNotFoundError, NotIntegerError
from app.expiring_dict.list import List
from app.expiring_dict.stream import Stream
from app.resp.array import Array
from app.resp.bulk_string import BulkString


class ExpiringDict:  # noqa: WPS214
    def __init__(self) -> None:
        self._items: dict[str, str] = dict()
        self._expiration_ms: dict[str, int] = dict()
        self._lists: defaultdict[str, List] = defaultdict(List)
        self._streams: defaultdict[str, Stream] = defaultdict(Stream)

    def get_type(self, key: str) -> str:
        item = self._items.get(key)
        if item is not None:
            return "string"
        if self._lists.get(key):
            return "list"
        if key in self._streams:
            return "stream"
        return "none"

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

    async def rpush(self, key: str, values: list[str]) -> int:
        return await self._lists[key].rpush(values)

    async def lpush(self, key: str, values: list[str]) -> int:
        return await self._lists[key].lpush(values)

    def llen(self, key: str) -> int:
        return len(self._lists[key])

    def lrange(self, key: str, start_index: int, stop_index: int) -> list[str]:
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

    async def lpop_one(self, key: str) -> Optional[str]:
        return await self._lists[key].lpop_one()

    async def lpop_many(self, key: str, count: int = 1) -> Optional[list[str]]:
        return await self._lists[key].lpop_many(count)

    async def blpop(self, key: str, timeout: float) -> Optional[str]:
        return await self._lists[key].blpop(timeout)

    async def xadd(self, stream_name: str, key: str, parameters: list[str]) -> Optional[str]:
        return await self._streams[stream_name].xadd(key, parameters)

    def xrange(self, stream_name: str, start_id: str, end_id: str) -> Array:
        return self._streams[stream_name].xrange(start_id, end_id)

    def xread_one_stream(self, stream_name: str, start_id: str) -> Array:
        return Array(
            [
                BulkString(stream_name),
                self._streams[stream_name].xread_one_stream(start_id),
            ]
        )

    async def xread_block(self, timeout: int, stream_name: str, start_id_str: str) -> Array:
        result = await self._streams[stream_name].xread_block(timeout, start_id_str)
        return Array([BulkString(stream_name), result])

    def incr(self, key: str) -> int:
        value = self._items.get(key)
        if value is None:
            result = 1
        elif value.isdigit():
            result = int(value) + 1
        else:
            raise NotIntegerError

        self._items[key] = str(result)
        return result
