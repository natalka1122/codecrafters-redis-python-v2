from app.exceptions import NoDataError


class SortedSet:
    def __init__(self) -> None:
        self._item_dict: dict[str, float] = {}
        self._item_list: list[str] = []

    def zadd(self, score: float, member: str) -> int:
        self._item_dict[member] = score
        result = 0
        if member not in self._item_list:
            result = 1
            self._item_list.append(member)
        self._item_list.sort(key=lambda x: self._item_dict[x])
        return result

    def zrank(self, member: str) -> int:
        try:
            return self._item_list.index(member)
        except ValueError:
            raise NoDataError
