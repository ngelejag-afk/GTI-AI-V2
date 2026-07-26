"""
Tests for ATR Engine.
"""

from indicators.atr_engine import ATREngine


class Candle:
    def __init__(self, high: float, low: float, close: float):
        self.high = high
        self.low = low
        self.close = close


def test_atr_returns_zero_when_not_enough_data():
    candles = [
        Candle(10, 8, 9),
        Candle(11, 9, 10),
    ]

    assert ATREngine.calculate(candles, period=14) == 0.0


def test_atr_calculates_expected_value():
    candles = [
        Candle(10, 8, 9),
        Candle(11, 9, 10),
        Candle(12, 10, 11),
        Candle(13, 11, 12),
    ]

    atr = ATREngine.calculate(candles, period=3)

    assert atr == 2.0
