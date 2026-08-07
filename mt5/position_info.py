from __future__ import annotations
"""
GTI AI
MT5 Position Information
Version 1.0
"""


try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None


class PositionInfo:
    """
    Provides information about open MT5 positions.
    """

    @staticmethod
    def get_all() -> list:
        """
        Return all open positions.
        """

        if mt5 is None:
            return []

        positions = mt5.positions_get()

        if positions is None:
            return []

        results = []

        for position in positions:
            results.append(
                {
                    "ticket": position.ticket,
                    "symbol": position.symbol,
                    "type": position.type,
                    "volume": float(position.volume),
                    "price_open": float(position.price_open),
                    "price_current": float(position.price_current),
                    "profit": float(position.profit),
                    "stop_loss": float(position.sl),
                    "take_profit": float(position.tp),
                }
            )

        return results

    @classmethod
    def total(cls) -> int:
        """
        Return the number of open positions.
        """

        return len(cls.get_all())

    @classmethod
    def total_profit(cls) -> float:
        """
        Return total floating profit/loss.
        """

        return round(
            sum(
                position["profit"]
                for position in cls.get_all()
            ),
            2,
        )

    @classmethod
    def summary(cls) -> dict:
        """
        Return a summary of open positions.
        """

        positions = cls.get_all()

        buy_positions = sum(
            1
            for position in positions
            if position["type"] == 0
        )

        sell_positions = sum(
            1
            for position in positions
            if position["type"] == 1
        )

        return {
            "total_positions": len(positions),
            "buy_positions": buy_positions,
            "sell_positions": sell_positions,
            "floating_profit": cls.total_profit(),
        }
