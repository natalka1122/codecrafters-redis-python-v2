import asyncio
import bisect
import re
import time
from collections import OrderedDict
from typing import Optional

from app.exceptions import NoDataError, StreamWrongIdError, StreamWrongOrderError
from app.logging_config import get_logger
from app.resp.array import Array
from app.resp.bulk_string import BulkString

logger = get_logger(__name__)


Item = Array


def str_to_tuple(data: str) -> tuple[int, Optional[int]]:
    if data == "*":
        timestamp = int(time.time() * 1000)
        counter = None
    elif data.isdigit():
        timestamp = int(data)
        counter = None
    else:
        data_match = re.fullmatch(r"(\d+)-(\d+|\*)", data)
        if data_match is None:
            raise NotImplementedError
        timestamp = int(data_match.group(1))
        counter_group = data_match.group(2)
        counter = int(counter_group) if counter_group.isdigit() else None
    return timestamp, counter


class Key:
    def __init__(self, timestamp: int, counter: int) -> None:
        self._data = f"{timestamp}-{counter}"
        self._timestamp = timestamp
        self._counter = counter
        self._tuple = (self._timestamp, self._counter)

    def __hash__(self) -> int:
        return hash(self._data)

    def __repr__(self) -> str:
        return self._data

    @property
    def timestamp(self) -> int:
        return self._timestamp

    @property
    def counter(self) -> int:
        return self._counter

    @property
    def tuple(self) -> tuple[int, int]:
        return self._tuple

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Key):
            raise NotImplementedError
        return self.tuple < other.tuple

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Key):
            raise NotImplementedError
        return self.tuple <= other.tuple

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Key):
            raise NotImplementedError
        return self.tuple > other.tuple


class Stamped:
    def __init__(self) -> None:
        self._data: OrderedDict[Key, Item] = OrderedDict()
        self.next_stamp = Key(0, 1)

    @property
    def stamps(self) -> list[Key]:
        return list(self._data.keys())

    @property
    def last_key(self) -> Key:
        if len(self._data) == 0:
            return Key(0, 0)
        return list(self._data.keys())[-1]

    def __getitem__(self, key: Key) -> Item:
        return self._data[key]

    def __setitem__(self, key: Key, value: Item) -> None:
        if key < self.next_stamp:
            raise NotImplementedError
        self._data[key] = value
        self.next_stamp = Key(key.timestamp, key.counter + 1)

    def __len__(self) -> int:
        return len(self._data)


class Stream:
    def __init__(self) -> None:
        self._data: Stamped = Stamped()
        self._condition: asyncio.Condition = asyncio.Condition()

    async def xadd(self, key_str: str, parameters: list[str]) -> Optional[str]:
        if key_str == "0-0":
            raise StreamWrongIdError
        timestamp, counter = str_to_tuple(key_str)
        if timestamp < self._data.next_stamp.timestamp:
            raise StreamWrongOrderError
        if timestamp == self._data.next_stamp.timestamp:
            counter_int = self._data.next_stamp.counter if counter is None else counter
            if counter_int < self._data.next_stamp.counter:
                raise StreamWrongOrderError
        else:
            counter_int = 0 if counter is None else counter
        self._data[Key(timestamp, counter_int)] = Array(
            list(map(BulkString, parameters))
        )
        async with self._condition:
            self._condition.notify_all()
        return f"{timestamp}-{counter_int}"

    def xrange(self, start_id_str: str, end_id_str: str) -> Array:
        stamps_list = self._data.stamps
        if start_id_str == "-":
            start_id = Key(0, 1)
        else:
            start_ts, start_counter = str_to_tuple(start_id_str)
            start_id = Key(start_ts, 0 if start_counter is None else start_counter)
        start_index = bisect.bisect_left(stamps_list, start_id)
        if start_index >= len(stamps_list):
            return Array([])

        if end_id_str == "+":
            end_index = len(stamps_list)
        else:
            end_ts, end_counter = str_to_tuple(end_id_str)
            if end_counter is None:
                end_index = bisect.bisect_left(stamps_list, Key(end_ts + 1, 0))
            else:
                end_index = bisect.bisect_left(
                    stamps_list, Key(end_ts, end_counter + 1)
                )
        result: list[Array] = []
        for key in stamps_list[start_index:end_index]:
            current_item: Array = Array([BulkString(str(key)), self._data[key]])
            result.append(current_item)
        return Array(result)

    def xread_one_stream(self, start_id_str: str) -> Array:
        start_ts, start_counter = str_to_tuple(start_id_str)
        if start_counter is None:
            return Array([])
        start_id = Key(start_ts, start_counter)
        stamps_list = self._data.stamps
        start_index = bisect.bisect_right(stamps_list, start_id)
        result: list[Array] = []
        for key in stamps_list[start_index:]:
            current_item: Array = Array([BulkString(str(key)), self._data[key]])
            result.append(current_item)
        return Array(result)

    async def xread_block(self, timeout: int, start_id_str: str) -> Array:
        start_ts, start_counter = str_to_tuple(start_id_str)
        if start_counter is None:
            raise NotImplementedError
        start_id = Key(start_ts, start_counter)

        if len(self._data) == 0 or start_id >= self._data.last_key:
            async with self._condition:
                try:
                    await asyncio.wait_for(
                        self._condition.wait_for(
                            lambda: start_id < self._data.last_key
                        ),
                        timeout=timeout / 1000 if timeout > 0 else None,
                    )
                except asyncio.TimeoutError:
                    raise NoDataError

        stamps_list = self._data.stamps
        start_index = bisect.bisect_right(stamps_list, start_id)
        current_item: Array = Array(
            [
                BulkString(str(stamps_list[start_index])),
                self._data[stamps_list[start_index]],
            ]
        )
        return Array([current_item])
