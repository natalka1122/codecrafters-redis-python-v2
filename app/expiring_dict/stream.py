import re
import time
from collections import OrderedDict
from typing import Optional

from app.logging_config import get_logger
from app.exceptions import StreamWrongIdError, StreamWrongOrderError

logger = get_logger(__name__)

Item = list[str]


class Sequenced(list[str]):
    def __init__(self, last_counter: int = 0) -> None:
        self._data: OrderedDict[int, Item] = OrderedDict()
        self.last_counter = last_counter

    def add_counter(self, counter: int, value: Item) -> None:
        if self._data and counter <= self.last_counter:
            raise StreamWrongOrderError
        self._data[counter] = value
        self.last_counter = counter


class Timestamped:
    def __init__(self) -> None:
        self._data: OrderedDict[int, Sequenced] = OrderedDict()
        self.last_timestamp = 0

    def add_timestamp(self, timestamp: int) -> None:
        if self._data and timestamp < self.last_timestamp:
            raise StreamWrongOrderError
        if timestamp not in self._data:
            self._data[timestamp] = Sequenced(1 if timestamp == 0 else 0)
            self.last_timestamp = timestamp

    def __getitem__(self, key: int) -> Sequenced:
        return self._data[key]


class Stream:
    def __init__(self) -> None:
        self._data: Timestamped = Timestamped()

    def xadd(self, key: str, parameters: list[str]) -> Optional[str]:
        if key == "0-0":
            raise StreamWrongIdError
        if key == "*":
            timestamp = int(time.time() * 1000)
            counter_match = "*"
        else:
            key_match = re.match(r"(\d+)-(\d+|\*)", key)
            if key_match is None:
                return None
            timestamp = int(key_match.group(1))
            counter_match = key_match.group(2)
        self._data.add_timestamp(timestamp)
        if counter_match == "*":
            logger.error("NotImplementedError")
            raise NotImplementedError
        else:
            counter = int(counter_match)

            self._data[timestamp].add_counter(counter, parameters)

        logger.info(f"timestamp = {timestamp} counter = {counter}")

        return key
