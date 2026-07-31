"""
GTI AI
System Configuration
Version 2.0
"""


class Settings:
    """
    Global system settings.
    """

    SYMBOL = "XAUUSD"

    TIMEFRAME = "M15"

    RISK_PERCENT = 1.0

    ATR_MULTIPLIER = 1.5

    DEFAULT_BALANCE = 10000.0

    # Trading modes:
    # PAPER -> Internal paper trading engine
    # DEMO  -> MetaTrader 5 demo account
    # LIVE  -> MetaTrader 5 live account
    TRADING_MODE = "PAPER"

    MAGIC_NUMBER = 2026001

    JOURNAL_FILE = "trade_history.csv"

    DEFAULT_LOT_SIZE = 0.01

    MAX_SLIPPAGE = 20
