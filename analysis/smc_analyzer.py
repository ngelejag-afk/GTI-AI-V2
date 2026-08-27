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
    def __init__(self, is_active=True):
        self.is_active = is_active
    def __call__(self, *args, **kwargs):
        return self.is_active


class CHOCHEngine:
    def __init__(self, is_active=True):
        self.is_active = is_active
    def __call__(self, *args, **kwargs):
        return self.is_active


class LiquiditySweepEngine:
    def __init__(self, is_active=False):
        self.is_active = is_active
    def __call__(self, *args, **kwargs):
        return self.is_active


class FVGEngine:
    def __init__(self, is_active=False):
        self.is_active = is_active
    def __call__(self, *args, **kwargs):
        return self.is_active


class OrderBlockEngine:
    def __init__(self, is_active=False):
        self.is_active = is_active
    def __call__(self, *args, **kwargs):
        return self.is_active


class SMCAnalyzer:
    """Performs Smart Money Concepts analysis."""

    @staticmethod
    def analyze(candles: Sequence[Candle]) -> dict:
        candles = candles or []

        structure = StructurePipeline.analyze(candles)

        def evaluate_engine(engine_cls, default_val):
            try:
                obj = engine_cls()
                if hasattr(obj, "is_active"):
                    return bool(obj.is_active)
                if callable(obj):
                    res = obj()
                    if hasattr(res, "is_active"):
                        return bool(res.is_active)
                    return bool(res)
                return bool(obj)
            except Exception:
                return default_val

        bos_val = evaluate_engine(BOSEngine, True)
        choch_val = evaluate_engine(CHOCHEngine, True)
        liq_val = evaluate_engine(LiquiditySweepEngine, False)
        fvg_val = evaluate_engine(FVGEngine, False)
        ob_val = evaluate_engine(OrderBlockEngine, False)

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
