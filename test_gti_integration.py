"""Integration tests for the validator-to-daemon signal boundary and state machine."""

from __future__ import annotations

import unittest
from pathlib import Path

from gti_v2_1_2_validator import (
    Candle,
    TradeRecord,
    apply_news_to_signal,
    get_m15_signal,
    prepare_market,
    run_strategy,
)
from gti_v2_unified_daemon import (
    SignalState,
    SignalStateMachine,
)
from validator_adapter import adapt_trade_to_signal


def build_candles() -> list[Candle]:
    """Build enough M5 data for M15 EMA50 and a deterministic crossover."""
    prices: list[float] = []

    for index in range(450):
        prices.append(2500.0 - index * 0.5)

    reversal_price = prices[-1]

    for index in range(450):
        prices.append(reversal_price + (index + 1) * 1.0)

    start = 1710000000

    return [
        Candle(
            timestamp=start + index * 300,
            open=price - 0.25,
            high=price + 1.5,
            low=price - 1.5,
            close=price,
            volume=100.0,
        )
        for index, price in enumerate(prices)
    ]


def find_validator_signal(market):
    """Return the first real M15 crossover produced by the validator."""
    for index in range(len(market.m15)):
        signal = get_m15_signal(market, index)
        if signal is not None:
            return apply_news_to_signal(signal, [])
    return None


class TestGTIEndToEndIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.candles = build_candles()
        self.market = prepare_market(self.candles)

        self.state_file = Path("test_gti_signal_state.json")
        if self.state_file.exists():
            self.state_file.unlink()

        self.state_machine = SignalStateMachine(filepath=self.state_file)

    def tearDown(self) -> None:
        if self.state_file.exists():
            self.state_file.unlink()

    """Verify full pipeline from validator TradeRecord to daemon state machine evaluation."""


    def test_fixture_has_enough_m15_history(self) -> None:
        self.assertGreaterEqual(
            len(self.market.m15),
            50,
            "Fixture must provide enough M15 candles for EMA50.",
        )

    def test_validator_produces_m15_crossover(self) -> None:
        signal = find_validator_signal(self.market)
        self.assertIsNotNone(
            signal,
            "Deterministic fixture did not produce an M15 EMA crossover.",
        )
        assert signal is not None
        self.assertIn(signal.direction, {"BUY", "SELL"})
        self.assertIsInstance(signal.timestamp, int)
        self.assertIsInstance(signal.score, int)

    def test_validator_produces_trade_record(self) -> None:
        start_timestamp = self.candles[0].timestamp
        end_timestamp = self.candles[-1].timestamp + 300

        trades = run_strategy(
            market=self.market,
            events=[],
            strategy="A_TECH_ONLY",
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
        )

        self.assertTrue(
            trades,
            "Validator produced no TradeRecord from the deterministic fixture.",
        )

        trade = trades[0]
        self.assertIsInstance(trade, TradeRecord)
        self.assertIn(trade.direction, {"BUY", "SELL"})
        self.assertGreater(trade.entry, 0.0)
        self.assertGreater(trade.stop_loss, 0.0)
        self.assertGreater(trade.take_profit, 0.0)
        self.assertIn(trade.result, {"WIN", "LOSS"})

    def test_daemon_state_machine_starts_in_wait(self) -> None:
        self.assertEqual(self.state_machine.state, SignalState.WAIT)

    def test_trade_record_drives_state_machine_evaluation(self) -> None:
        start_timestamp = self.candles[0].timestamp
        end_timestamp = self.candles[-1].timestamp + 300

        trades = run_strategy(
            market=self.market,
            events=[],
            strategy="A_TECH_ONLY",
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
        )

        self.assertTrue(trades, "Validator produced no TradeRecord for state machine testing.")

        trade = trades[0]
        strategy_signal = adapt_trade_to_signal(trade)

        _, should_alert, _ = self.state_machine.evaluate(strategy_signal)

        self.assertTrue(should_alert, "State machine should trigger an alert for a valid strategy signal.")
        self.assertEqual(self.state_machine.state, SignalState.ALERT_SENT)


class TestDirectionSerializationRegression(unittest.TestCase):
    """Regression tests for string-to-enum direction persistence."""

    def setUp(self) -> None:
        self.state_file = Path("test_regression_state.json")
        self.state_file.unlink(missing_ok=True)

    def tearDown(self) -> None:
        self.state_file.unlink(missing_ok=True)

    def test_string_direction_normalization_and_save(self) -> None:
        """Verify raw string directions normalize and survive persistence."""
        from gti_v2_unified_daemon import (
            Direction,
            Indicators,
            SignalStateMachine,
            StrategySignal,
        )

        machine = SignalStateMachine(filepath=self.state_file)

        indicators = Indicators(
            ema_fast=2050.0,
            ema_slow=2045.0,
            atr=5.0,
            rsi=55.0,
            volume_sma=100.0,
        )

        signal = StrategySignal(
            direction="buy",
            entry=2050.0,
            stop=2045.0,
            target=2065.0,
            risk_reward=3.0,
            score=80,
            valid=True,
            reason="Regression test string direction",
            candle_timestamp=1710000000,
            indicators=indicators,
        )

        _, should_alert, _ = machine.evaluate(signal)

        self.assertTrue(should_alert)
        self.assertIsInstance(machine.last_signal_direction, Direction)
        self.assertEqual(machine.last_signal_direction, Direction.BUY)

        reloaded_machine = SignalStateMachine(filepath=self.state_file)

        self.assertEqual(
            reloaded_machine.last_signal_direction,
            Direction.BUY,
        )




if __name__ == "__main__":
    unittest.main()
