
"""
GTI AI
Multi Timeframe Analyzer
Version 1.0
"""

from analysis.market_analyzer import MarketAnalyzer


class MultiTimeframeAnalyzer:
    """
    Analyzes multiple timeframes.
    """

    @staticmethod
    def analyze(timeframes: dict) -> dict:
        results = {}

        for timeframe, candles in timeframes.items():
            results[timeframe] = MarketAnalyzer.analyze(candles)

        return results
