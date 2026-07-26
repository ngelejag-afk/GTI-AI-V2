"""
GTI AI
Decision Engine
Version 1.0
"""


class DecisionEngine:
    """
    Converts a confluence score into a trading decision.
    """

    @staticmethod
    def decide(score: int) -> str:
        """
        Returns BUY, SELL, or WAIT based on confidence score.
        """
        if score >= 80:
            return "BUY"

        if score <= 20:
            return "SELL"

        return "WAIT"
ai/decision_engine.py
