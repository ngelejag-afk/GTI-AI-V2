"""
GTI AI
Signal Engine
Version 2.0
"""

from ai.decision_engine import DecisionEngine


class SignalEngine:
    """
    Builds the final trading signal.
    """

    @staticmethod
    def generate(
        trend: str,
        score: int,
        confidence: int,
        reasons: list[str],
    ) -> dict:
        """
        Generate the final trading signal.
        """

        decision = DecisionEngine.summary(score, trend)

        return {
            "signal": decision["decision"],
            "trend": trend,
            "score": score,
            "confidence": confidence,
            "strength": decision["strength"],
            "trade_allowed": decision["trade_allowed"],
            "reasons": reasons,
        }
