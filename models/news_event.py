"""
GTI AI
News Event Model
Version 1.0
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class NewsEvent:
    """
    Represents one economic news event.
    """

    title: str
    currency: str
    impact: str

    event_time: datetime

    actual: str = ""
    forecast: str = ""
    previous: str = ""
