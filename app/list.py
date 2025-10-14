class List:
    def __init__(self) -> None:
        self._data: list[str] = []

    def rpush(self, values: list[str]) -> None:
        self._data = self._data + values

    def __len__(self) -> int:
        return len(self._data)
