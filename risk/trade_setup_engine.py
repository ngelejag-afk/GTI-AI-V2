from __future__ import annotations
"""
GTI AI
Trade Setup Engine
Version 1.0
"""


from risk.entry_price_engine import EntryPriceEngine
from risk.position_sizing_engine import PositionSizingEngine
from risk.stop_loss_engine import StopLossEngine


class TradeSetupEngine:
    """
    Builds a complete trade setup from the AI decision.
    """

    @staticmethod
    def build(
        signal: str,
        confidence: int,
        bid: float,
        ask: float,
        atr: float,
        account_balance: float,
        risk_percent: float = 1.0,
        pip_value: float = 10.0,
        risk_reward: float = 2.0,
    ) -> dict:
        """
        Build a complete trade setup.
        """

        entry = EntryPriceEngine.calculate(
            signal=signal,
            bid=bid,
            ask=ask,
        )

        if not entry["valid"]:
            return {
                "valid": False,
                "reason": "No trade signal.",
            }

        stop = StopLossEngine.calculate(
            signal=signal,
            entry_price=entry["entry"],
            atr=atr,
        )

        if not stop["valid"]:
            return {
                "valid": False,
                "reason": "Unable to calculate stop loss.",
            }

        position = PositionSizingEngine.calculate(
            balance=account_balance,
            risk_percent=risk_percent,
            stop_loss_pips=stop["risk_distance"],
            pip_value=pip_value,
        )

        if not position["valid"]:
            return {
                "valid": False,
                "reason": "Unable to calculate position size.",
            }

        risk = stop["risk_distance"] * risk_reward

        if signal.upper() == "BUY":
            take_profit = entry["entry"] + risk
        else:
            take_profit = entry["entry"] - risk

        return {
            "valid": True,
            "signal": signal,
            "confidence": confidence,
            "entry": round(entry["entry"], 2),
            "stop_loss": stop["stop_loss"],
            "take_profit": round(take_profit, 2),
            "risk_distance": stop["risk_distance"],
            "risk_reward": f"1:{risk_reward}",
            "lot_size": position["lot_size"],
            "risk_amount": position["risk_amount"],
            "order_type": entry["order_type"],
        }
