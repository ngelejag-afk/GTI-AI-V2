"""
GTI AI
Confluence Analyzer
Version 2.0
"""


class ConfluenceAnalyzer:
    """
    Combines multi-timeframe analysis into a single trading decision.
    """

    @staticmethod
    def analyze(timeframes: dict) -> dict:
        """
        Analyze overall market confluence.
        """

        if not timeframes:
            return {
                "decision": "WAIT",
                "confidence": 0,
                "confirmed": False,
                "bullish_votes": 0,
                "bearish_votes": 0,
                "reason": ["No timeframe analysis available"],
            }

        bullish = 0
        bearish = 0

        for analysis in timeframes.values():
            trend = analysis.get("market_bias", analysis.get("trend"))

            if trend in ("BULLISH", "STRONG_BULLISH"):
                bullish += 1

            elif trend in ("BEARISH", "STRONG_BEARISH"):
                bearish += 1

        if bullish > bearish:
            decision = "BUY"
            confidence = min(bullish * 25, 100)
            confirmed = bullish >= 3
            reason = [
                f"{bullish} bullish timeframe(s)",
                "Bullish confluence confirmed" if confirmed else "Bullish bias detected",
            ]

        elif bearish > bullish:
            decision = "SELL"
            confidence = min(bearish * 25, 100)
            confirmed = bearish >= 3
            reason = [
                f"{bearish} bearish timeframe(s)",
                "Bearish confluence confirmed" if confirmed else "Bearish bias detected",
            ]

        else:
            decision = "WAIT"
            confidence = 50
            confirmed = False
            reason = ["Mixed market conditions"]

        return {
            "decision": decision,
            "confidence": confidence,
            "confirmed": confirmed,
            "bullish_votes": bullish,
            "bearish_votes": bearish,
            "reason": reason,
        }
