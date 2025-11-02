from collections import defaultdict
from typing import Optional

from app.exceptions import ItemNotFoundError
from app.resp.array import Array
from app.resp.bulk_string import BulkString
from app.storage.list import List
from app.storage.stream import Stream
from app.storage.string import ExpiringString


class Storage:  # noqa: WPS214
    def __init__(self) -> None:
        self._strings: dict[str, ExpiringString] = dict()
        self._lists: defaultdict[str, List] = defaultdict(List)
        self._streams: defaultdict[str, Stream] = defaultdict(Stream)

    def get_type(self, key: str) -> str:
        if key in self._strings:
            return "string"
        if key in self._lists:
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
        try:
            self._strings[key] = ExpiringString(value, expire_set_ms)
        except ItemNotFoundError:
            self._strings.pop(key, None)

    def get(self, key: str) -> str:
        if key not in self._strings:
            raise ItemNotFoundError

        try:
            return self._strings[key].get()
        except ItemNotFoundError:
            self._strings.pop(key, None)
            raise

    def incr(self, key: str) -> int:
        if key not in self._strings:
            self._strings[key] = ExpiringString("0")
        return self._strings[key].incr()

    def rpush(self, key: str, values: list[str]) -> int:
        result: int = self._lists[key].rpush(values)
        return result

    def lpush(self, key: str, values: list[str]) -> int:
        result: int = self._lists[key].lpush(values)
        return result

    def llen(self, key: str) -> int:
        return self._lists[key].llen()

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

    def lpop_one(self, key: str) -> Optional[str]:
        return self._lists[key].lpop_one()

    def lpop_many(self, key: str, count: int = 1) -> Optional[list[str]]:
        return self._lists[key].lpop_many(count)

    async def blpop(self, key: str, timeout: float) -> Optional[str]:
        return await self._lists[key].blpop_one(timeout)

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
