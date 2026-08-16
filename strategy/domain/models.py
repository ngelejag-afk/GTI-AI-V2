"""
GTI AI - Domain Layer
Core immutable data models.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Candle:
    """A single closed OHLC candle. Immutable by design."""

    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0
