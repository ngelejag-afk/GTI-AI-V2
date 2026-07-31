"""
GTI AI
Trade Lifecycle Manager
Version 4.0
"""

from __future__ import annotations

from account.account_engine import AccountEngine
from analysis.performance_monitor import PerformanceMonitor
from execution.paper_trading_engine import PaperTradingEngine
from execution.profit_loss_engine import ProfitLossEngine
from execution.statistics_engine import StatisticsEngine
from execution.trade_journal import TradeJournal


class TradeLifecycleManager:
    """
    Updates paper and MT5 trades until they are closed.
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

            # MT5 trades are managed by the MT5 terminal.
            # This manager records their lifecycle once they
            # are marked as closed by the execution layer.
            if position.get("ticket") is not None:
                position["current_price"] = current_price
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

            StatisticsEngine.record(
                result=result["status"],
                profit=pnl["profit"] if result["status"] != "BREAKEVEN" else 0.0,
            )

            TradeJournal.record(
                symbol=position.get("symbol", "UNKNOWN"),
                decision=position["decision"],
                entry=position["entry"],
                exit_price=current_price,
                stop_loss=position.get("stop_loss", 0.0),
                take_profit=position.get("take_profit", 0.0),
                lot_size=position.get("lot_size", 0.01),
                profit=pnl["profit"],
                pips=pnl["pips"],
                confidence=position.get("confidence", 0),
                result=result["status"],
            )

    @staticmethod
    def attach_ticket(position: dict, ticket: int) -> None:
        """
        Attach an MT5 ticket to a position.
        """

        position["ticket"] = ticket

    @staticmethod
    def has_ticket(position: dict) -> bool:
        """
        Return whether the position has an MT5 ticket.
        """

        return position.get("ticket") is not None
