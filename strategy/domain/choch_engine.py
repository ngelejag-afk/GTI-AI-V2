"""
GTI AI - Domain Layer
Change Of Character (CHoCH) Engine (clean rebuild, Sprint 2)

Contract:
    Input:
        A chronological sequence of BOSEvent (from BOSEngine),
        oldest first.

    Concept:
        The "regime" is the prevailing structural direction,
        set by the most recent BOS event.

        The FIRST BOS event in the sequence can never be a CHoCH:
        it only establishes the initial regime.

    Rule (processing BOS events in order):
        - If no regime is established yet: this BOS sets the
          initial regime. Not a CHoCH.
        - If this BOS shares the current regime's direction:
          this is a continuation. Not a CHoCH.
        - If this BOS opposes the current regime's direction:
          this IS a CHoCH. The regime flips to this BOS's
          direction.

    Output:
        "INSUFFICIENT_DATA" if no BOS events were supplied.
        Otherwise a list of CHoCHEvent (possibly empty, if all
        BOS events shared the same direction).

    Purity:
        Does not mutate the input BOSEvent sequence.
        Deterministic given the same inputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence, Union

from strategy.domain.bos_engine import BOSEvent

INSUFFICIENT_DATA = "INSUFFICIENT_DATA"


@dataclass(frozen=True)
class CHoCHEvent:
    timestamp: int
    from_regime: str
    to_regime: str


class CHOCHEngine:
    """Detects Change Of Character events from a BOS event sequence."""

    INSUFFICIENT_DATA = INSUFFICIENT_DATA

    @staticmethod
    def analyze(
        bos_events: Sequence[BOSEvent],
    ) -> Union[str, List[CHoCHEvent]]:
        if not bos_events:
            return CHOCHEngine.INSUFFICIENT_DATA

        events: List[CHoCHEvent] = []
        regime: str | None = None

        for bos in bos_events:
            if regime is None:
                regime = bos.direction
                continue

            if bos.direction == regime:
                continue

            events.append(
                CHoCHEvent(
                    timestamp=bos.timestamp,
                    from_regime=regime,
                    to_regime=bos.direction,
                )
            )
            regime = bos.direction

        return events
