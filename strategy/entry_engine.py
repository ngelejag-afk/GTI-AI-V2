"""
GTI AI
Entry Engine
Version 1.0
"""


class EntryEngine:
    """
    Determines the entry price for a trade.
    """

    @staticmethod
    def calculate(
        decision: str,
        bid: float,
        ask: float,
    ) -> float:
        """
        Returns the recommended entry price.
        """
        if decision == "BUY":
            return ask

        if decision == "SELL":
            return bid

        return 0.0
