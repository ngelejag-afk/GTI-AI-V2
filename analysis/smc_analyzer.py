from __future__ import annotations

from typing import Sequence

from strategy.domain.models import Candle
from strategy.domain.structure_pipeline import StructurePipeline


class SMCAnalyzer:
    """Analyze SMC execution conditions from closed candles."""

    @staticmethod
    def analyze(candles: Sequence[Candle]) -> dict:
        candles = list(candles or [])

        if len(candles) < 5:
            return SMCAnalyzer._insufficient()

        structure = StructurePipeline.analyze(candles)

        bos_events = (
            structure.bos
            if isinstance(structure.bos, list)
            else []
        )

        choch_events = (
            structure.choch
            if isinstance(structure.choch, list)
            else []
        )

        bos = bool(bos_events)
        choch = bool(choch_events)

        liquidity_direction = SMCAnalyzer._liquidity_sweep(candles)
        fvg_direction = SMCAnalyzer._fvg(candles)
        order_block_direction = SMCAnalyzer._order_block(candles)
        displacement_direction = SMCAnalyzer._displacement(candles)

        liquidity = liquidity_direction != "NONE"
        fvg = fvg_direction != "NONE"
        order_block = order_block_direction != "NONE"
        displacement = displacement_direction != "NONE"

        directions: list[str] = []

        if bos_events:
            latest_bos = bos_events[-1]
            directions.append(str(latest_bos.direction).upper())

        if choch_events:
            latest_choch = choch_events[-1]
            directions.append(str(latest_choch.to_regime).upper())

        if liquidity_direction != "NONE":
            directions.append(liquidity_direction)

        if fvg_direction != "NONE":
            directions.append(fvg_direction)

        if order_block_direction != "NONE":
            directions.append(order_block_direction)

        if displacement_direction != "NONE":
            directions.append(displacement_direction)

        bullish_count = directions.count("BULLISH")
        bearish_count = directions.count("BEARISH")

        if bullish_count > bearish_count:
            direction = "BUY"
        elif bearish_count > bullish_count:
            direction = "SELL"
        else:
            direction = "NEUTRAL"

        score = 0

        if bos:
            score += 20

        if choch:
            score += 20

        if liquidity:
            score += 20

        if fvg:
            score += 15

        if order_block:
            score += 15

        if displacement:
            score += 10

        score = min(score, 100)

        conflicting = False

        if direction == "BUY":
            conflicting = any(
                value == "BEARISH"
                for value in directions
            )

        elif direction == "SELL":
            conflicting = any(
                value == "BULLISH"
                for value in directions
            )

        structural_confirmation = bos or choch
        execution_zone = fvg or order_block

        confirmed = (
            score >= 60
            and structural_confirmation
            and liquidity
            and displacement
            and execution_zone
            and not conflicting
            and direction in ("BUY", "SELL")
        )

        reasons: list[str] = []

        if bos:
            reasons.append("BOS")

        if choch:
            reasons.append("CHoCH")

        if liquidity:
            reasons.append(f"Liquidity Sweep ({liquidity_direction})")

        if fvg:
            reasons.append(f"FVG ({fvg_direction})")

        if order_block:
            reasons.append(f"Order Block ({order_block_direction})")

        if displacement:
            reasons.append(f"Displacement ({displacement_direction})")

        if conflicting:
            reasons.append("CONFLICTING SMC DIRECTION")

        return {
            "direction": direction,

            "bos": bos,
            "choch": choch,
            "liquidity": liquidity,
            "fvg": fvg,
            "order_block": order_block,
            "displacement": displacement,

            "bos_events": bos_events,
            "choch_events": choch_events,

            "liquidity_direction": liquidity_direction,
            "fvg_direction": fvg_direction,
            "order_block_direction": order_block_direction,
            "displacement_direction": displacement_direction,

            "bullish_count": bullish_count,
            "bearish_count": bearish_count,

            "score": score,
            "conflicting": conflicting,
            "confirmed": confirmed,

            "execution_ready": confirmed,

            "reasons": reasons,
        }

    @staticmethod
    def _liquidity_sweep(candles: Sequence[Candle]) -> str:
        if len(candles) < 2:
            return "NONE"

        previous = candles[-2]
        current = candles[-1]

        if (
            current.low < previous.low
            and current.close > previous.low
        ):
            return "BULLISH"

        if (
            current.high > previous.high
            and current.close < previous.high
        ):
            return "BEARISH"

        return "NONE"

    @staticmethod
    def _fvg(candles: Sequence[Candle]) -> str:
        if len(candles) < 3:
            return "NONE"

        first = candles[-3]
        third = candles[-1]

        if third.low > first.high:
            return "BULLISH"

        if third.high < first.low:
            return "BEARISH"

        return "NONE"

    @staticmethod
    def _order_block(candles: Sequence[Candle]) -> str:
        if len(candles) < 2:
            return "NONE"

        previous = candles[-2]
        current = candles[-1]

        if (
            previous.close < previous.open
            and current.close > previous.high
        ):
            return "BULLISH"

        if (
            previous.close > previous.open
            and current.close < previous.low
        ):
            return "BEARISH"

        return "NONE"

    @staticmethod
    def _displacement(candles: Sequence[Candle]) -> str:
        if len(candles) < 7:
            return "NONE"

        previous = candles[-6:-1]
        current = candles[-1]

        bodies = [
            abs(c.close - c.open)
            for c in previous
        ]

        if not bodies:
            return "NONE"

        average_body = sum(bodies) / len(bodies)

        if average_body <= 0:
            return "NONE"

        current_body = abs(current.close - current.open)

        if current_body < average_body * 1.5:
            return "NONE"

        if current.close > current.open:
            return "BULLISH"

        if current.close < current.open:
            return "BEARISH"

        return "NONE"

    @staticmethod
    def _insufficient() -> dict:
        return {
            "direction": "NEUTRAL",

            "bos": False,
            "choch": False,
            "liquidity": False,
            "fvg": False,
            "order_block": False,
            "displacement": False,

            "bos_events": [],
            "choch_events": [],

            "liquidity_direction": "NONE",
            "fvg_direction": "NONE",
            "order_block_direction": "NONE",
            "displacement_direction": "NONE",

            "bullish_count": 0,
            "bearish_count": 0,

            "score": 0,
            "conflicting": False,
            "confirmed": False,
            "execution_ready": False,

            "reasons": [
                "Insufficient closed candle data."
            ],
        }
