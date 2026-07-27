"""
GTI AI
SMC Analyzer
Version 1.1
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

        if len(candles) < 3:
            return {
                "score": 0,
                "confirmed": False,
                "reasons": ["Not enough candles"],
            }

        first = candles[-3]
        previous = candles[-2]
        current = candles[-1]

        bos = BOSEngine.bullish(previous, current)
        choch = CHOCHEngine.bullish(previous, current)
        liquidity = LiquiditySweepEngine.buy_side(previous, current)
        fvg = FVGEngine.bullish(first, previous, current)
        order_block = OrderBlockEngine.bullish(previous, current)

        return SMCEngine.analyze(
            bos=bos,
            choch=choch,
            liquidity=liquidity,
            fvg=fvg,
            order_block=order_block,
        )
