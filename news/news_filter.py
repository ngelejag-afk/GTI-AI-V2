"""
GTI AI
News Filter
Version 1.0
"""

from news.news_service import NewsService


class NewsFilter:
    """
    Filters high-impact economic news.
    """

    @staticmethod
    def trading_allowed() -> bool:
        """
        Returns False if a HIGH impact event exists.
        """
        events = NewsService.events()

        for event in events:
            if event["impact"] == "HIGH":
                return False

        return True

    @staticmethod
    def high_impact_events() -> list[dict]:
        """
        Returns all HIGH impact events.
        """
        events = NewsService.events()

        return [
            event
            for event in events
            if event["impact"] == "HIGH"
        ]
