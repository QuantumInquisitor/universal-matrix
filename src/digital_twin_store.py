"""Thread-safe in-process digital twin state store.

The store keeps the latest snapshot per asset and an optional bounded history.
It is intentionally storage-backend neutral so production deployments can later
replace it with PostgreSQL, TimescaleDB, Redis Streams, or another customer
backend without changing the digital-twin contract.
"""

from __future__ import annotations

from collections import deque
from threading import RLock

from .digital_twin_contract import DigitalTwinSnapshot


class DigitalTwinStore:
    def __init__(self, history_limit: int = 256) -> None:
        if history_limit < 1:
            raise ValueError("history_limit must be positive")
        self.history_limit = history_limit
        self._lock = RLock()
        self._latest: dict[str, DigitalTwinSnapshot] = {}
        self._history: dict[str, deque[DigitalTwinSnapshot]] = {}

    def put(self, snapshot: DigitalTwinSnapshot) -> None:
        with self._lock:
            self._latest[snapshot.asset_id] = snapshot
            history = self._history.setdefault(
                snapshot.asset_id,
                deque(maxlen=self.history_limit),
            )
            history.append(snapshot)

    def latest(self, asset_id: str) -> DigitalTwinSnapshot | None:
        with self._lock:
            return self._latest.get(asset_id)

    def history(self, asset_id: str) -> tuple[DigitalTwinSnapshot, ...]:
        with self._lock:
            values = self._history.get(asset_id)
            if values is None:
                return ()
            return tuple(values)

    def assets(self) -> tuple[str, ...]:
        with self._lock:
            return tuple(sorted(self._latest))

    def clear(self, asset_id: str | None = None) -> None:
        with self._lock:
            if asset_id is None:
                self._latest.clear()
                self._history.clear()
                return
            self._latest.pop(asset_id, None)
            self._history.pop(asset_id, None)
