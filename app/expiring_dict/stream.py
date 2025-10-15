import re
import time
from collections import OrderedDict
from typing import Optional

from app.logging_config import get_logger

logger = get_logger(__name__)


class Stream:
    def __init__(self) -> None:
        self._dict: OrderedDict[int, OrderedDict[int, list[str]]] = OrderedDict()

    def xadd(self, key: str, parameters: list[str]) -> Optional[str]:
        if key == "*":
            timestamp = int(time.time() * 1000)
            counter_match = "*"
        else:
            key_match = re.match(r"(\d+)-(\d+|\*)", key)
            if key_match is None:
                return None
            timestamp = int(key_match.group(1))
            counter_match = key_match.group(2)
        if counter_match == "*":
            logger.error("NotImplementedError")
            raise NotImplementedError
        else:
            counter = int(counter_match)
        logger.info(f"timestamp = {timestamp} counter = {counter}")
        return key
