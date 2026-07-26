"""
Tests for Confluence Analyzer.
"""

from analysis.confluence_analyzer import ConfluenceAnalyzer


def test_buy_decision():
    analysis = {
        "M5": {"trend": "BUY"},
        "M15": {"trend": "BUY"},
        "H1": {"trend": "BUY"},
        "H4": {"trend": "SELL"},
    }

    result = ConfluenceAnalyzer.analyze(analysis)

    assert result["decision"] == "BUY"
    assert result["bullish_votes"] == 3
    assert result["bearish_votes"] == 1


def test_sell_decision():
    analysis = {
        "M5": {"trend": "SELL"},
        "M15": {"trend": "SELL"},
        "H1": {"trend": "BUY"},
        "H4": {"trend": "SELL"},
    }

    result = ConfluenceAnalyzer.analyze(analysis)

    assert result["decision"] == "SELL"
    assert result["bullish_votes"] == 1
    assert result["bearish_votes"] == 3


def test_wait_decision():
    analysis = {
        "M5": {"trend": "BUY"},
        "M15": {"trend": "SELL"},
        "H1": {"trend": "BUY"},
        "H4": {"trend": "SELL"},
    }

    result = ConfluenceAnalyzer.analyze(analysis)

    assert result["decision"] == "WAIT"
    assert result["bullish_votes"] == 2
    assert result["bearish_votes"] == 2
