
"""
GTI AI
Confluence Analyzer
Version 1.0
"""


class ConfluenceAnalyzer:
    """
    Combines multi-timeframe analysis into one trading decision.
    """

    @staticmethod
    def analyze(timeframes: dict) -> dict:
        bullish = 0
        bearish = 0

        for analysis in timeframes.values():
            trend = analysis.get("trend")

            if trend in ("BULLISH", "STRONG_BULLISH"):
                bullish += 1

            elif trend in ("BEARISH", "STRONG_BEARISH"):
                bearish += 1

        if bullish >= 3:
            decision = "BUY"
            confidence = bullish * 25

        elif bearish >= 3:
            decision = "SELL"
            confidence = bearish * 25

        else:
            decision = "WAIT"
            confidence = 50

        return {
            "decision": decision,
            "confidence": confidence,
            "bullish_votes": bullish,
            "bearish_votes": bearish,
        }
