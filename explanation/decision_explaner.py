
"""
GTI AI
Decision Explainer
Version 1.0
"""


class DecisionExplainer:
    """
    Generates human-readable reasons for a trading decision.
    """

    @staticmethod
    def explain(
        decision: str,
        confidence: int,
        trend: str = "UNKNOWN",
        session: str = "UNKNOWN",
        confirmed: bool = False,
    ) -> dict:
        """
        Build an explanation for the current trading signal.
        """

        reasons = []

        if trend == "BULLISH":
            reasons.append("Bullish trend confirmed")

        elif trend == "BEARISH":
            reasons.append("Bearish trend confirmed")

        if confirmed:
            reasons.append("Multi-timeframe confirmation")

        if session != "CLOSED":
            reasons.append(f"{session} session active")

        else:
            reasons.append("Trading session closed")

        if confidence >= 90:
            reasons.append("Very high confidence")

        elif confidence >= 75:
            reasons.append("High confidence")

        elif confidence >= 60:
            reasons.append("Moderate confidence")

        else:
            reasons.append("Low confidence")

        return {
            "decision": decision,
            "confidence": confidence,
            "reasons": reasons,
        }
