import time
import random

# --- MT5 Compatibility Layer for Mobile Testing ---
try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    print("[SYSTEM NOTICE] MetaTrader5 package not found. Running in SIMULATION MODE.")

# --- Configuration Constants ---
MAGIC_NUMBER = 202608
SLIPPAGE_POINTS = 20

# --- Simulated MT5 Engine ---
class MockMT5:
    class SymbolInfoTick:
        def __init__(self, ask, bid):
            self.ask = ask
            self.bid = bid

    class Position:
        def __init__(self, ticket, pos_type, price_open, sl, tp):
            self.ticket = ticket
            self.type = pos_type
            self.price_open = price_open
            self.sl = sl
            self.tp = tp

    POSITION_TYPE_BUY = 0
    POSITION_TYPE_SELL = 1
    TRADE_ACTION_DEAL = 1
    TRADE_ACTION_SLTP = 6
    ORDER_TYPE_BUY = 0
    ORDER_TYPE_SELL = 1
    ORDER_TIME_GTC = 0
    ORDER_FILLING_IOC = 1
    TRADE_RETCODE_DONE = 10009

    def __init__(self):
        self.mock_positions = [
            self.Position(ticket=10101, pos_type=0, price_open=2415.00, sl=2405.00, tp=2435.00)
        ]

    def initialize(self):
        return True

    def symbol_select(self, symbol, enable):
        return True

    def symbol_info_tick(self, symbol):
        # Simulated live XAUUSD price
        base_price = 2420.50 + round(random.uniform(-0.5, 0.5), 2)
        return self.SymbolInfoTick(ask=base_price + 0.30, bid=base_price)

    def order_send(self, request):
        class Result:
            def __init__(self):
                self.retcode = 10009
                self.order = random.randint(100000, 999999)
                self.deal = random.randint(100000, 999999)
                self.price = request.get("price", 2420.50)
                self.volume = request.get("volume", 0.01)
                self.comment = "Success"
        return Result()

    def positions_get(self, symbol=None):
        return self.mock_positions

    def last_error(self):
        return (1, "No error")

if not MT5_AVAILABLE:
    mt5 = MockMT5()

# --- MT5 Core Functions ---
def initialize_mt5() -> bool:
    if not mt5.initialize():
        print(f"[MT5 Execution Error] Initialization failed: {mt5.last_error()}")
        return False
    return True

def execute_trade(signal_data: dict) -> dict:
    if not initialize_mt5():
        return {"success": False, "reason": "MT5 Terminal Connection Failed"}

    action_str = signal_data.get("action")
    symbol = signal_data.get("symbol", "XAUUSD")
    lot_size = signal_data.get("lot_size", 0.01)
    sl = signal_data.get("sl", 0.0)
    tp = signal_data.get("tp", 0.0)

    if not mt5.symbol_select(symbol, True):
        return {"success": False, "reason": f"Symbol {symbol} not available"}

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return {"success": False, "reason": f"Failed to retrieve price for {symbol}"}

    if action_str == "BUY":
        order_type = mt5.ORDER_TYPE_BUY
        execution_price = tick.ask
    elif action_str == "SELL":
        order_type = mt5.ORDER_TYPE_SELL
        execution_price = tick.bid
    else:
        return {"success": False, "reason": f"Invalid action: {action_str}"}

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot_size,
        "type": order_type,
        "price": execution_price,
        "sl": sl,
        "tp": tp,
        "deviation": SLIPPAGE_POINTS,
        "magic": MAGIC_NUMBER,
        "comment": "GTI-AI Automated Signal",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }

    result = mt5.order_send(request)
    if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
        return {"success": False, "reason": "Order execution rejected"}

    return {
        "success": True,
        "order_id": result.order,
        "deal_id": result.deal,
        "execution_price": result.price,
        "volume": result.volume
    }

