"""
GTI AI
Smart Money Concepts Engine
Version 1.0
"""


class SMCEngine:
    """
    Basic Smart Money Concepts analysis.
    """

    @staticmethod
    def analyze(
        bos: bool,
        choch: bool,
        liquidity: bool,
        fvg: bool,
        order_block: bool,
    ) -> dict:
        """
        Returns SMC score and confirmation.
        """
        score = 0
        reasons = []

        if bos:
            score += 20
            reasons.append("Break of Structure")

        if choch:
            score += 20
            reasons.append("Change of Character")

        if liquidity:
            score += 20
            reasons.append("Liquidity Sweep")

        if fvg:
            score += 20
            reasons.append("Fair Value Gap")

        if order_block:
            score += 20
            reasons.append("Order Block")

        return {
            "score": score,
            "confirmed": score >= 60,
            "reasons": reasons,
        }
