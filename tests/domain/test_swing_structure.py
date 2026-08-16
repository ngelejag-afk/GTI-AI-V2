"""
Unit tests for SwingStructureEngine (Sprint 2 clean rebuild).
"""

import unittest

from strategy.domain.models import Candle
from strategy.domain.swing_structure import (
    SwingStructureEngine,
    SwingPoint,
)


def candle(ts, o, h, l, c):
    return Candle(timestamp=ts, open=o, high=h, low=l, close=c, volume=1.0)


class TestSwingStructureEngine(unittest.TestCase):

    def test_insufficient_data_below_window(self):
        candles = [candle(i, 1, 1, 1, 1) for i in range(4)]
        result = SwingStructureEngine.analyze(candles)
        self.assertEqual(result, SwingStructureEngine.INSUFFICIENT_DATA)

    def test_exact_window_size_is_not_insufficient(self):
        candles = [candle(i, 1, 1, 1, 1) for i in range(5)]
        result = SwingStructureEngine.analyze(candles)
        self.assertNotEqual(result, SwingStructureEngine.INSUFFICIENT_DATA)

    def test_detects_simple_swing_high(self):
        # index:  0    1    2    3    4
        # high:   1    2    5    2    1
        highs = [1, 2, 5, 2, 1]
        candles = [
            candle(i, h, h, h - 0.5, h) for i, h in enumerate(highs)
        ]
        result = SwingStructureEngine.analyze(candles)
        self.assertIsInstance(result, list)
        types = [(p.timestamp, p.type) for p in result]
        self.assertIn((2, "HIGH"), types)

    def test_detects_simple_swing_low(self):
        lows = [5, 4, 1, 4, 5]
        candles = [
            candle(i, l, l + 0.5, l, l) for i, l in enumerate(lows)
        ]
        result = SwingStructureEngine.analyze(candles)
        types = [(p.timestamp, p.type) for p in result]
        self.assertIn((2, "LOW"), types)

    def test_equal_highs_do_not_count_as_swing(self):
        # Plateau: 1, 5, 5, 5, 1 — no strictly-greater candidate.
        highs = [1, 5, 5, 5, 1]
        candles = [
            candle(i, h, h, h - 0.5, h) for i, h in enumerate(highs)
        ]
        result = SwingStructureEngine.analyze(candles)
        high_points = [p for p in result if p.type == "HIGH"]
        self.assertEqual(high_points, [])

    def test_last_two_candles_can_never_be_confirmed_swing(self):
        # Even if the last candle has an extreme high, it cannot
        # be returned as a swing because there is no right-side
        # confirmation data — this is the causality guarantee.
        highs = [1, 2, 3, 4, 1000]
        candles = [
            candle(i, h, h, h - 0.5, h) for i, h in enumerate(highs)
        ]
        result = SwingStructureEngine.analyze(candles)
        timestamps_flagged = [p.timestamp for p in result]
        self.assertNotIn(4, timestamps_flagged)
        self.assertNotIn(3, timestamps_flagged)

    def test_no_swings_in_monotonic_series(self):
        # Strictly increasing highs: no candle has BOTH left and
        # right neighbors lower (right side is always higher).
        highs = [1, 2, 3, 4, 5, 6, 7]
        candles = [
            candle(i, h, h, h - 0.5, h) for i, h in enumerate(highs)
        ]
        result = SwingStructureEngine.analyze(candles)
        self.assertEqual(result, [])

    def test_does_not_mutate_input(self):
        highs = [1, 2, 5, 2, 1]
        candles = [
            candle(i, h, h, h - 0.5, h) for i, h in enumerate(highs)
        ]
        snapshot = list(candles)
        SwingStructureEngine.analyze(candles)
        self.assertEqual(candles, snapshot)

    def test_deterministic_repeated_calls(self):
        highs = [1, 2, 5, 2, 1, 2, 6, 2, 1]
        candles = [
            candle(i, h, h, h - 0.5, h) for i, h in enumerate(highs)
        ]
        first = SwingStructureEngine.analyze(candles)
        second = SwingStructureEngine.analyze(candles)
        self.assertEqual(first, second)

    def test_returns_swingpoint_dataclass_instances(self):
        highs = [1, 2, 5, 2, 1]
        candles = [
            candle(i, h, h, h - 0.5, h) for i, h in enumerate(highs)
        ]
        result = SwingStructureEngine.analyze(candles)
        for point in result:
            self.assertIsInstance(point, SwingPoint)


if __name__ == "__main__":
    unittest.main()
