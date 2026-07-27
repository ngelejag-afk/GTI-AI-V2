"""
GTI AI
Backtesting Engine
Version 1.0
"""

from analysis.pipeline import AnalysisPipeline
from strategy.stop_loss_engine import StopLossEngine
from strategy.take_profit_engine import TakeProfitEngine


class BacktestEngine:
    """
    Runs historical backtests.
    """

    def __init__(self):
        self.pipeline = AnalysisPipeline()

    def run(self, candles: list) -> list:
        """
        Run a simple backtest over historical candles.
        """

        results = []

        for index in range(50, len(candles)):
            history = candles[: index + 1]

            signal = self.pipeline.analyze(history)

            if signal.get("signal") not in ("BUY", "SELL"):
                continue

            entry = history[-1].close

            stop_loss = StopLossEngine.calculate(
                entry=entry,
                candles=history,
                trade_type=signal["signal"],
            )

            take_profit = TakeProfitEngine.calculate(
                entry=entry,
                candles=history,
                trade_type=signal["signal"],
            )

            results.append(
                {
                    "time": history[-1].time,
                    "signal": signal["signal"],
                    "entry": entry,
                    "stop_loss": stop_loss,
                    "take_profit": take_profit,
                }
            )

        return results
