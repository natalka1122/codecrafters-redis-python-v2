from typing import Optional

class List:
    def __init__(self) -> None:
        self._data: list[str] = []

    def rpush(self, values: list[str]) -> None:
        self._data = self._data + values

    def lpush(self, values: list[str]) -> None:
        self._data = list(reversed(values)) + self._data

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
