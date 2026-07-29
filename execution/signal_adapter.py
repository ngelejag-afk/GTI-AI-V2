"""
GTI AI
Signal Adapter
Version 1.0
"""

from __future__ import annotations

from risk.stop_loss_engine import StopLossEngine
from risk.take_profit_engine import TakeProfitEngine


class SignalAdapter:
    """
    Converts an AI trading decision into
    an execution-ready trading signal.
    """

    @staticmethod
    def adapt(
        ai_signal: dict,
        symbol: str,
        entry: float,
    ) -> dict:
        """
        Convert an AI signal into the format expected
        by the execution layer.
        """

        decision = ai_signal.get("signal", "WAIT")

        stop_loss = StopLossEngine.calculate(
            entry=entry,
            decision=decision,
        )

        take_profit = TakeProfitEngine.calculate(
            entry=entry,
            stop_loss=stop_loss,
            decision=decision,
        )

        return {
            "symbol": symbol,
            "decision": decision,
            "entry": entry,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "confidence": ai_signal.get("confidence", 0),
            "trend": ai_signal.get("trend", "UNKNOWN"),
            "score": ai_signal.get("score", 0),
            "strength": ai_signal.get("strength", "WEAK"),
            "trade_allowed": ai_signal.get(
                "trade_allowed",
                False,
            ),
            "reasons": ai_signal.get("reasons", []),
        }
