"""
GTI AI
SMC Analyzer
Version 2.0
"""

from strategy.bos_engine import BOSEngine
from strategy.choch_engine import CHOCHEngine
from strategy.fvg_engine import FVGEngine
from strategy.liquidity_sweep_engine import LiquiditySweepEngine
from strategy.order_block_engine import OrderBlockEngine
from strategy.smc_engine import SMCEngine


class SMCAnalyzer:
    """
    Performs Smart Money Concepts (SMC) analysis.
    """

    @staticmethod
    def analyze(candles: list) -> dict:
        """
        Analyze Smart Money Concepts from candle data.
        """

        if not candles:
            return {
                "score": 0,
                "confirmed": False,
                "bos": False,
                "choch": False,
                "liquidity": False,
                "fvg": False,
                "order_block": False,
            }

        bos_engine = BOSEngine()
        choch_engine = CHOCHEngine()
        liquidity_engine = LiquiditySweepEngine()
        fvg_engine = FVGEngine()
        order_block_engine = OrderBlockEngine()

        bos = bos_engine.bullish(candles)
        choch = choch_engine.bullish(candles)
        liquidity = liquidity_engine.buy_side(candles)
        fvg = fvg_engine.bullish(candles)
        order_block = order_block_engine.bullish(candles)

        return SMCEngine.analyze(
            bos=bos,
            choch=choch,
            liquidity=liquidity,
            fvg=fvg,
            order_block=order_block,
        )
