"""
GTI AI
Execution Router Tests
"""

from unittest.mock import patch

from execution.execution_router import ExecutionRouter


def test_paper_mode():
    order = {"entry": 2000.0}

    with patch("config.settings.Settings.TRADING_MODE", "PAPER"):
        with patch(
            "execution.execution_router.PaperTradingEngine.update"
        ) as paper:

            paper.return_value = {
                "status": "OPEN",
            }

            result = ExecutionRouter.execute(order)

            assert result["success"] is True
            assert result["mode"] == "PAPER"

            paper.assert_called_once()


def test_demo_mode():
    order = {"entry": 2000.0}

    with patch("config.settings.Settings.TRADING_MODE", "DEMO"):
        with patch(
            "execution.execution_router.MT5TradeExecutor.execute"
        ) as mt5:

            mt5.return_value = {
                "success": True,
                "ticket": 123456,
            }

            result = ExecutionRouter.execute(order)

            assert result["success"] is True
            assert result["mode"] == "DEMO"

            mt5.assert_called_once()


def test_live_mode():
    order = {"entry": 2000.0}

    with patch("config.settings.Settings.TRADING_MODE", "LIVE"):
        with patch(
            "execution.execution_router.MT5TradeExecutor.execute"
        ) as mt5:

            mt5.return_value = {
                "success": True,
                "ticket": 654321,
            }

            result = ExecutionRouter.execute(order)

            assert result["success"] is True
            assert result["mode"] == "LIVE"

            mt5.assert_called_once()


def test_invalid_mode():
    order = {"entry": 2000.0}

    with patch("config.settings.Settings.TRADING_MODE", "UNKNOWN"):

        result = ExecutionRouter.execute(order)

        assert result["success"] is False
        assert result["mode"] == "UNKNOWN"
