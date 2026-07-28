
"""
GTI AI
Trading Engine
Version 2.0
"""

from ai.confluence_engine import ConfluenceEngine
from ai.confidence_engine import ConfidenceEngine
from ai.signal_engine import SignalEngine


class TradingEngine:
    """
    Coordinates AI trading decision generation.
    """

    @staticmethod
    def generate_signal(
        trend: str,
        ema_aligned: bool,
        smc: dict,
        multi_timeframe_confirmed: bool,
        news_safe: bool = True,
    ) -> dict:
        """
        Generate the final AI trading signal.
        """

        confluence = ConfluenceEngine.calculate(
            trend=trend,
            ema_aligned=ema_aligned,
            bos=smc.get("bos", False),
            choch=smc.get("choch", False),
            liquidity=smc.get("liquidity", False),
            fvg=smc.get("fvg", False),
            order_block=smc.get("order_block", False),
            session_allowed=True,
            news_allowed=news_safe,
        )

        confidence = ConfidenceEngine.calculate(
            {
                "trend": trend,
                "ema_alignment": ema_aligned,
                "smc_confirmed": smc.get("confirmed", False),
                "multi_timeframe_confirmed": multi_timeframe_confirmed,
                "news_safe": news_safe,
            }
        )

        return SignalEngine.generate(
            trend=trend,
            score=confluence["score"],
            confidence=confidence["confidence"],
            reasons=confluence["reasons"] + confidence["reasons"],
        )
