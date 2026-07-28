"""
GTI AI
Multi Timeframe Analyzer
Version 2.0
"""

from analysis.market_analyzer import MarketAnalyzer


class MultiTimeframeAnalyzer:
    """
    Analyzes multiple timeframes and provides confirmation.
    """

    @staticmethod
    def analyze(timeframes: dict) -> dict:
        """
        Analyze all supplied timeframes.
        """

        if not timeframes:
            return {
                "timeframes": {},
                "confirmed": False,
                "trend": "UNKNOWN",
            }

        results = {}

        bullish = 0
        bearish = 0

        for timeframe, prices in timeframes.items():
            analysis = MarketAnalyzer.analyze(prices)

            results[timeframe] = analysis

            bias = analysis["market_bias"]

            if bias == "BULLISH":
                bullish += 1
            elif bias == "BEARISH":
                bearish += 1

        confirmed = bullish > bearish or bearish > bullish

        if bullish > bearish:
            trend = "BULLISH"
        elif bearish > bullish:
            trend = "BEARISH"
        else:
            trend = "SIDEWAYS"

        return {
            "timeframes": results,
            "confirmed": confirmed,
            "trend": trend,
            "bullish": bullish,
            "bearish": bearish,
            }
