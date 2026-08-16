"""
End-to-end tests for the Trend -> Swing -> BOS domain pipeline.
"""

import unittest

from strategy.domain.bos_engine import BOSEngine, BOSEvent
from strategy.domain.models import Candle
from strategy.domain.swing_structure import SwingPoint, SwingStructureEngine


def candle(ts, o, h, l, c):
    return Candle(
        timestamp=ts,
        open=o,
        high=h,
        low=l,
        close=c,
        volume=1.0,
    )


class TestStructurePipeline(unittest.TestCase):
    def test_swing_feeds_bos_without_same_candle_break(self):
        candles = [
            candle(0, 100, 101, 99, 100),
            candle(1, 100, 102, 98, 101),
            candle(2, 101, 110, 100, 105),
            candle(3, 105, 106, 99, 102),
            candle(4, 102, 103, 100, 101),
            candle(5, 101, 104, 101, 103),
            candle(6, 103, 115, 102, 114),
        ]

        swings = SwingStructureEngine.analyze(candles)

        self.assertIsInstance(swings, list)

        swing_highs = [
            swing for swing in swings
            if swing.type == SwingStructureEngine.HIGH
        ]

        self.assertTrue(
            any(
                swing.timestamp == 2 and swing.price == 110
                for swing in swing_highs
            )
        )

        events = BOSEngine.analyze(candles, swings)

        self.assertIsInstance(events, list)

        self.assertTrue(
            all(isinstance(event, BOSEvent) for event in events)
        )

        for event in events:
            self.assertGreater(
                event.timestamp,
                event.broken_swing_timestamp,
            )

    def test_pipeline_uses_close_not_wick_for_bos(self):
        candles = [
            candle(0, 100, 101, 99, 100),
            candle(1, 100, 102, 98, 101),
            candle(2, 101, 110, 100, 105),
            candle(3, 105, 106, 99, 102),
            candle(4, 102, 103, 100, 101),
            candle(5, 101, 104, 101, 103),
            candle(6, 103, 120, 102, 109),
        ]

        swings = SwingStructureEngine.analyze(candles)

        events = BOSEngine.analyze(candles, swings)

        bullish_events = [
            event
            for event in events
            if event.direction == BOSEngine.BULLISH
        ]

        self.assertEqual(bullish_events, [])

    def test_pipeline_preserves_strict_swing_equality(self):
        candles = [
            candle(0, 100, 100, 99, 100),
            candle(1, 100, 105, 98, 101),
            candle(2, 101, 110, 100, 105),
            candle(3, 105, 110, 99, 102),
            candle(4, 102, 103, 100, 101),
        ]

        swings = SwingStructureEngine.analyze(candles)

        high_swings = [
            swing
            for swing in swings
            if swing.type == SwingStructureEngine.HIGH
        ]

        self.assertEqual(high_swings, [])

    def test_pipeline_preserves_independent_bos_sides(self):
        swings = [
            SwingPoint(
                timestamp=0,
                price=100.0,
                type=SwingStructureEngine.HIGH,
            ),
            SwingPoint(
                timestamp=0,
                price=50.0,
                type=SwingStructureEngine.LOW,
            ),
        ]

        candles = [
            candle(0, 75, 100, 50, 75),
            candle(1, 75, 80, 70, 75),
            candle(2, 75, 110, 70, 105),
            candle(3, 105, 106, 40, 45),
        ]

        events = BOSEngine.analyze(candles, swings)

        directions = [event.direction for event in events]

        self.assertIn(BOSEngine.BULLISH, directions)
        self.assertIn(BOSEngine.BEARISH, directions)

    def test_pipeline_is_deterministic(self):
        candles = [
            candle(0, 100, 101, 99, 100),
            candle(1, 100, 102, 98, 101),
            candle(2, 101, 110, 100, 105),
            candle(3, 105, 106, 99, 102),
            candle(4, 102, 103, 100, 101),
            candle(5, 101, 104, 101, 103),
            candle(6, 103, 115, 102, 114),
            candle(7, 114, 116, 108, 110),
            candle(8, 110, 118, 109, 117),
        ]

        first_swings = SwingStructureEngine.analyze(candles)
        first_events = BOSEngine.analyze(candles, first_swings)

        second_swings = SwingStructureEngine.analyze(candles)
        second_events = BOSEngine.analyze(candles, second_swings)

        self.assertEqual(first_swings, second_swings)
        self.assertEqual(first_events, second_events)

    def test_pipeline_does_not_mutate_inputs(self):
        candles = [
            candle(0, 100, 101, 99, 100),
            candle(1, 100, 102, 98, 101),
            candle(2, 101, 110, 100, 105),
            candle(3, 105, 106, 99, 102),
            candle(4, 102, 103, 100, 101),
            candle(5, 101, 104, 101, 103),
            candle(6, 103, 115, 102, 114),
        ]

        candle_snapshot = list(candles)

        swings = SwingStructureEngine.analyze(candles)
        swing_snapshot = list(swings)

        BOSEngine.analyze(candles, swings)

        self.assertEqual(candles, candle_snapshot)
        self.assertEqual(swings, swing_snapshot)

    def test_pipeline_has_no_bos_without_confirmed_swings(self):
        candles = [
            candle(0, 100, 101, 99, 100),
            candle(1, 100, 101, 99, 100),
            candle(2, 100, 101, 99, 100),
            candle(3, 100, 101, 99, 100),
        ]

        swings = SwingStructureEngine.analyze(candles)

        self.assertEqual(
            swings,
            SwingStructureEngine.INSUFFICIENT_DATA,
        )


if __name__ == "__main__":
    unittest.main()
