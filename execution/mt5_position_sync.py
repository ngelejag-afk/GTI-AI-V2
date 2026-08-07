from __future__ import annotations
"""
GTI AI
MT5 Position Sync
Version 1.0
"""


try:
    import MetaTrader5 as mt5
except ModuleNotFoundError:
    mt5 = None


class MT5PositionSync:
    """
    Synchronizes open positions from MetaTrader 5.
    """

    @staticmethod
    def positions() -> list[dict]:
        """
        Return all open MT5 positions.
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
                    "volume": position.volume,
                    "price_open": position.price_open,
                    "price_current": position.price_current,
                    "profit": position.profit,
                    "sl": position.sl,
                    "tp": position.tp,
                    "type": position.type,
                }
            )

        return results

    @classmethod
    def count(cls) -> int:
        """
        Return number of open positions.
        """

        return len(cls.positions())

    @classmethod
    def ticket_exists(cls, ticket: int) -> bool:
        """
        Check whether a ticket exists.
        """

        return any(
            position["ticket"] == ticket
            for position in cls.positions()
        )

    @classmethod
    def by_ticket(cls, ticket: int) -> dict | None:
        """
        Return a position by ticket.
        """

        for position in cls.positions():
            if position["ticket"] == ticket:
                return position

        return None
