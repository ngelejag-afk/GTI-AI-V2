"""
GTI AI
Trading Engine
Version 3.0
"""

from __future__ import annotations

from ai.confluence_engine import ConfluenceEngine
from ai.decision_engine import DecisionEngine


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
        Generate the final AI trading decision.
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

        score = confluence["score"]

        if multi_timeframe_confirmed:
            score = min(score + 10, 100)

        decision = DecisionEngine.summary(
            score=score,
            trend=trend,
        )

        return {
            "signal": decision["decision"],
            "trend": trend,
            "score": score,
            "confidence": score,
            "strength": decision["strength"],
            "trade_allowed": decision["trade_allowed"],
            "reasons": confluence["reasons"],
        }
