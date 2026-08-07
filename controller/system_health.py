from __future__ import annotations
"""
GTI AI
System Health Monitor
Version 1.0
"""


from analysis.performance_dashboard import PerformanceDashboard
from controller.system_status import SystemStatus
from mt5.account_info import AccountInfo
from mt5.position_info import PositionInfo
from notifications.notification_center import NotificationCenter


class SystemHealth:
    """
    Provides a complete health summary for GTI AI.
    """

    @staticmethod
    def report() -> dict:
        """
        Return the overall system health.
        """

        return {
            "system": SystemStatus.get_status(),
            "account": AccountInfo.get(),
            "positions": PositionInfo.summary(),
            "notifications": NotificationCenter.statistics(),
            "performance": PerformanceDashboard.data(),
        }

    @staticmethod
    def ready() -> bool:
        """
        Check whether the system is ready.
        """

        account = AccountInfo.get()

        return bool(account.get("connected", False))
