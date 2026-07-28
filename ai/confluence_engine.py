"""
GTI AI
Confidence Engine
Version 1.0
"""


class ConfidenceEngine:
    """
    Calculates confidence score from analysis results.
    """

    @staticmethod
    def calculate(analysis: dict) -> dict:
        """
        Calculate confidence percentage.
        """

        score = 0

        if analysis.get("trend") == "BULLISH":
            score += 20
        elif analysis.get("trend") == "BEARISH":
            score += 20

        if analysis.get("ema_alignment"):
            score += 20

        if analysis.get("smc_confirmed"):
            score += 30

        if analysis.get("multi_timeframe_confirmed"):
            score += 20

        if analysis.get("news_safe", True):
            score += 10

        score = min(score, 100)

        return {
            "confidence": score,
            "grade": (
                "A"
                if score >= 90
                else "B"
                if score >= 75
                else "C"
                if score >= 60
                else "D"
            ),
        }
