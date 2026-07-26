"""
GTI AI
News Service
Version 1.0
"""


class NewsService:
    """
    Provides economic news events.
    """

    @staticmethod
    def events() -> list[dict]:
        """
        Returns economic calendar events.

        Version 1.0 uses sample data.
        This will later be replaced by a live economic calendar API.
        """
        return [
            {
                "title": "FOMC Interest Rate Decision",
                "currency": "USD",
                "impact": "HIGH",
            },
            {
                "title": "Non-Farm Payrolls",
                "currency": "USD",
                "impact": "HIGH",
            },
            {
                "title": "Consumer Price Index",
                "currency": "USD",
                "impact": "HIGH",
            },
            {
                "title": "Producer Price Index",
                "currency": "USD",
                "impact": "MEDIUM",
            },
        ]
