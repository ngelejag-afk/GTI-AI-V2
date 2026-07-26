"""
GTI AI
Take Profit Engine
Version 1.0
"""


class TakeProfitEngine:
    """
    Calculates take profit levels using Risk:Reward ratios.
    """

    @staticmethod
    def calculate(
        decision: str,
        entry: float,
        stop_loss: float,
    ) -> dict:
        """
        Returns TP1, TP2 and TP3.
        """
        risk = abs(entry - stop_loss)

        if decision == "BUY":
            return {
                "tp1": round(entry + (risk * 1), 2),
                "tp2": round(entry + (risk * 2), 2),
                "tp3": round(entry + (risk * 3), 2),
            }

        if decision == "SELL":
            return {
                "tp1": round(entry - (risk * 1), 2),
                "tp2": round(entry - (risk * 2), 2),
                "tp3": round(entry - (risk * 3), 2),
            }

        return {
            "tp1": 0.0,
            "tp2": 0.0,
            "tp3": 0.0,
        }
