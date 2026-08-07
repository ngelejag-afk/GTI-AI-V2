from __future__ import annotations
"""
GTI AI
Analysis Pipeline
Version 3.0
"""


from analysis.market_analyzer import MarketAnalyzer
from analysis.multi_timeframe_analyzer import MultiTimeframeAnalyzer
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
        timeframes: dict | None = None,
        news_safe: bool = True,
    ) -> dict:
        """
        Analyze market data and generate a trading signal.
        """

        market = MarketAnalyzer.analyze(prices)

        multi_timeframe = MultiTimeframeAnalyzer.analyze(
            timeframes or {}
        )

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
            trend=market["trend"],
            ema_aligned=market["ema_aligned"],
            smc=smc,
            multi_timeframe_confirmed=multi_timeframe["confirmed"],
            news_safe=news_safe,
        )

        return {
            "market": market,
            "multi_timeframe": multi_timeframe,
            "smc": smc,
            "signal": signal,
        }
