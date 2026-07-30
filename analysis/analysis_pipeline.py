"""
GTI AI
Analysis Pipeline
Version 4.0
"""

from __future__ import annotations

from analysis.dxy_analyzer import DXYAnalyzer
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
        dxy_prices: list[float] | None = None,
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

        dxy = (
            DXYAnalyzer.analyze(dxy_prices)
            if dxy_prices
            else {
                "signal": "NEUTRAL",
                "confirmed": False,
            }
        )

        signal = TradingEngine.generate_signal(
            trend=market["trend"],
            ema_aligned=market["ema_aligned"],
            smc=smc,
            multi_timeframe_confirmed=multi_timeframe["confirmed"],
            news_safe=news_safe,
            dxy_signal=dxy["signal"],
        )

        return {
            "market": market,
            "multi_timeframe": multi_timeframe,
            "smc": smc,
            "dxy": dxy,
            "signal": signal,
        }
