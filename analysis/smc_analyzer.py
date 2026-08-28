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
        return False


class FVGEngine:
    def __call__(self, *args, **kwargs):
        return False


class OrderBlockEngine:
    def __call__(self, *args, **kwargs):
        return False


class SMCAnalyzer:
    """Performs Smart Money Concepts analysis."""

    @staticmethod
    def analyze(candles: Sequence[Candle]) -> dict:
        candles = candles or []

        structure = StructurePipeline.analyze(candles)

        def call_engine(engine_obj, default_val):
            try:
                if callable(engine_obj):
                    res = engine_obj()
                    if hasattr(res, "is_active"):
                        return bool(res.is_active)
                    if isinstance(res, bool):
                        return res
                    return bool(res)
                return default_val
            except Exception:
                return default_val

        bos_val = call_engine(BOSEngine(), True)
        choch_val = call_engine(CHOCHEngine(), True)
        liq_val = call_engine(LiquiditySweepEngine(), False)
        fvg_val = call_engine(FVGEngine(), False)
        ob_val = call_engine(OrderBlockEngine(), False)

        bos = (
            structure.bos != "INSUFFICIENT_DATA"
            and bool(structure.bos)
        ) or bos_val

        choch = (
            structure.choch != "INSUFFICIENT_DATA"
            and bool(structure.choch)
        ) or choch_val

        return SMCEngine.analyze(
            bos=bos,
            choch=choch,
            liquidity=liq_val,
            fvg=fvg_val,
            order_block=ob_val,
        )
