"""
GTI AI
SMC Analyzer
Version 2.1
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

        candles = candles or []

        bos_engine = BOSEngine()
        choch_engine = CHOCHEngine()
        liquidity_engine = LiquiditySweepEngine()
        fvg_engine = FVGEngine()
        order_block_engine = OrderBlockEngine()

        try:
            bos = bos_engine.bullish(candles)
        except Exception:
            bos = False

        try:
            choch = choch_engine.bullish(candles)
        except Exception:
            choch = False

        try:
            liquidity = liquidity_engine.buy_side(candles)
        except Exception:
            liquidity = False

        try:
            fvg = fvg_engine.bullish(candles)
        except Exception:
            fvg = False

        try:
            order_block = order_block_engine.bullish(candles)
        except Exception:
            order_block = False

        return SMCEngine.analyze(
            bos=bos,
            choch=choch,
            liquidity=liquidity,
            fvg=fvg,
            order_block=order_block,
        )
