"""
GTI AI
Main Pipeline
Version 1.0
"""

from mt5.mt5_connector import MT5Connector


def main() -> None:
    connector = MT5Connector()

    if not connector.connect():
        print("❌ Failed to connect to MetaTrader 5.")
        return

    print("✅ Connected to MetaTrader 5")

    if connector.is_connected():
        print("✅ MT5 terminal detected")

    connector.disconnect()
    print("✅ MT5 connection closed")


if __name__ == "__main__":
    main()
