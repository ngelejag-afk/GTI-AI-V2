"""
GTI AI
Multi Timeframe Reader
Version 1.0
"""

from mt5.candle_reader import CandleReader
from mt5.timeframe_service import TimeframeService


class MultiTimeframeReader:
    """
    Reads market data from multiple timeframes.
    """

    @staticmethod
    def read(symbol: str, bars: int = 500) -> dict:
        """
        Returns candles from all configured timeframes.
        """
        return {
            "M5": CandleReader.read(
                symbol,
                TimeframeService.M5,
                bars,
            ),
            "M15": CandleReader.read(
                symbol,
                TimeframeService.M15,
                bars,
            ),
            "H1": CandleReader.read(
                symbol,
                TimeframeService.H1,
                bars,
            ),
            "H4": CandleReader.read(
                symbol,
                TimeframeService.H4,
                bars,
            ),
        }
