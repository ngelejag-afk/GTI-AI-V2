try:
    import MetaTrader5 as mt5
except ImportError:
    # Fallback/Mock object kwa ajili ya cloud/Linux deployment (Render)
    class DummyMT5:
        def initialize(self):
            return True

        def shutdown(self):
            pass

    mt5 = DummyMT5()
