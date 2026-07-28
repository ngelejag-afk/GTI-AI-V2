"""
GTI AI
Signal History
Version 1.0
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


class SignalHistory:
    """
    Stores generated trading signals in memory.
    """

    def __init__(self, max_records: int = 100) -> None:
        self.max_records = max_records
        self._history: list[dict[str, Any]] = []

    def add(
        self,
        decision: str,
        confidence: int,
        session: str,
        reasons: list[str],
    ) -> None:
        """
        Save a trading signal.
        """

        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "decision": decision,
            "confidence": confidence,
            "session": session,
            "reasons": reasons,
        }

        self._history.append(record)

        if len(self._history) > self.max_records:
            self._history.pop(0)

    def latest(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Return the most recent signals.
        """

        return list(reversed(self._history[-limit:]))

    def all(self) -> list[dict[str, Any]]:
        """
        Return the complete history.
        """

        return list(self._history)

    def clear(self) -> None:
        """
        Remove all stored signals.
        """

        self._history.clear()

    def count(self) -> int:
        """
        Return the number of stored signals.
        """

        return len(self._history)
