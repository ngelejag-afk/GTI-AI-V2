"""
GTI AI
Trading Engine
Version 1.0
"""

from analysis.pipeline import AnalysisPipeline
from ai.signal_engine import SignalEngine


class TradingEngine:
    """
    Main AI trading engine.
    """

    def __init__(self):
        self.pipeline = AnalysisPipeline()

    def analyze(
        self,
        symbol: str,
        prices: list[float],
        entry: float,
        stop_loss: float,
        take_profit_1: float,
        take_profit_2: float,
    ) -> dict:

        result = self.pipeline.analyze(prices)

        signal = SignalEngine.generate(
            symbol=symbol,
            action=result["decision"]["decision"],
            entry=entry,
            stop_loss=stop_loss,
            take_profit_1=take_profit_1,
            take_profit_2=take_profit_2,
            confidence=result["decision"]["score"],
            reasons=result["decision"]["reasons"],
        )

        return signal
