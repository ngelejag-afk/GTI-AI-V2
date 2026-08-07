from __future__ import annotations
"""
GTI AI
Performance Dashboard
Version 1.0
"""


from analysis.performance_monitor import PerformanceMonitor


class PerformanceDashboard:
    """
    Provides performance data for the dashboard.
    """

    @staticmethod
    def data() -> dict:
        """
        Return AI performance summary.
        """

        summary = PerformanceMonitor.summary()

        return {
            "total_trades": summary["total"],
            "wins": summary["wins"],
            "losses": summary["losses"],
            "breakeven": summary["breakeven"],
            "win_rate": summary["win_rate"],
            "average_confidence": summary["average_confidence"],
        }

    @staticmethod
    def history() -> list:
        """
        Return recorded performance history.
        """

        return PerformanceMonitor.history()

    @staticmethod
    def reset() -> None:
        """
        Reset all performance statistics.
        """

        PerformanceMonitor.reset()
