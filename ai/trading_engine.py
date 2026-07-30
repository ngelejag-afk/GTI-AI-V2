"""
GTI AI
Trading Engine
Version 4.0
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
        news_safe: bool =True,
        dxy_signal: str = "NEUTRAL",
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

        score = confluence["score"]

        if multi_timeframe_confirmed:
            score = min(score + 10, 100)

        trend = trend.upper()

        if dxy_signal == "USD_WEAKNESS":
            if trend in ("BULLISH", "STRONG_BULLISH"):
                score = min(score + 10, 100)
            elif trend in ("BEARISH", "STRONG_BEARISH"):
                score = max(score - 10, 0)

        elif dxy_signal == "USD_STRENGTH":
            if trend in ("BEARISH", "STRONG_BEARISH"):
                score = min(score + 10, 100)
            elif trend in ("BULLISH", "STRONG_BULLISH"):
                score = max(score - 10, 0)

        decision = DecisionEngine.summary(
            score=score,
            trend=trend,
        )

        reasons = list(confluence["reasons"])

        if dxy_signal == "USD_WEAKNESS":
            reasons.append("DXY confirms Gold bullish bias")

        elif dxy_signal == "USD_STRENGTH":
            reasons.append("DXY confirms Gold bearish bias")

        return {
            "signal": decision["decision"],
            "trend": trend,
            "score": score,
            "confidence": score,
            "strength": decision["strength"],
            "trade_allowed": decision["trade_allowed"],
            "dxy_signal": dxy_signal,
            "reasons": reasons,
        }
