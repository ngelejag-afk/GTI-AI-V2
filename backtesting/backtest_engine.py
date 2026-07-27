"""
GTI AI
Backtesting Engine
Version 2.0
"""

from analysis.pipeline import AnalysisPipeline
from strategy.stop_loss_engine import StopLossEngine
from strategy.take_profit_engine import TakeProfitEngine
from backtesting.backtest_simulator import BacktestSimulator


class BacktestEngine:
    """
    Runs historical backtests with trade simulation.
    """

    def __init__(self):
        self.pipeline = AnalysisPipeline()

    def run(self, candles: list) -> list:
        """
        Run a backtest over historical candles.
        """

        results = []

        for index in range(50, len(candles) - 1):
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

            tp_price = take_profit["tp1"]

            status = BacktestSimulator.simulate(
                candles=candles,
                start_index=index + 1,
                signal=signal["signal"],
                entry=entry,
                stop_loss=stop_loss,
                take_profit=tp_price,
            )

            results.append(
                {
                    "time": history[-1].time,
                    "signal": signal["signal"],
                    "entry": entry,
                    "stop_loss": stop_loss,
                    "take_profit": tp_price,
                    "status": status,
                }
            )

        return results
