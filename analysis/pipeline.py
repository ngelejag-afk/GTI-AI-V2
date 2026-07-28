"""
GTI AI
Analysis Pipeline
Version 2.0
"""

from analysis.market_analyzer import MarketAnalyzer
from analysis.smc_analyzer import SMCAnalyzer
from ai.trading_engine import TradingEngine


class AnalysisPipeline:
    """
    Runs the complete GTI AI analysis pipeline.
    """

    @staticmethod
    def analyze(
        prices: list[float],
        candles: list | None = None,
        news_safe: bool = True,
    ) -> dict:
        """
        Analyze market data and generate a trading signal.
        """

        analysis = MarketAnalyzer.analyze(prices)

        smc = (
            SMCAnalyzer.analyze(candles)
            if candles
            else {
                "bos": False,
                "choch": False,
                "liquidity": False,
                "fvg": False,
                "order_block": False,
                "confirmed": False,
            }
        )

        signal = TradingEngine.generate_signal(
            trend=analysis["trend"],
            ema_aligned=analysis["ema_aligned"],
            smc=smc,
            multi_timeframe_confirmed=False,
            news_safe=news_safe,
        )

        return {
            "analysis": analysis,
            "smc": smc,
            "signal": signal,
        }
