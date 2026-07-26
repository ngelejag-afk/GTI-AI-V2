"""
Integration tests for main_ai.py
"""

import main_ai


class MockConnector:
    def connect(self):
        return True

    def disconnect(self):
        return None


def test_main_wait_flow(monkeypatch):
    monkeypatch.setattr(
        main_ai,
        "MT5Connector",
        lambda: MockConnector(),
    )

    monkeypatch.setattr(
        main_ai.EconomicCalendar,
        "trading_allowed",
        staticmethod(lambda: True),
    )

    monkeypatch.setattr(
        main_ai.MultiTimeframeReader,
        "read",
        staticmethod(lambda **kwargs: {}),
    )

    monkeypatch.setattr(
        main_ai.MultiTimeframeAnalyzer,
        "analyze",
        staticmethod(lambda market: {}),
    )

    monkeypatch.setattr(
        main_ai.ConfluenceAnalyzer,
        "analyze",
        staticmethod(
            lambda analysis: {
                "decision": "WAIT",
                "confidence": 50,
            }
        ),
    )

    main_ai.main()
