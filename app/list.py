from typing import Optional
import asyncio


class List:
    def __init__(self) -> None:
        self._data: list[str] = []
        self._condition: asyncio.Condition = asyncio.Condition()

    async def rpush(self, values: list[str]) -> int:
        self._data = self._data + values
        result = len(self._data)
        if len(self._data) > 0:
            async with self._condition:
                self._condition.notify(1)
        return result

    async def lpush(self, values: list[str]) -> int:
        self._data = list(reversed(values)) + self._data
        result = len(self._data)
        if len(self._data) > 0:
            async with self._condition:
                self._condition.notify(1)
        return result

    def llen(self) -> int:
        return len(self._data)

    def __len__(self) -> int:
        return len(self._data)

    def __getitem__(self, key: int | slice) -> str | list[str]:
        """Support indexing and slicing operations."""
        return self._data[key]

    def lpop_one(self) -> Optional[str]:
        if len(self._data) == 0:
            return None
        return self._data.pop(0)

    async def blpop(self, timeout: float) -> Optional[str]:
        async with self._condition:
            try:
                await asyncio.wait_for(
                    self._condition.wait_for(lambda: len(self._data) > 0),
                    timeout=timeout if timeout > 0 else None,
                )
            except asyncio.TimeoutError:
                return None

            result = self._data.pop(0)

        if len(self._data) > 0:
            self._condition.notify(1)
        return result
