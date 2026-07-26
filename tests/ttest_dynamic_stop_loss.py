"""
Tests for Dynamic Stop Loss.
"""

from strategy.dynamic_stop_loss import DynamicStopLoss


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


def test_buy_stop_loss_is_below_entry():
    candles = create_candles()

    stop_loss = DynamicStopLoss.calculate(
        decision="BUY",
        entry=100.0,
        candles=candles,
        multiplier=2.0,
    )

    assert stop_loss == 96.0


def test_sell_stop_loss_is_above_entry():
    candles = create_candles()

    stop_loss = DynamicStopLoss.calculate(
        decision="SELL",
        entry=100.0,
        candles=candles,
        multiplier=2.0,
    )

    assert stop_loss == 104.0


def test_invalid_decision_returns_zero():
    candles = create_candles()

    stop_loss = DynamicStopLoss.calculate(
        decision="WAIT",
        entry=100.0,
        candles=candles,
    )

    assert stop_loss == 0.0
