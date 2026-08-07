from __future__ import annotations
"""
GTI AI
Dashboard Data
Version 2.1
"""


from analysis.performance_dashboard import PerformanceDashboard
from execution.statistics_engine import StatisticsEngine
from mt5.account_info import AccountInfo
from mt5.position_info import PositionInfo
from notifications.notification_center import NotificationCenter


class DashboardData:
    """
    Supplies all data required by the GTI AI dashboard.
    """

    @staticmethod
    def build(current_signal: dict) -> dict:
        """
        Build the dashboard payload.
        """

        return {
            "current_signal": current_signal,
            "statistics": NotificationCenter.statistics(),
            "notifications": NotificationCenter.latest(10),
            "performance": PerformanceDashboard.data(),
            "trading_statistics": StatisticsEngine.summary(),
            "account": AccountInfo.get(),
            "positions": PositionInfo.summary(),
        }
