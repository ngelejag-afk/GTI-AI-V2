"""
GTI AI
Confluence Engine
Version 1.0
"""


class ConfluenceEngine:
    """
    Combines analysis results into one confidence score.
    """

    def calculate(
        self,
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

        score = 0
        reasons = []

        if ema_aligned:
            score += 15
            reasons.append("EMA Alignment")

        if trend == "STRONG_BULLISH":
            score += 15
            reasons.append("Strong Bullish Trend")

        elif trend == "STRONG_BEARISH":
            score += 15
            reasons.append("Strong Bearish Trend")

        if bos:
            score += 15
            reasons.append("Break Of Structure")

        if choch:
            score += 10
            reasons.append("Change Of Character")

        if liquidity:
            score += 10
            reasons.append("Liquidity Sweep")

        if fvg:
            score += 10
            reasons.append("Fair Value Gap")

        if order_block:
            score += 10
            reasons.append("Order Block")

        if session_allowed:
            score += 10
            reasons.append("Trading Session")

        if news_allowed:
            score += 5
            reasons.append("No High Impact News")

        if score >= 80:
            decision = "BUY_OR_SELL"

        elif score >= 60:
            decision = "WATCH"

        else:
            decision = "NO_TRADE"

        return {
            "score": score,
            "decision": decision,
            "reasons": reasons,
        }
