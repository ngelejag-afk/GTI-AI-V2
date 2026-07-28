"""
GTI AI
Confluence Engine
Version 2.0
"""


class ConfluenceEngine:
    """
    Calculates a confluence score from market conditions.
    """

    @staticmethod
    def calculate(
        trend: str,
        ema_aligned: bool,
        bos: bool,
        choch: bool,
        liquidity: bool,
        fvg: bool,
        order_block: bool,
        session_allowed: bool,
        news_allowed: bool,
    ) -> dict:
        """
        Calculate overall market confluence.
        """

        score = 0
        reasons = []

        if trend == "BULLISH":
            score += 20
            reasons.append("Bullish trend")

        elif trend == "BEARISH":
            score += 20
            reasons.append("Bearish trend")

        if ema_aligned:
            score += 15
            reasons.append("EMA aligned")

        if bos:
            score += 15
            reasons.append("Break of Structure")

        if choch:
            score += 10
            reasons.append("Change of Character")

        if liquidity:
            score += 10
            reasons.append("Liquidity sweep")

        if fvg:
            score += 10
            reasons.append("Fair Value Gap")

        if order_block:
            score += 10
            reasons.append("Order Block")

        if session_allowed:
            score += 5
            reasons.append("Trading session allowed")

        if news_allowed:
            score += 5
            reasons.append("News filter passed")

        score = min(score, 100)

        return {
            "score": score,
            "confirmed": score >= 70,
            "reasons": reasons,
        }
