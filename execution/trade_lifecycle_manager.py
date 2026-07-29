"""
GTI AI
Trade Lifecycle Manager
Version 1.0
"""

from __future__ import annotations

from analysis.performance_monitor import PerformanceMonitor
from execution.paper_trading_engine import PaperTradingEngine


class TradeLifecycleManager:
    """
    Updates all open paper trades and records
    completed trade results.
    """

    @staticmethod
    def update(
        positions: list[dict],
        current_price: float,
    ) -> None:
        """
        Update every open position using the latest price.
        """

        for position in positions:
            if position.get("status") in ("WIN", "LOSS"):
                continue

            result = PaperTradingEngine.update(
                order=position,
                current_price=current_price,
            )

            position["current_price"] = result["current_price"]
            position["status"] = result["status"]

            if result["status"] in ("WIN", "LOSS"):
                PerformanceMonitor.record(
                    decision=position["decision"],
                    confidence=position["confidence"],
                    result=result["status"],
                )
