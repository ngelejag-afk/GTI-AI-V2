"""
GTI AI
Dashboard Data
Version 1.0
"""

from __future__ import annotations

from notifications.notification_center import NotificationCenter


class DashboardData:
    """
    Supplies dashboard data from all system components.
    """

    @staticmethod
    def build(current_signal: dict) -> dict:
        """
        Build dashboard payload.
        """

        statistics = NotificationCenter.statistics()

        return {
            "current_signal": current_signal,
            "statistics": statistics,
            "notifications": NotificationCenter.latest(10),
        }
