"""
GTI AI
Trade Lifecycle Manager
Version 2.0
"""

from __future__ import annotations

from account.account_engine import AccountEngine
from analysis.performance_monitor import PerformanceMonitor
from execution.paper_trading_engine import PaperTradingEngine


class TradeLifecycleManager:
    """
    Updates paper trades until they are closed.
    """

    WIN_AMOUNT = 20.0
    LOSS_AMOUNT = -10.0

    @staticmethod
    def update(
        positions: list[dict],
        current_price: float,
    ) -> None:
        """
        Update every open position.
        """

        for position in positions:

            if position.get("status") != "OPEN":
                continue

            result = PaperTradingEngine.update(
                order=position,
                current_price=current_price,
            )

            position["current_price"] = result["current_price"]

            if result["status"] == "OPEN":
                continue

            position["status"] = result["status"]

            if result["status"] == "WIN":
                AccountEngine.apply_profit(
                    TradeLifecycleManager.WIN_AMOUNT
                )

            elif result["status"] == "LOSS":
                AccountEngine.apply_profit(
                    TradeLifecycleManager.LOSS_AMOUNT
                )

            PerformanceMonitor.record(
                decision=position["decision"],
                confidence=position["confidence"],
                result=result["status"],
            )
