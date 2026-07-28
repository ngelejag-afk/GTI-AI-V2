"""
GTI AI
Take Profit Engine
Version 2.0
"""


class TakeProfitEngine:
    """
    Calculates Take Profit using
    configurable Risk/Reward ratios.
    """

    @staticmethod
    def calculate(
        entry: float,
        stop_loss: float,
        decision: str,
        risk_reward: float = 2.0,
    ) -> float:

        decision = decision.upper()

        risk = abs(entry - stop_loss)

        if decision == "BUY":
            return round(entry + (risk * risk_reward), 2)

        if decision == "SELL":
            return round(entry - (risk * risk_reward), 2)

        return round(entry, 2)
