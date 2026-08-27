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
    """Compatibility stub for BOSEngine."""
    pass


class CHOCHEngine:
    """Compatibility stub for CHOCHEngine."""
    pass


class SMCAnalyzer:
    """Performs Smart Money Concepts analysis."""

    @staticmethod
    def analyze(candles: Sequence[Candle]) -> dict:
        """Analyze SMC conditions from closed candles."""
        candles = candles or []

        structure = StructurePipeline.analyze(candles)

        bos = (
            structure.bos != "INSUFFICIENT_DATA"
            and bool(structure.bos)
        )

        choch = (
            structure.choch != "INSUFFICIENT_DATA"
            and bool(structure.choch)
        )

        return SMCEngine.analyze(
            bos=bos,
            choch=choch,
            liquidity=False,
            fvg=False,
            order_block=False,
        )
