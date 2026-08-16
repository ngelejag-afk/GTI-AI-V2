"""GTI AI - Domain Layer.

Structure Pipeline
==================

Coordinates the causal Trend -> Swing Structure -> BOS -> CHoCH
domain engines.

Contract:
    Input:
        A sequence of CLOSED candles, oldest first.

    Processing:
        1. TrendEngine analyzes EMA20/EMA50/EMA200 alignment.
        2. SwingStructureEngine detects confirmed fractal swings.
        3. BOSEngine evaluates breaks using only confirmed swings that
           are strictly older than the break candle.
        4. CHOCHEngine evaluates chronological BOS events to detect
           structural regime changes.

    Output:
        StructureAnalysis containing the independent results of all
        domain stages.

    Purity:
        The pipeline does not mutate its input or any intermediate result.

    Determinism:
        Identical candle sequences produce identical results.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Union

from strategy.domain.bos_engine import BOSEngine, BOSEvent
from strategy.domain.choch_engine import CHOCHEngine, CHoCHEvent
from strategy.domain.models import Candle
from strategy.domain.swing_structure import (
    SwingPoint,
    SwingStructureEngine,
)
from strategy.domain.trend_engine import TrendEngine


DomainResult = Union[
    str,
    List[SwingPoint],
    List[BOSEvent],
    List[CHoCHEvent],
]


@dataclass(frozen=True)
class StructureAnalysis:
    """Immutable result of the complete structure pipeline."""

    trend: str
    swings: Union[str, List[SwingPoint]]
    bos: Union[str, List[BOSEvent]]
    choch: Union[str, List[CHoCHEvent]]


class StructurePipeline:
    """Coordinates the causal domain structure engines."""

    @staticmethod
    def analyze(candles: Sequence[Candle]) -> StructureAnalysis:
        """Analyze trend, confirmed swings, BOS events, and CHoCH events.

        The caller is responsible for providing closed candles only.
        """
        trend = TrendEngine.analyze(candles)
        swings = SwingStructureEngine.analyze(candles)

        if swings == SwingStructureEngine.INSUFFICIENT_DATA:
            return StructureAnalysis(
                trend=trend,
                swings=SwingStructureEngine.INSUFFICIENT_DATA,
                bos=BOSEngine.INSUFFICIENT_DATA,
                choch=CHOCHEngine.INSUFFICIENT_DATA,
            )

        bos = BOSEngine.analyze(candles, swings)

        if bos == BOSEngine.INSUFFICIENT_DATA:
            choch = CHOCHEngine.INSUFFICIENT_DATA
        else:
            choch = CHOCHEngine.analyze(bos)

        return StructureAnalysis(
            trend=trend,
            swings=swings,
            bos=bos,
            choch=choch,
        )
