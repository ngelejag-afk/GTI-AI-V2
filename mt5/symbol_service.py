try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None

class SymbolService:
    def __init__(self, *args, **kwargs):
        self.connected = mt5 is not None

    @classmethod
    def get(cls, symbol="XAUUSD", *args, **kwargs):
        return cls.get_symbol_info(symbol, *args, **kwargs)

    @classmethod
    def get_symbol_info(cls, symbol="XAUUSD", *args, **kwargs):
        return {
            "symbol": symbol,
            "bid": 2650.0,
            "ask": 2650.5,
            "digits": 2,
            "point": 0.01,
            "spread": 50
        }
    # Fallback/Mock object kwa ajili ya cloud/Linux deployment (Render)
    class DummyMT5:
        def initialize(self):
            return True

        def shutdown(self):
            pass

    mt5 = DummyMT5()
