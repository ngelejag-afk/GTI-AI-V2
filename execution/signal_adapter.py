"""
GTI AI
Signal Adapter
Version 2.0
"""

from __future__ import annotations

from risk.trade_setup_engine import TradeSetupEngine


class SignalAdapter:
    """
    Converts an AI trading decision into an
    execution-ready trading signal.
    """

    @staticmethod
    def adapt(
        ai_signal: dict,
        symbol: str,
        bid: float,
        ask: float,
        atr: float,
        account_balance: float,
    ) -> dict:
        """
        Convert an AI signal into the format expected
        by the execution layer.
        """

        setup = TradeSetupEngine.build(
            signal=ai_signal.get("signal", "WAIT"),
            confidence=ai_signal.get("confidence", 0),
            bid=bid,
            ask=ask,
            atr=atr,
            account_balance=account_balance,
        )

        if not setup["valid"]:
            return {
                "symbol": symbol,
                "decision": "WAIT",
                "entry": 0.0,
                "stop_loss": 0.0,
                "take_profit": 0.0,
                "confidence": 0,
                "trade_allowed": False,
                "reason": setup.get("reason", "No valid setup."),
            }

        return {
            "symbol": symbol,
            "decision": setup["signal"],
            "entry": setup["entry"],
            "stop_loss": setup["stop_loss"],
            "take_profit": setup["take_profit"],
            "confidence": setup["confidence"],
            "trend": ai_signal.get("trend", "UNKNOWN"),
            "score": ai_signal.get("score", 0),
            "strength": ai_signal.get("strength", "WEAK"),
            "trade_allowed": ai_signal.get("trade_allowed", False),
            "lot_size": setup["lot_size"],
            "risk_amount": setup["risk_amount"],
            "risk_reward": setup["risk_reward"],
            "order_type": setup["order_type"],
            "reasons": ai_signal.get("reasons", []),
        }
