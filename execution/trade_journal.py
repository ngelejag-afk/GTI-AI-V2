from __future__ import annotations
"""
GTI AI
Trade Journal
Version 1.0
"""


import csv
from pathlib import Path
from datetime import datetime


class TradeJournal:
    """
    Records completed trades into a CSV journal.
    """

    FILE = Path("trade_journal.csv")

    HEADERS = [
        "timestamp",
        "symbol",
        "decision",
        "entry",
        "exit",
        "stop_loss",
        "take_profit",
        "lot_size",
        "profit",
        "pips",
        "confidence",
        "result",
    ]

    @classmethod
    def _create_file(cls) -> None:
        """
        Create the journal file if it does not exist.
        """

        if cls.FILE.exists():
            return

        with cls.FILE.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.writer(file)
            writer.writerow(cls.HEADERS)

    @classmethod
    def record(
        cls,
        symbol: str,
        decision: str,
        entry: float,
        exit_price: float,
        stop_loss: float,
        take_profit: float,
        lot_size: float,
        profit: float,
        pips: float,
        confidence: float,
        result: str,
    ) -> None:
        """
        Record one completed trade.
        """

        cls._create_file()

        with cls.FILE.open(
            "a",
            newline="",
            encoding="utf-8",
        ) as file:
            writer = csv.writer(file)

            writer.writerow(
                [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    symbol,
                    decision,
                    round(entry, 5),
                    round(exit_price, 5),
                    round(stop_loss, 5),
                    round(take_profit, 5),
                    round(lot_size, 2),
                    round(profit, 2),
                    round(pips, 1),
                    confidence,
                    result,
                ]
            )

    @classmethod
    def total_trades(cls) -> int:
        """
        Return total recorded trades.
        """

        if not cls.FILE.exists():
            return 0

        with cls.FILE.open(
            "r",
            encoding="utf-8",
        ) as file:
            return max(sum(1 for _ in file) - 1, 0)
