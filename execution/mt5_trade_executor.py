from __future__ import annotations
"""
GTI AI
MetaTrader 5 Trade Executor
Version 1.0
"""


try:
    import MetaTrader5 as mt5
except ModuleNotFoundError:
    mt5 = None

from mt5.mt5_connector import MT5Connector


class MT5TradeExecutor:
    """
    Executes market orders on MetaTrader 5.
    """

    DEFAULT_DEVIATION = 20
    MAGIC_NUMBER = 20260731

    def __init__(self) -> None:
        self.connector = MT5Connector()

    def execute(self, order: dict) -> dict:
        """
        Execute a BUY or SELL market order.

        Returns:
            {
                "success": bool,
                "ticket": int | None,
                "message": str,
                "retcode": int | None,
            }
        """

        if mt5 is None:
            return {
                "success": False,
                "ticket": None,
                "message": "MetaTrader5 package is not installed.",
                "retcode": None,
            }

        if not self.connector.connect():
            return {
                "success": False,
                "ticket": None,
                "message": "Unable to connect to MetaTrader 5.",
                "retcode": None,
            }

        symbol = order.get("symbol", "XAUUSD")

        if not mt5.symbol_select(symbol, True):
            return {
                "success": False,
                "ticket": None,
                "message": f"Unable to select symbol: {symbol}",
                "retcode": None,
            }

        symbol_info = mt5.symbol_info(symbol)

        if symbol_info is None:
            return {
                "success": False,
                "ticket": None,
                "message": f"Symbol not found: {symbol}",
                "retcode": None,
            }

        tick = mt5.symbol_info_tick(symbol)

        if tick is None:
            return {
                "success": False,
                "ticket": None,
                "message": "Unable to read market price.",
                "retcode": None,
            }

        decision = order.get("decision")

        if decision == "BUY":
            order_type = mt5.ORDER_TYPE_BUY
            price = tick.ask
        elif decision == "SELL":
            order_type = mt5.ORDER_TYPE_SELL
            price = tick.bid
        else:
            return {
                "success": False,
                "ticket": None,
                "message": "Invalid trade decision.",
                "retcode": None,
            }

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": float(order.get("lot_size", 0.01)),
            "type": order_type,
            "price": price,
            "sl": float(order.get("stop_loss", 0.0)),
            "tp": float(order.get("take_profit", 0.0)),
            "deviation": self.DEFAULT_DEVIATION,
            "magic": self.MAGIC_NUMBER,
            "comment": "GTI AI Demo",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_FOK,
        }

        result = mt5.order_send(request)

        if result is None:
            return {
                "success": False,
                "ticket": None,
                "message": str(mt5.last_error()),
                "retcode": None,
            }

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            return {
                "success": False,
                "ticket": None,
                "message": result.comment,
                "retcode": result.retcode,
            }

        return {
            "success": True,
            "ticket": result.order,
            "message": "Trade executed successfully.",
            "retcode": result.retcode,
        }
