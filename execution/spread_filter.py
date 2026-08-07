from __future__ import annotations

"""
GTI AI
Spread Filter
Version 1.0
"""



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
        """
        Validate the current spread.
        """

        spread = float(spread)

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
