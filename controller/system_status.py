"""
GTI AI
System Status
Version 1.0
"""

from __future__ import annotations

from analysis.performance_dashboard import PerformanceDashboard
from notifications.notification_center import NotificationCenter


class SystemStatus:
    """
    Central system status provider.
    """

    @staticmethod
    def get_status() -> dict:
        """
        Return the overall GTI AI system status.
        """

        performance = PerformanceDashboard.data()
        notifications = NotificationCenter.statistics()

        return {
            "system": "GTI AI V2",
            "status": "ONLINE",
            "performance": performance,
            "notifications": notifications,
        }

    @staticmethod
    def health() -> dict:
        """
        Return a simple health report.
        """

        return {
            "dashboard": "ONLINE",
            "scanner": "ONLINE",
            "notifications": "ONLINE",
            "performance": "ONLINE",
        }
