"""
GTI AI
Backtest Simulator
Version 1.0
"""


class BacktestSimulator:
    """
    Simulates trade outcomes using historical candles.
    """

    @staticmethod
    def simulate(
        candles: list,
        start_index: int,
        signal: str,
        entry: float,
        stop_loss: float,
        take_profit: float,
    ) -> str:
        """
        Returns:
            WIN
            LOSS
            OPEN
        """

        for candle in candles[start_index:]:

            if signal == "BUY":

                if candle.low <= stop_loss:
                    return "LOSS"

                if candle.high >= take_profit:
                    return "WIN"

            elif signal == "SELL":

                if candle.high >= stop_loss:
                    return "LOSS"

                if candle.low <= take_profit:
                    return "WIN"

        return "OPEN"
