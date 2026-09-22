from app.models.change import ChangeRecord


class ChangeRegistry:
    """
    V1 in-memory registry for recorded ChangeRecords.

    This is intentionally temporary. Persistent storage will be
    introduced when the real storage/integration phase is reached.
    """

    def __init__(self) -> None:
        self._changes: dict[str, ChangeRecord] = {}

    def save(self, change: ChangeRecord) -> ChangeRecord:
        self._changes[change.change_id] = change
        return change

    def get(self, change_id: str) -> ChangeRecord | None:
        return self._changes.get(change_id)

    def exists(self, change_id: str) -> bool:
        return change_id in self._changes

    def clear(self) -> None:
        self._changes.clear()