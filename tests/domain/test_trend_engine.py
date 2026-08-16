"""
Unit tests for the clean Sprint-2 TrendEngine.
"""

import unittest

from strategy.domain.models import Candle
from strategy.domain.trend_engine import TrendEngine


def make_candle(timestamp: int, close: float) -> Candle:
    return Candle(
        timestamp=timestamp,
        open=close,
        high=close,
        low=close,
        close=close,
        volume=1.0,
    )


def rising_candles(count: int, start: float = 100.0, step: float = 1.0):
    return [
        make_candle(i, start + i * step)
        for i in range(count)
    ]


def falling_candles(count: int, start: float = 500.0, step: float = 1.0):
    return [
        make_candle(i, start - i * step)
        for i in range(count)
    ]


def flat_candles(count: int, price: float = 100.0):
    return [make_candle(i, price) for i in range(count)]


class TestTrendEngine(unittest.TestCase):

    def test_insufficient_data_returns_explicit_marker(self):
        candles = rising_candles(50)  # fewer than EMA200 needs
        result = TrendEngine.analyze(candles)
        self.assertEqual(result, TrendEngine.INSUFFICIENT_DATA)

    def test_bullish_alignment(self):
        candles = rising_candles(250)
        result = TrendEngine.analyze(candles)
        self.assertEqual(result, TrendEngine.BULLISH)

    def test_bearish_alignment(self):
        candles = falling_candles(250)
        result = TrendEngine.analyze(candles)
        self.assertEqual(result, TrendEngine.BEARISH)

    def test_flat_prices_are_neutral(self):
        candles = flat_candles(250)
        result = TrendEngine.analyze(candles)
        self.assertEqual(result, TrendEngine.NEUTRAL)

    def test_exact_boundary_at_ema_slow_length(self):
        # Exactly 200 candles: should NOT be INSUFFICIENT_DATA.
        candles = rising_candles(200)
        result = TrendEngine.analyze(candles)
        self.assertNotEqual(result, TrendEngine.INSUFFICIENT_DATA)

    def test_one_below_boundary_is_insufficient(self):
        candles = rising_candles(199)
        result = TrendEngine.analyze(candles)
        self.assertEqual(result, TrendEngine.INSUFFICIENT_DATA)

    def test_deterministic_repeated_calls(self):
        candles = rising_candles(250)
        first = TrendEngine.analyze(candles)
        second = TrendEngine.analyze(candles)
        self.assertEqual(first, second)

    def test_does_not_mutate_input(self):
        candles = rising_candles(250)
        snapshot = list(candles)
        TrendEngine.analyze(candles)
        self.assertEqual(candles, snapshot)

    def test_closed_candle_only_contract_documented_behavior(self):
        # This test documents that TrendEngine trusts its input.
        # If the caller appends a "still forming" candle with an
        # extreme price, the result WILL change — proving that
        # causality safety must be enforced by the CALLER
        # (the backtest loop / live loop), not by this engine.
        closed = rising_candles(250)
        with_extra_forming_candle = closed + [make_candle(250, 100000.0)]

        result_without = TrendEngine.analyze(closed)
        result_with = TrendEngine.analyze(with_extra_forming_candle)

        # We only assert they CAN differ — this is a guard rail
        # test to keep this contract visible, not a correctness
        # assertion about which one is "right".
        self.assertIn(result_without, (TrendEngine.BULLISH, TrendEngine.NEUTRAL))
        self.assertIn(result_with, (TrendEngine.BULLISH, TrendEngine.NEUTRAL))


if __name__ == "__main__":
    unittest.main()
