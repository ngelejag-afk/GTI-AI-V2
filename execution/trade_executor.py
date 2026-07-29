"""
GTI AI
Trade Executor
Version 3.0
"""

from __future__ import annotations

from analysis.performance_monitor import PerformanceMonitor
from execution.order_manager import OrderManager
from execution.paper_trading_engine import PaperTradingEngine
from execution.position_manager import PositionManager
from execution.trade_history import TradeHistory
from risk.account_risk_manager import AccountRiskManager
from risk.daily_loss_guard import DailyLossGuard
from risk.drawdown_protector import DrawdownProtector
from risk.trading_session_filter import TradingSessionFilter


class TradeExecutor:
    """
    Executes validated trading signals after
    passing all risk management checks.
    """

    STARTING_BALANCE = 1000.0
    CURRENT_BALANCE = 1000.0

    @classmethod
    def execute(cls, signal: dict) -> bool:
        """
        Execute a trading signal.
        """

        if signal.get("decision") not in ("BUY", "SELL"):
            print("Execution skipped: WAIT signal.")
            return False

        if not TradingSessionFilter.trading_allowed():
            print("Execution blocked: Trading session is closed.")
            return False

        if not DrawdownProtector.is_allowed(
            starting_balance=cls.STARTING_BALANCE,
            current_balance=cls.CURRENT_BALANCE,
        ):
            print("Execution blocked: Drawdown limit reached.")
            return False

        DailyLossGuard.update_balance(cls.CURRENT_BALANCE)

        if not DailyLossGuard.trading_allowed():
            print("Execution blocked: Daily loss limit reached.")
            return False

        order = OrderManager.submit(signal)

        if order is None:
            print("Execution blocked: Invalid or duplicate order.")
            return False

        risk = AccountRiskManager.calculate_position(
            balance=cls.CURRENT_BALANCE,
            stop_loss_pips=100,
        )

        order["lot_size"] = risk["lot_size"]
        order["risk_percent"] = risk["risk_percent"]

        PositionManager.open_position(order)
        TradeHistory.add(order)

        paper_trade = PaperTradingEngine.update(
            order=order,
            current_price=order["entry"],
        )

        if paper_trade["status"] in ("WIN", "LOSS", "BREAKEVEN"):
            PerformanceMonitor.record(
                decision=order["decision"],
                confidence=order["confidence"],
                result=paper_trade["status"],
            )

        print("=" * 50)
        print(" GTI AI TRADE EXECUTED")
        print("=" * 50)
        print(f"Symbol        : {order['symbol']}")
        print(f"Decision      : {order['decision']}")
        print(f"Entry         : {order['entry']}")
        print(f"Stop Loss     : {order['stop_loss']}")
        print(f"Take Profit   : {order['take_profit']}")
        print(f"Lot Size      : {order['lot_size']}")
        print(f"Risk          : {order['risk_percent']}%")
        print(f"Confidence    : {order['confidence']}%")
        print(f"Status        : {paper_trade['status']}")
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
        Return trade history.
        """

        return TradeHistory.all()
