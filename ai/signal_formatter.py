"""
GTI AI
Signal Formatter
Version 1.0
"""


class SignalFormatter:
    """
    Formats trading signals into a readable message.
    """

    @staticmethod
    def format(
        symbol: str,
        action: str,
        entry: float,
        stop_loss: float,
        take_profit: dict,
        confidence: int,
    ) -> str:
        """
        Returns a formatted trading signal.
        """
        return f"""
==============================
🚀 GTI AI V2 SIGNAL
==============================

PAIR
{symbol}

ACTION
{action}

ENTRY
{entry:.2f}

STOP LOSS
{stop_loss:.2f}

TAKE PROFIT 1
{take_profit["tp1"]:.2f}

TAKE PROFIT 2
{take_profit["tp2"]:.2f}

TAKE PROFIT 3
{take_profit["tp3"]:.2f}

CONFIDENCE
{confidence}%

==============================
"""
