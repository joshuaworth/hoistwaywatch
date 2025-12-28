from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class _Entry:
    ts: float
    value: dict[str, Any]


class TTLState:
    """
    Tiny in-memory TTL store for cross-event correlation.
    Field devices are single-node; persistence is not required for MVP correlation rules.
    """

    def __init__(self) -> None:
        self._by_key: dict[str, _Entry] = {}

    def set(self, key: str, value: dict[str, Any], *, ts: float | None = None) -> None:
        self._by_key[key] = _Entry(ts=time.time() if ts is None else ts, value=value)

    def get_if_fresh(self, key: str, *, within_sec: float) -> dict[str, Any] | None:
        entry = self._by_key.get(key)
        if entry is None:
            return None
        if (time.time() - entry.ts) > within_sec:
            return None
        return entry.value

