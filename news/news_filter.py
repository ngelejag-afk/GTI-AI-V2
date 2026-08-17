"""GTI-AI economic news filter."""

from news.news_service import NewsService


class NewsFilter:
    """Filter trading based on high-impact economic news."""

    @staticmethod
    def trading_allowed() -> bool:
        """Return False when a HIGH-impact event exists."""
        return not any(
            event.impact == "HIGH"
            for event in NewsService.events()
        )

    @staticmethod
    def high_impact_events():
        """Return all HIGH-impact economic events."""
        return [
            event
            for event in NewsService.events()
            if event.impact == "HIGH"
        ]
