from __future__ import annotations
"""
GTI AI
Spread Filter
Version 1.0
"""

from config.settings import Settings

class SpreadFilter:
    """
    Validates whether the current spread is acceptable.
    """

    DEFAULT_MAX_SPREAD = 30

    @staticmethod
    def validate(
        spread: int | float,
        max_spread: int = DEFAULT_MAX_SPREAD,
    ) -> dict:
        spread = float(spread)

        if getattr(Settings, "IGNORE_SPREAD_CHECK", False):
            return {
                "valid": True,
                "spread": spread,
                "max_spread": max_spread,
                "reason": "Spread check bypassed by override setting.",
            }

        valid = spread <= max_spread

        return {
            "valid": valid,
            "spread": spread,
            "max_spread": max_spread,
            "reason": (
                "Spread acceptable."
                if valid
                else "Spread exceeds maximum allowed."
            ),
        }
