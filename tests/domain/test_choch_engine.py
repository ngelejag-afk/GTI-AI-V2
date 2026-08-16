"""
Unit tests for CHOCHEngine (Sprint 2 clean rebuild).
"""

import unittest

from strategy.domain.bos_engine import BOSEvent
from strategy.domain.choch_engine import CHOCHEngine, CHoCHEvent


def bos(ts, direction, price=100.0):
    return BOSEvent(
        timestamp=ts,
        direction=direction,
        broken_swing_price=price,
        broken_swing_timestamp=ts - 1,
    )


class TestCHOCHEngine(unittest.TestCase):

    def test_insufficient_data_when_no_bos_events(self):
        result = CHOCHEngine.analyze([])
        self.assertEqual(result, CHOCHEngine.INSUFFICIENT_DATA)

    def test_single_bos_establishes_regime_no_choch(self):
        events = [bos(1, "BULLISH")]
        result = CHOCHEngine.analyze(events)
        self.assertEqual(result, [])

    def test_same_direction_bos_is_continuation_not_choch(self):
        events = [
            bos(1, "BULLISH"),
            bos(2, "BULLISH"),
            bos(3, "BULLISH"),
        ]
        result = CHOCHEngine.analyze(events)
        self.assertEqual(result, [])

    def test_direction_flip_is_choch(self):
        events = [
            bos(1, "BULLISH"),
            bos(2, "BEARISH"),
        ]
        result = CHOCHEngine.analyze(events)
        self.assertEqual(len(result), 1)
        event = result[0]
        self.assertIsInstance(event, CHoCHEvent)
        self.assertEqual(event.timestamp, 2)
        self.assertEqual(event.from_regime, "BULLISH")
        self.assertEqual(event.to_regime, "BEARISH")

    def test_multiple_flips_each_produce_choch(self):
        events = [
            bos(1, "BULLISH"),
            bos(2, "BEARISH"),   # CHoCH #1
            bos(3, "BEARISH"),   # continuation
            bos(4, "BULLISH"),   # CHoCH #2
        ]
        result = CHOCHEngine.analyze(events)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].timestamp, 2)
        self.assertEqual(result[0].from_regime, "BULLISH")
        self.assertEqual(result[0].to_regime, "BEARISH")
        self.assertEqual(result[1].timestamp, 4)
        self.assertEqual(result[1].from_regime, "BEARISH")
        self.assertEqual(result[1].to_regime, "BULLISH")

    def test_all_same_direction_never_produces_choch(self):
        events = [bos(i, "BULLISH") for i in range(1, 10)]
        result = CHOCHEngine.analyze(events)
        self.assertEqual(result, [])

    def test_does_not_mutate_input(self):
        events = [bos(1, "BULLISH"), bos(2, "BEARISH")]
        snapshot = list(events)
        CHOCHEngine.analyze(events)
        self.assertEqual(events, snapshot)

    def test_deterministic_repeated_calls(self):
        events = [bos(1, "BULLISH"), bos(2, "BEARISH"), bos(3, "BULLISH")]
        first = CHOCHEngine.analyze(events)
        second = CHOCHEngine.analyze(events)
        self.assertEqual(first, second)

    def test_returns_choch_event_dataclass_instances(self):
        events = [bos(1, "BULLISH"), bos(2, "BEARISH")]
        result = CHOCHEngine.analyze(events)
        for event in result:
            self.assertIsInstance(event, CHoCHEvent)


if __name__ == "__main__":
    unittest.main()
