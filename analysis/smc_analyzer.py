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
    def analyze(candles) -> dict:
        bos = BOSEngine()
        choch = CHOCHEngine()
        liquidity = LiquiditySweepEngine()
        fvg = FVGEngine()
        order_block = OrderBlockEngine()

        return SMCEngine.analyze(
            bos=bos.bullish(candles),
            choch=choch.bullish(candles),
            liquidity=liquidity.buy_side(candles),
            fvg=fvg.bullish(candles),
            order_block=order_block.bullish(candles),
        )
