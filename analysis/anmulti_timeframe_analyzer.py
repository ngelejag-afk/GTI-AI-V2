"""
GTI AI
Multi Timeframe Analyzer
Version 1.0
"""

from analysis.market_analyzer import MarketAnalyzer


class MultiTimeframeAnalyzer:
    """
    Analyzes multiple timeframes independently.
    """

    @staticmethod
    def analyze(data: dict) -> dict:
        """
        Returns analysis for each timeframe.
        """
        result = {}

        for timeframe, candles in data.items():
            prices = [candle.close for candle in candles]

            result[timeframe] = MarketAnalyzer.analyze(prices)

        return result
