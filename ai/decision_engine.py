"""
GTI AI
Decision Engine
Version 2.0
"""


class DecisionEngine:
    """
    Converts analysis results into a trading decision.
    """

    @staticmethod
    def decide(score: int, trend: str = "UNKNOWN") -> str:
        """
        Returns BUY, SELL or WAIT.
        """

        trend = trend.upper()

        if score >= 80 and trend == "BULLISH":
            return "BUY"

        if score >= 80 and trend == "BEARISH":
            return "SELL"

        return "WAIT"

    @staticmethod
    def summary(score: int, trend: str = "UNKNOWN") -> dict:
        """
        Returns a complete decision summary.
        """

        decision = DecisionEngine.decide(score, trend)

        if score >= 90:
            strength = "VERY_STRONG"
        elif score >= 75:
            strength = "STRONG"
        elif score >= 60:
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
