from __future__ import annotations
"""
GTI AI
Decision Engine
Version 3.0
"""



class DecisionEngine:
    """
    Converts analysis results into a final trading decision.
    """

    BUY_TRENDS = {
        "BULLISH",
        "STRONG_BULLISH",
    }

    SELL_TRENDS = {
        "BEARISH",
        "STRONG_BEARISH",
    }

    @staticmethod
    def decide(score: int, trend: str = "UNKNOWN") -> str:
        """
        Return BUY, SELL or WAIT.
        """

        trend = trend.upper()

        if score >= 80:
            if trend in DecisionEngine.BUY_TRENDS:
                return "BUY"

            if trend in DecisionEngine.SELL_TRENDS:
                return "SELL"

        return "WAIT"

    @staticmethod
    def summary(score: int, trend: str = "UNKNOWN") -> dict:
        """
        Return a complete decision summary.
        """

        trend = trend.upper()

        decision = DecisionEngine.decide(score, trend)

        if score >= 90:
            strength = "VERY_STRONG"
        elif score >= 80:
            strength = "STRONG"
        elif score >= 70:
            strength = "MODERATE"
        else:
            strength = "WEAK"

        return {
            "decision": decision,
            "score": score,
            "trend": trend,
            "strength": strength,
            "trade_allowed": decision != "WAIT",
        }
