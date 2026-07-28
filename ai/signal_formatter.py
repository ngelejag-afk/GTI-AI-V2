"""
GTI AI
Signal Formatter
Version 2.0
"""


class SignalFormatter:
    """
    Formats trading signals for display.
    """

    @staticmethod
    def format(signal: dict) -> str:
        """
        Return a formatted trading signal.
        """

        reasons = "\n".join(
            f"✔ {reason}" for reason in signal.get("reasons", [])
        )

        return f"""
==============================
GTI AI SIGNAL
==============================
Signal      : {signal.get("signal")}
Trend       : {signal.get("trend")}
Score       : {signal.get("score")}
Confidence  : {signal.get("confidence")}%
Strength    : {signal.get("strength")}

Reasons:
{reasons}

Trade Allowed : {signal.get("trade_allowed")}
==============================
""".strip()
