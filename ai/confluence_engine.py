"""
GTI AI
Confidence Engine
Version 2.0
"""


class ConfidenceEngine:
    """
    Calculates signal confidence from analysis results.
    """

    @staticmethod
    def calculate(analysis: dict) -> dict:
        """
        Calculate confidence score and grade.
        """

        score = 0
        reasons = []

        trend = analysis.get("trend")

        if trend == "BULLISH":
            score += 20
            reasons.append("Bullish trend")

        elif trend == "BEARISH":
            score += 20
            reasons.append("Bearish trend")

        if analysis.get("ema_alignment", False):
            score += 20
            reasons.append("EMA alignment")

        if analysis.get("smc_confirmed", False):
            score += 30
            reasons.append("SMC confirmed")

        if analysis.get("multi_timeframe_confirmed", False):
            score += 20
            reasons.append("Multi-timeframe confirmation")

        if analysis.get("news_safe", True):
            score += 10
            reasons.append("News filter passed")

        score = min(score, 100)

        if score >= 90:
            grade = "A"
        elif score >= 75:
            grade = "B"
        elif score >= 60:
            grade = "C"
        else:
            grade = "D"

        return {
            "confidence": score,
            "grade": grade,
            "strong_signal": score >= 75,
            "reasons": reasons,
        }
