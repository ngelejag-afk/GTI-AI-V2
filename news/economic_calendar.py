"""
GTI AI
Economic Calendar
Version 1.0
"""

from news.news_filter import NewsFilter


class EconomicCalendar:
    """
    Economic calendar interface.
    """

    @staticmethod
    def trading_allowed() -> bool:
        """
        Returns whether trading is currently allowed.
        """
        return NewsFilter.trading_allowed()

    @staticmethod
    def events() -> list[dict]:
        """
        Returns high-impact events.
        """
        return NewsFilter.high_impact_events()
