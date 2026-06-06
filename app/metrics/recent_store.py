from __future__ import annotations

from collections import deque
from threading import Lock
from typing import Any


class RecentResolutionStore:
    def __init__(self, max_items: int = 50) -> None:
        self._lock = Lock()
        self._items = deque(maxlen=max_items)

    def append(self, item: dict[str, Any]) -> None:
        with self._lock:
            self._items.appendleft(item)

    def list(self, limit: int = 10) -> list[dict[str, Any]]:
        with self._lock:
            return list(self._items)[:limit]

    def reset(self) -> None:
        with self._lock:
            self._items.clear()


recent_resolution_store = RecentResolutionStore()