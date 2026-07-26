"""
Tests for Dynamic Take Profit.
"""

from strategy.dynamic_take_profit import DynamicTakeProfit


class Candle:
    def __init__(self, high: float, low: float, close: float):
        self.high = high
        self.low = low
        self.close = close


def create_candles():
    return [
        Candle(10, 8, 9),
        Candle(11, 9, 10),
        Candle(12, 10, 11),
        Candle(13, 11, 12),
    ]


def test_buy_take_profit_levels():
    candles = create_candles()

    result = DynamicTakeProfit.calculate(
        decision="BUY",
        entry=100.0,
        candles=candles,
    )

    assert result["tp1"] == 104.0
    assert result["tp2"] == 106.0
    assert result["tp3"] == 108.0


def test_sell_take_profit_levels():
    candles = create_candles()

    result = DynamicTakeProfit.calculate(
        decision="SELL",
        entry=100.0,
        candles=candles,
    )

    assert result["tp1"] == 96.0
    assert result["tp2"] == 94.0
    assert result["tp3"] == 92.0


def test_invalid_decision_returns_zero_levels():
    candles = create_candles()

    result = DynamicTakeProfit.calculate(
        decision="WAIT",
        entry=100.0,
        candles=candles,
    )

    assert result == {
        "tp1": 0.0,
        "tp2": 0.0,
        "tp3": 0.0,
    }
