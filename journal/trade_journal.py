"""
GTI AI
Trade Journal
Version 1.0
"""

from __future__ import annotations

import csv
from pathlib import Path


class TradeJournal:
    """
    Stores trade history in a CSV file.
    """

    def __init__(self, filename: str = "trade_history.csv"):
        self.file = Path(filename)

        if not self.file.exists():
            with self.file.open("w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([
                    "timestamp",
                    "symbol",
                    "action",
                    "entry",
                    "stop_loss",
                    "take_profit",
                    "volume",
                    "status",
                ])

    def log(self, trade: dict) -> None:
        """
        Save a trade to the journal.
        """

        with self.file.open("a", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)

            writer.writerow([
                trade.get("timestamp", ""),
                trade.get("symbol", ""),
                trade.get("action", ""),
                trade.get("entry", ""),
                trade.get("stop_loss", ""),
                trade.get("take_profit", ""),
                trade.get("volume", ""),
                trade.get("status", ""),
            ])
