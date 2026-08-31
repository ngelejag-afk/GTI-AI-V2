
"""
Tests for the current SMC Analyzer architecture.
"""

from types import SimpleNamespace

from analysis.smc_analyzer import SMCAnalyzer
from strategy.domain.models import Candle


def make_candles(count=6):
    return [
        Candle(
            timestamp=i,
            open=100.0,
            high=101.0,
            low=99.0,
            close=100.0,
        )
        for i in range(count)
    ]


def test_smc_insufficient_candles():
    result = SMCAnalyzer.analyze(make_candles(4))

    assert result["confirmed"] is False
    assert result["execution_ready"] is False
    assert result["score"] == 0


def test_smc_no_directional_structure(monkeypatch):
    monkeypatch.setattr(
        "analysis.smc_analyzer.StructurePipeline.analyze",
        lambda candles: SimpleNamespace(
            bos=[],
            choch=[],
        ),
    )

    monkeypatch.setattr(
        SMCAnalyzer,
        "_liquidity_sweep",
        staticmethod(lambda candles: "NONE"),
    )
    monkeypatch.setattr(
        SMCAnalyzer,
        "_fvg",
        staticmethod(lambda candles: "NONE"),
    )
    monkeypatch.setattr(
        SMCAnalyzer,
        "_order_block",
        staticmethod(lambda candles: "NONE"),
    )
    monkeypatch.setattr(
        SMCAnalyzer,
        "_displacement",
        staticmethod(lambda candles: "NONE"),
    )

    result = SMCAnalyzer.analyze(make_candles())

    assert result["direction"] == "NEUTRAL"
    assert result["bos"] is False
    assert result["choch"] is False
    assert result["liquidity"] is False
    assert result["fvg"] is False
    assert result["order_block"] is False
    assert result["displacement"] is False
    assert result["score"] == 0
    assert result["conflicting"] is False
    assert result["confirmed"] is False
    assert result["execution_ready"] is False


def test_smc_conflicting_direction_is_rejected(monkeypatch):
    monkeypatch.setattr(
        "analysis.smc_analyzer.StructurePipeline.analyze",
        lambda candles: SimpleNamespace(
            bos=[
                SimpleNamespace(direction="BULLISH")
            ],
            choch=[
                SimpleNamespace(to_regime="BEARISH")
            ],
        ),
    )

    monkeypatch.setattr(
        SMCAnalyzer,
        "_liquidity_sweep",
        staticmethod(lambda candles: "BULLISH"),
    )
    monkeypatch.setattr(
        SMCAnalyzer,
        "_fvg",
        staticmethod(lambda candles: "BULLISH"),
    )
    monkeypatch.setattr(
        SMCAnalyzer,
        "_order_block",
        staticmethod(lambda candles: "BULLISH"),
    )
    monkeypatch.setattr(
        SMCAnalyzer,
        "_displacement",
        staticmethod(lambda candles: "BULLISH"),
    )

    result = SMCAnalyzer.analyze(make_candles())

    assert result["direction"] == "BUY"
    assert result["conflicting"] is True
    assert result["confirmed"] is False
    assert result["execution_ready"] is False
    assert "CONFLICTING SMC DIRECTION" in result["reasons"]


def test_smc_full_confluence_confirms(monkeypatch):
    monkeypatch.setattr(
        "analysis.smc_analyzer.StructurePipeline.analyze",
        lambda candles: SimpleNamespace(
            bos=[
                SimpleNamespace(direction="BULLISH")
            ],
            choch=[
                SimpleNamespace(to_regime="BULLISH")
            ],
        ),
    )

    monkeypatch.setattr(
        SMCAnalyzer,
        "_liquidity_sweep",
        staticmethod(lambda candles: "BULLISH"),
    )
    monkeypatch.setattr(
        SMCAnalyzer,
        "_fvg",
        staticmethod(lambda candles: "BULLISH"),
    )
    monkeypatch.setattr(
        SMCAnalyzer,
        "_order_block",
        staticmethod(lambda candles: "BULLISH"),
    )
    monkeypatch.setattr(
        SMCAnalyzer,
        "_displacement",
        staticmethod(lambda candles: "BULLISH"),
    )

    result = SMCAnalyzer.analyze(make_candles())

    assert result["direction"] == "BUY"

    assert result["bos"] is True
    assert result["choch"] is True
    assert result["liquidity"] is True
    assert result["fvg"] is True
    assert result["order_block"] is True
    assert result["displacement"] is True

    assert result["score"] == 100
    assert result["conflicting"] is False
    assert result["confirmed"] is True
    assert result["execution_ready"] is True


def test_smc_bearish_full_confluence_confirms(monkeypatch):
    monkeypatch.setattr(
        "analysis.smc_analyzer.StructurePipeline.analyze",
        lambda candles: SimpleNamespace(
            bos=[
                SimpleNamespace(direction="BEARISH")
            ],
            choch=[
                SimpleNamespace(to_regime="BEARISH")
            ],
        ),
    )

    monkeypatch.setattr(
        SMCAnalyzer,
        "_liquidity_sweep",
        staticmethod(lambda candles: "BEARISH"),
    )
    monkeypatch.setattr(
        SMCAnalyzer,
        "_fvg",
        staticmethod(lambda candles: "BEARISH"),
    )
    monkeypatch.setattr(
        SMCAnalyzer,
        "_order_block",
        staticmethod(lambda candles: "BEARISH"),
    )
    monkeypatch.setattr(
        SMCAnalyzer,
        "_displacement",
        staticmethod(lambda candles: "BEARISH"),
    )

    result = SMCAnalyzer.analyze(make_candles())

    assert result["direction"] == "SELL"
    assert result["score"] == 100
    assert result["conflicting"] is False
    assert result["confirmed"] is True
    assert result["execution_ready"] is True
