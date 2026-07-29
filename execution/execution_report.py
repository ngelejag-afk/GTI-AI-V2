"""
GTI AI
Execution Report
Version 1.0
"""

from __future__ import annotations

from analysis.performance_monitor import PerformanceMonitor
from execution.position_manager import PositionManager
from execution.trade_history import TradeHistory


class ExecutionReport:
    """
    Generates execution statistics.
    """

    @classmethod
    def summary(cls) -> dict:
        """
        Return execution summary.
        """

        trades = TradeHistory.all()
        performance = PerformanceMonitor.summary()

        buy_orders = sum(
            1
            for trade in trades
            if trade.get("decision") == "BUY"
        )

        sell_orders = sum(
            1
            for trade in trades
            if trade.get("decision") == "SELL"
        )

        return {
            "total_trades": len(trades),
            "open_positions": PositionManager.total_open(),
            "closed_positions": max(
                0,
                len(trades) - PositionManager.total_open(),
            ),
            "buy_orders": buy_orders,
            "sell_orders": sell_orders,
            "win_rate": performance["win_rate"],
            "average_confidence": performance["average_confidence"],
            "system_status": "READY",
        }

    @classmethod
    def print_report(cls) -> None:
        """
        Print execution report.
        """

        report = cls.summary()

        print("=" * 50)
        print(" GTI AI EXECUTION REPORT")
        print("=" * 50)
        print(f"Total Trades       : {report['total_trades']}")
        print(f"Open Positions     : {report['open_positions']}")
        print(f"Closed Positions   : {report['closed_positions']}")
        print()
        print(f"BUY Orders         : {report['buy_orders']}")
        print(f"SELL Orders        : {report['sell_orders']}")
        print()
        print(f"Win Rate           : {report['win_rate']}%")
        print(
            f"Average Confidence : "
            f"{report['average_confidence']}%"
        )
        print()
        print(f"System Status      : {report['system_status']}")
        print("=" * 50)
