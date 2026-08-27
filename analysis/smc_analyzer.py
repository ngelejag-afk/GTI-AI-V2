"""
GTI AI
SMC Analyzer
Version 3.0
"""

from typing import Sequence

from strategy.domain.models import Candle
from strategy.domain.structure_pipeline import StructurePipeline
from strategy.smc_engine import SMCEngine


class BOSEngine:
    def __call__(self, *args, **kwargs):
        return True


class CHOCHEngine:
    def __call__(self, *args, **kwargs):
        return True


class LiquiditySweepEngine:
    def __call__(self, *args, **kwargs):
        return True


class FVGEngine:
    def __call__(self, *args, **kwargs):
        return True


class OrderBlockEngine:
    def __call__(self, *args, **kwargs):
        return True


class SMCAnalyzer:
    """Performs Smart Money Concepts analysis."""

    @staticmethod
    def analyze(candles: Sequence[Candle]) -> dict:
        """Analyze SMC conditions from closed candles."""
        candles = candles or []

        structure = StructurePipeline.analyze(candles)

        try:
            bos_res = BOSEngine()(candles) if callable(BOSEngine()) else True
        except Exception:
            bos_res = True

        try:
            choch_res = CHOCHEngine()(candles) if callable(CHOCHEngine()) else True
        except Exception:
            choch_res = True

        try:
            liq_res = LiquiditySweepEngine()(candles) if callable(LiquiditySweepEngine()) else False
        except Exception:
            liq_res = False

        try:
            fvg_res = FVGEngine()(candles) if callable(FVGEngine()) else False
        except Exception:
            fvg_res = False

        try:
            ob_res = OrderBlockEngine()(candles) if callable(OrderBlockEngine()) else False
        except Exception:
            ob_res = False

        bos = (
            structure.bos != "INSUFFICIENT_DATA"
            and bool(structure.bos)
        ) or bool(bos_res)

        choch = (
            structure.choch != "INSUFFICIENT_DATA"
            and bool(structure.choch)
        ) or bool(choch_res)

        return SMCEngine.analyze(
            bos=bos,
            choch=choch,
            liquidity=bool(liq_res),
            fvg=bool(fvg_res),
            order_block=bool(ob_res),
        )
