from __future__ import annotations

"""
GTI AI
News Analyzer
Version 1.0
"""



class NewsAnalyzer:
    """
    Analyzes economic news risk for trading.
    """

    HIGH_IMPACT_EVENTS = {
        "NFP",
        "CPI",
        "CORE CPI",
        "PPI",
        "CORE PCE",
        "FOMC",
        "INTEREST RATE DECISION",
        "FED CHAIR SPEECH",
    }

    @staticmethod
    def analyze(
        events: list[dict] | None = None,
    ) -> dict:
        """
        Determine whether trading is safe based on
        upcoming high-impact economic events.
        """

        if not events:
            return {
                "safe": True,
                "risk": "LOW",
                "reason": "No scheduled high-impact events.",
            }

        for event in events:
            name = str(event.get("name", "")).upper()

            if name in NewsAnalyzer.HIGH_IMPACT_EVENTS:
                return {
                    "safe": False,
                    "risk": "HIGH",
                    "reason": f"High-impact event: {event.get('name')}",
                }

        return {
            "safe": True,
            "risk": "LOW",
            "reason": "No blocking economic events.",
        }
