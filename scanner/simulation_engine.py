"""
GTI AI
Simulation Engine
Version 1.0
"""


class SimulationEngine:
    """
    Generates sample market signals for testing.
    """

    _signals = [
        {
            "decision": "BUY",
            "confidence": 91,
            "market_bias": "Bullish",
            "entry": 3350.50,
        },
        {
            "decision": "SELL",
            "confidence": 87,
            "market_bias": "Bearish",
            "entry": 3342.80,
        },
        {
            "decision": "WAIT",
            "confidence": 48,
            "market_bias": "Neutral",
            "entry": 3346.10,
        },
    ]

    _index = 0

    @classmethod
    def next_signal(cls) -> dict:
        signal = cls._signals[cls._index]
        cls._index = (cls._index + 1) % len(cls._signals)
        return signal.copy()
