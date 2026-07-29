"""
GTI AI
Trade Executor
Version 1.0
"""

from __future__ import annotations

from analysis.performance_monitor import PerformanceMonitor
from execution.order_manager import OrderManager
from execution.position_manager import PositionManager
from execution.trade_history import TradeHistory


class TradeExecutor:
    """
    Executes validated trading signals.
    """

    @classmethod
    def execute(cls, signal: dict) -> bool:
        """
        Execute a trading signal.

        Returns:
            True if the trade was accepted.
            False otherwise.
        """

        order = OrderManager.submit(signal)

        if order is None:
            return False

        PositionManager.open_position(order)

        TradeHistory.add(order)

        # Placeholder until live trade results are available.
        PerformanceMonitor.record(
            decision=order["decision"],
            confidence=order["confidence"],
            result="BREAKEVEN",
        )

        print("=" * 50)
        print(" GTI AI TRADE EXECUTED")
        print("=" * 50)
        print(f"Symbol      : {order['symbol']}")
        print(f"Decision    : {order['decision']}")
        print(f"Entry       : {order['entry']}")
        print(f"Stop Loss   : {order['stop_loss']}")
        print(f"Take Profit : {order['take_profit']}")
        print(f"Confidence  : {order['confidence']}%")
        print("=" * 50)

        return True

    @classmethod
    def open_positions(cls) -> list:
        """
        Return all open positions.
        """

        return PositionManager.open_positions()

    @classmethod
    def trade_history(cls) -> list:
        """
        Return executed trade history.
        """

        return TradeHistory.all()
