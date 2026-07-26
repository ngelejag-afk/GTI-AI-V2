"""
GTI AI
Signal Engine
Version 1.0
"""


class SignalEngine:
    """
    Builds a trading signal from the AI analysis.
    """

    @staticmethod
    def generate(
        symbol: str,
        action: str,
        entry: float,
        stop_loss: float,
        take_profit_1: float,
        take_profit_2: float,
        confidence: int,
        reasons: list[str],
    ) -> dict:

        risk = abs(entry - stop_loss)
        reward = abs(take_profit_1 - entry)

        rr = round(reward / risk, 2) if risk else 0.0

        return {
            "symbol": symbol,
            "action": action,
            "entry": entry,
            "stop_loss": stop_loss,
            "take_profit_1": take_profit_1,
            "take_profit_2": take_profit_2,
            "confidence": confidence,
            "risk_reward": rr,
            "reasons": reasons,
        }
