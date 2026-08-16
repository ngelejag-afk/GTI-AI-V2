"""Regression tests for CHoCH integration in StructurePipeline."""

import unittest
from dataclasses import dataclass

from strategy.domain.bos_engine import BOSEvent
from strategy.domain.choch_engine import CHOCHEngine, CHoCHEvent
from strategy.domain.structure_pipeline import StructureAnalysis


def bos(timestamp: int, direction: str) -> BOSEvent:
    """Create a deterministic BOS event for result-contract tests."""
    return BOSEvent(
        timestamp=timestamp,
        direction=direction,
        broken_swing_price=100.0,
        broken_swing_timestamp=timestamp - 1,
    )


class TestStructureAnalysisCHoCH(unittest.TestCase):
    def test_structure_analysis_exposes_choch_result(self):
        result = StructureAnalysis(
            trend="BULLISH",
            swings=[],
            bos=[
                bos(1, "BULLISH"),
                bos(2, "BEARISH"),
            ],
            choch=[
                CHoCHEvent(
                    timestamp=2,
                    from_regime="BULLISH",
                    to_regime="BEARISH",
                )
            ],
        )

        self.assertEqual(result.trend, "BULLISH")
        self.assertEqual(len(result.bos), 2)
        self.assertEqual(len(result.choch), 1)

    def test_same_direction_bos_has_no_choch(self):
        bos_events = [
            bos(1, "BULLISH"),
            bos(2, "BULLISH"),
            bos(3, "BULLISH"),
        ]

        result = CHOCHEngine.analyze(bos_events)

        self.assertEqual(result, [])

    def test_opposite_bos_direction_produces_choch(self):
        bos_events = [
            bos(1, "BULLISH"),
            bos(2, "BEARISH"),
        ]

        result = CHOCHEngine.analyze(bos_events)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].timestamp, 2)
        self.assertEqual(result[0].from_regime, "BULLISH")
        self.assertEqual(result[0].to_regime, "BEARISH")

    def test_multiple_regime_changes_are_preserved(self):
        bos_events = [
            bos(1, "BULLISH"),
            bos(2, "BEARISH"),
            bos(3, "BEARISH"),
            bos(4, "BULLISH"),
            bos(5, "BULLISH"),
            bos(6, "BEARISH"),
        ]

        result = CHOCHEngine.analyze(bos_events)

        self.assertEqual(
            [(event.timestamp, event.from_regime, event.to_regime)
             for event in result],
            [
                (2, "BULLISH", "BEARISH"),
                (4, "BEARISH", "BULLISH"),
                (6, "BULLISH", "BEARISH"),
            ],
        )


if __name__ == "__main__":
    unittest.main()
