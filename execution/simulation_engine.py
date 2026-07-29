"""
GTI AI
Simulation Engine
Version 1.0
"""

from __future__ import annotations

from datetime import datetime

from execution.trade_history import TradeHistory
from analysis.performance_monitor import PerformanceMonitor


class SimulationEngine:
    """
    Executes and manages simulated trades.
    """

    _open_trades: list[dict] = []

    @classmethod
    def open_trade(cls, signal: dict) -> dict:
        """
        Open a simulated trade.
        """

        trade = {
            "symbol": signal["symbol"],
            "decision": signal["decision"],
            "entry": signal["entry"],
            "stop_loss": signal["stop_loss"],
            "take_profit": signal["take_profit"],
            "confidence": signal["confidence"],
            "status": "OPEN",
            "opened_at": datetime.utcnow().isoformat(),
        }

        cls._open_trades.append(trade)

        print(f"Simulation trade opened ({trade['decision']})")

        return trade

    @classmethod
    def update_price(cls, symbol: str, price: float) -> None:
        """
        Check whether any simulated trade should close.
        """

        for trade in list(cls._open_trades):

            if trade["symbol"] != symbol:
                continue

            result = None

            if trade["decision"] == "BUY":

                if price <= trade["stop_loss"]:
                    result = "LOSS"

                elif price >= trade["take_profit"]:
                    result = "WIN"

            elif trade["decision"] == "SELL":

                if price >= trade["stop_loss"]:
                    result = "LOSS"

                elif price <= trade["take_profit"]:
                    result = "WIN"

            if result is None:
                continue

            trade["status"] = "CLOSED"
            trade["closed_at"] = datetime.utcnow().isoformat()
            trade["exit"] = price
            trade["result"] = result

            TradeHistory.add(trade)

            PerformanceMonitor.record(
                decision=trade["decision"],
                confidence=trade["confidence"],
                result=result,
            )

            cls._open_trades.remove(trade)

            print(
                f"Simulation closed: "
                f"{trade['decision']} "
                f"{result} "
                f"@ {price}"
            )

    @classmethod
    def open_positions(cls) -> list[dict]:
        """
        Return all simulated open trades.
        """

        return list(cls._open_trades)
