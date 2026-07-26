"""
GTI AI
SMC Analyzer
Version 1.0
"""

from strategy.bos_engine import BOSEngine
from strategy.choch_engine import CHOCHEngine
from strategy.fvg_engine import FVGEngine
from strategy.liquidity_sweep_engine import LiquiditySweepEngine
from strategy.order_block_engine import OrderBlockEngine
from strategy.smc_engine import SMCEngine


class SMCAnalyzer:
    """
    Runs Smart Money Concepts analysis.
    """

    @staticmethod
    def analyze(candles: list) -> dict:
        """
        Returns Smart Money Concepts analysis.
        """
        bos = BOSEngine.bullish(candles)
        choch = CHOCHEngine.bullish(candles)
        liquidity = LiquiditySweepEngine.buy_side(candles)
        fvg = FVGEngine.bullish(candles)
        order_block = OrderBlockEngine.bullish(candles)

        return SMCEngine.analyze(
            bos=bos,
            choch=choch,
            liquidity=liquidity,
            fvg=fvg,
            order_block=order_block,
        )