# --- Position Management ---
def apply_breakeven(symbol: str = "XAUUSD", offset_usd: float = 0.50):
    positions = mt5.positions_get(symbol=symbol)
    if not positions:
        return

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return

    for pos in positions:
        open_price = pos.price_open
        current_sl = pos.sl
        target_be_sl = round(open_price + offset_usd, 2)

        if pos.type == mt5.POSITION_TYPE_BUY and tick.bid - open_price >= abs(open_price - current_sl):
            if current_sl < target_be_sl:
                print(f"[Break-Even] BUY #{pos.ticket} SL updated -> {target_be_sl}")
                pos.sl = target_be_sl

def apply_trailing_stop(symbol: str = "XAUUSD", trailing_step_usd: float = 2.0, activation_pips_usd: float = 3.0):
    positions = mt5.positions_get(symbol=symbol)
    if not positions:
        return

    tick = mt5.symbol_info_tick(symbol)
    if tick is None:
        return

    for pos in positions:
        if pos.type == mt5.POSITION_TYPE_BUY:
            profit = tick.bid - pos.price_open
            if profit >= activation_pips_usd:
                new_sl = round(tick.bid - trailing_step_usd, 2)
                if pos.sl == 0.0 or new_sl > pos.sl:
                    print(f"[Trailing Stop] BUY #{pos.ticket} SL updated -> {new_sl} (Bid: {tick.bid})")
                    pos.sl = new_sl

# --- Risk & Signal Helper Logic ---
def calculate_trade_levels(action, current_price, atr, balance, risk_pct=1.0, rr_ratio=2.0):
    risk_amount = balance * (risk_pct / 100.0)
    sl_distance = atr * 1.5
    lot_size = max(0.01, round(risk_amount / (sl_distance * 100), 2))

    if action == "BUY":
        sl = round(current_price - sl_distance, 2)
        tp = round(current_price + (sl_distance * rr_ratio), 2)
    else:
        sl = round(current_price + sl_distance, 2)
        tp = round(current_price - (sl_distance * rr_ratio), 2)

    return {"lot_size": lot_size, "sl": sl, "tp": tp, "risk_usd": round(risk_amount, 2)}

def send_signal_notification(signal_data):
    print(f"[Broadcaster] Signal broadcasted for {signal_data.get('action')} {signal_data.get('symbol')}")

# --- Main Automation Loop ---
def run_automated_trading_pipeline():
    last_sent_action = None
    print("\n--- Starting GTI-AI-V2 Automated Trading Pipeline ---\n")

    loop_count = 0
    while loop_count < 3:  # Runs 3 cycles for verification
        apply_breakeven(symbol="XAUUSD", offset_usd=0.50)
        apply_trailing_stop(symbol="XAUUSD", trailing_step_usd=2.0, activation_pips_usd=3.0)

        current_balance = 10000.0
        tick = mt5.symbol_info_tick("XAUUSD")

        market_data = {
            "action": "BUY",
            "symbol": "XAUUSD",
            "price": tick.ask if tick else 2420.50,
            "confidence": 85.0,
            "atr": 3.40
        }

        current_action = market_data.get("action")
        confidence = market_data.get("confidence", 0)

        if confidence >= 75 and current_action in ["BUY", "SELL"]:
            if current_action != last_sent_action:
                risk_levels = calculate_trade_levels(
                    action=current_action,
                    current_price=market_data["price"],
                    atr=market_data["atr"],
                    balance=current_balance,
                    risk_pct=1.0,
                    rr_ratio=2.0
                )

                full_signal = {**market_data, **risk_levels}
                print(f"[Execution Engine] Placing {current_action} order for {full_signal['lot_size']} Lots...")

                exec_result = execute_trade(full_signal)
                if exec_result.get("success"):
                    print(f"[Execution Success] Order ID #{exec_result['order_id']} opened at ${exec_result['execution_price']}")
                
                send_signal_notification(full_signal)
                last_sent_action = current_action
            else:
                print(f"[Pipeline Status] Signal '{current_action}' active. Monitoring open position...")

        loop_count += 1
        time.sleep(3)

    print("\n[Pipeline] Simulation cycle completed successfully.")

if __name__ == "__main__":
    run_automated_trading_pipeline()

