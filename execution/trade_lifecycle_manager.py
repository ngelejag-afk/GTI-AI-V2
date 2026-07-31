"""
GTI AI
Trade Lifecycle Manager
Version 3.1
"""

from __future__ import annotations

from account.account_engine import AccountEngine
from analysis.performance_monitor import PerformanceMonitor
from execution.paper_trading_engine import PaperTradingEngine
from execution.profit_loss_engine import ProfitLossEngine
from execution.statistics_engine import StatisticsEngine


class TradeLifecycleManager:
    """
    Updates paper trades until they are closed.
    """

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

            position["current_price"] = current_price

            pnl = ProfitLossEngine.calculate(
                decision=position["decision"],
                entry=position["entry"],
                current_price=current_price,
                lot_size=position.get("lot_size", 0.01),
            )

            position["floating_profit"] = pnl["profit"]
            position["floating_pips"] = pnl["pips"]
            position["floating_status"] = pnl["status"]

            if result["status"] == "OPEN":
                continue

            position["status"] = result["status"]

            AccountEngine.apply_profit(
                pnl["profit"]
            )

            PerformanceMonitor.record(
                decision=position["decision"],
                confidence=position["confidence"],
                result=result["status"],
            )

            if result["status"] == "WIN":
                StatisticsEngine.record(
                    result="WIN",
                    profit=pnl["profit"],
                )

            elif result["status"] == "LOSS":
                StatisticsEngine.record(
                    result="LOSS",
                    profit=pnl["profit"],
                )

            else:
                StatisticsEngine.record(
                    result="BREAKEVEN",
                    profit=0.0,
                )
