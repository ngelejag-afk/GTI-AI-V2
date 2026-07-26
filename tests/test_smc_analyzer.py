"""
Tests for SMC Analyzer.
"""

from analysis.smc_analyzer import SMCAnalyzer


class MockEngine:
    def __init__(self, value: bool):
        self.value = value

    def bullish(self, candles):
        return self.value

    def buy_side(self, candles):
        return self.value


def test_smc_all_signals_confirmed(monkeypatch):
    monkeypatch.setattr(
        "analysis.smc_analyzer.BOSEngine",
        lambda: MockEngine(True),
    )
    monkeypatch.setattr(
        "analysis.smc_analyzer.CHOCHEngine",
        lambda: MockEngine(True),
    )
    monkeypatch.setattr(
        "analysis.smc_analyzer.LiquiditySweepEngine",
        lambda: MockEngine(True),
    )
    monkeypatch.setattr(
        "analysis.smc_analyzer.FVGEngine",
        lambda: MockEngine(True),
    )
    monkeypatch.setattr(
        "analysis.smc_analyzer.OrderBlockEngine",
        lambda: MockEngine(True),
    )

    result = SMCAnalyzer.analyze([])

    assert result["confirmed"] is True
    assert result["score"] == 100


def test_smc_no_signals(monkeypatch):
    monkeypatch.setattr(
        "analysis.smc_analyzer.BOSEngine",
        lambda: MockEngine(False),
    )
    monkeypatch.setattr(
        "analysis.smc_analyzer.CHOCHEngine",
        lambda: MockEngine(False),
    )
    monkeypatch.setattr(
        "analysis.smc_analyzer.LiquiditySweepEngine",
        lambda: MockEngine(False),
    )
    monkeypatch.setattr(
        "analysis.smc_analyzer.FVGEngine",
        lambda: MockEngine(False),
    )
    monkeypatch.setattr(
        "analysis.smc_analyzer.OrderBlockEngine",
        lambda: MockEngine(False),
    )

    result = SMCAnalyzer.analyze([])

    assert result["confirmed"] is False
    assert result["score"] == 0
