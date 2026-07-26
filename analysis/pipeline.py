"""
GTI AI
Analysis Pipeline
Version 1.0
"""

from analysis.market_analyzer import MarketAnalyzer
from ai.confluence_engine import ConfluenceEngine


class AnalysisPipeline:
    """
    Runs the complete market analysis pipeline.
    """

    def __init__(self):
        self.confluence = ConfluenceEngine()

    def analyze(self, prices: list[float]) -> dict:
        analysis = MarketAnalyzer.analyze(prices)

        result = self.confluence.calculate(
            trend=analysis["trend"],
            ema_aligned=analysis["ema_aligned"],
            bos=False,
            choch=False,
            liquidity=False,
            fvg=False,
            order_block=False,
            session_allowed=True,
            news_allowed=True,
        )

        return {
            "analysis": analysis,
            "decision": result,
        }
