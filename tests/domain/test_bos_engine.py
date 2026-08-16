"""
Unit tests for BOSEngine (Sprint 2 clean rebuild).
"""

import unittest

from strategy.domain.models import Candle
from strategy.domain.swing_structure import SwingPoint
from strategy.domain.bos_engine import BOSEngine, BOSEvent


def candle(ts, o, h, l, c):
    return Candle(timestamp=ts, open=o, high=h, low=l, close=c, volume=1.0)


def swing_high(ts, price):
    return SwingPoint(timestamp=ts, price=price, type="HIGH")


def swing_low(ts, price):
    return SwingPoint(timestamp=ts, price=price, type="LOW")


class TestBOSEngine(unittest.TestCase):

    def test_insufficient_data_when_no_swings(self):
        candles = [candle(0, 1, 1, 1, 1)]
        result = BOSEngine.analyze(candles, [])
        self.assertEqual(result, BOSEngine.INSUFFICIENT_DATA)

    def test_simple_bullish_bos(self):
        swings = [swing_high(0, 100.0)]
        candles = [
            candle(0, 90, 100, 80, 90),
            candle(1, 90, 90, 90, 90),   # no break yet
            candle(2, 105, 110, 100, 105),  # close 105 > 100 -> BOS
        ]
        result = BOSEngine.analyze(candles, swings)
        self.assertEqual(len(result), 1)
        event = result[0]
        self.assertIsInstance(event, BOSEvent)
        self.assertEqual(event.direction, BOSEngine.BULLISH)
        self.assertEqual(event.timestamp, 2)
        self.assertEqual(event.broken_swing_price, 100.0)

    def test_simple_bearish_bos(self):
        swings = [swing_low(0, 50.0)]
        candles = [
            candle(0, 60, 65, 50, 60),
            candle(1, 60, 60, 60, 60),
            candle(2, 45, 55, 40, 45),  # close 45 < 50 -> BOS
        ]
        result = BOSEngine.analyze(candles, swings)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].direction, BOSEngine.BEARISH)
        self.assertEqual(result[0].timestamp, 2)

    def test_wick_only_does_not_trigger_bos(self):
        # High wick pierces 100 but CLOSE stays below -> no BOS.
        swings = [swing_high(0, 100.0)]
        candles = [
            candle(0, 90, 100, 80, 90),
            candle(1, 90, 90, 90, 90),
            candle(2, 95, 150, 90, 95),  # wick to 150, close 95
        ]
        result = BOSEngine.analyze(candles, swings)
        self.assertEqual(result, [])

    def test_equal_close_does_not_trigger_bos(self):
        swings = [swing_high(0, 100.0)]
        candles = [
            candle(0, 90, 100, 80, 90),
            candle(1, 90, 90, 90, 90),
            candle(2, 95, 100, 90, 100.0),  # close == 100 exactly
        ]
        result = BOSEngine.analyze(candles, swings)
        self.assertEqual(result, [])

    def test_swing_confirmed_on_same_candle_as_break_is_not_eligible(self):
        # Swing timestamp equals the break candle's own timestamp.
        swings = [swing_high(2, 100.0)]
        candles = [
            candle(0, 90, 95, 80, 90),
            candle(1, 90, 90, 90, 90),
            candle(2, 105, 110, 90, 105),  # same ts as swing -> not eligible
        ]
        result = BOSEngine.analyze(candles, swings)
        self.assertEqual(result, [])

    def test_consumed_high_requires_newer_high_for_next_bullish_bos(self):
        swings = [
            swing_high(0, 100.0),
            swing_high(3, 120.0),  # newer HIGH, confirmed later
        ]
        candles = [
            candle(0, 90, 100, 80, 90),
            candle(1, 90, 90, 90, 90),
            candle(2, 105, 110, 100, 105),  # breaks 100 -> BOS #1
            candle(3, 105, 105, 105, 105),
            candle(4, 106, 106, 106, 106),  # NOT > 120, no BOS
            candle(5, 125, 130, 106, 125),  # breaks 120 -> BOS #2
        ]
        result = BOSEngine.analyze(candles, swings)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].broken_swing_price, 100.0)
        self.assertEqual(result[1].broken_swing_price, 120.0)

    def test_bullish_bos_does_not_consume_low_side(self):
        swings = [
            swing_high(0, 100.0),
            swing_low(0, 50.0),
        ]
        candles = [
            candle(0, 90, 100, 50, 90),
            candle(1, 90, 90, 90, 90),
            candle(2, 105, 110, 100, 105),  # bullish BOS
            candle(3, 45, 60, 40, 45),      # bearish BOS still possible
        ]
        result = BOSEngine.analyze(candles, swings)
        directions = [e.direction for e in result]
        self.assertIn(BOSEngine.BULLISH, directions)
        self.assertIn(BOSEngine.BEARISH, directions)

    def test_does_not_mutate_inputs(self):
        swings = [swing_high(0, 100.0)]
        candles = [
            candle(0, 90, 100, 80, 90),
            candle(1, 90, 90, 90, 90),
            candle(2, 105, 110, 100, 105),
        ]
        candles_snapshot = list(candles)
        swings_snapshot = list(swings)

        BOSEngine.analyze(candles, swings)

        self.assertEqual(candles, candles_snapshot)
        self.assertEqual(swings, swings_snapshot)

    def test_deterministic_repeated_calls(self):
        swings = [swing_high(0, 100.0), swing_low(0, 50.0)]
        candles = [
            candle(0, 90, 100, 50, 90),
            candle(1, 90, 90, 90, 90),
            candle(2, 105, 110, 40, 105),
        ]
        first = BOSEngine.analyze(candles, swings)
        second = BOSEngine.analyze(candles, swings)
        self.assertEqual(first, second)

    def test_no_bos_when_price_never_breaks(self):
        swings = [swing_high(0, 100.0), swing_low(0, 50.0)]
        candles = [
            candle(0, 90, 100, 50, 90),
            candle(1, 90, 95, 55, 90),
            candle(2, 90, 95, 55, 90),
        ]
        result = BOSEngine.analyze(candles, swings)
        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
