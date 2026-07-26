"""
GTI AI
News Engine
Version 1.0
"""

from datetime import datetime, timedelta

from models.news_event import NewsEvent


class NewsEngine:
    """
    Evaluates economic news events.
    """

    @staticmethod
    def is_high_impact(event: NewsEvent) -> bool:
        return event.impact.upper() == "HIGH"

    @staticmethod
    def should_trade(
        event: NewsEvent,
        now: datetime,
        minutes_before: int = 30,
        minutes_after: int = 30,
    ) -> bool:
        """
        Returns False if trading should be avoided
        around a high-impact event.
        """
        if not NewsEngine.is_high_impact(event):
            return True

        start = event.event_time - timedelta(minutes=minutes_before)
        end = event.event_time + timedelta(minutes=minutes_after)

        return not (start <= now <= end)

    @staticmethod
    def recommendation(event: NewsEvent, now: datetime) -> str:
        if NewsEngine.should_trade(event, now):
            return "TRADE"

        return "WAIT_FOR_NEWS"
