from strategy.bos_engine import BOSEngine
from strategy.choch_engine import CHOCHEngine
from strategy.liquidity_sweep_engine import LiquiditySweepEngine
from strategy.fvg_engine import FVGEngine
from strategy.order_block_engine import OrderBlockEngine
from strategy.smc_engine import SMCEngine


class SMCAnalyzer:
    def __init__(self):
        self.bos = BOSEngine()
        self.choch = CHOCHEngine()
        self.liquidity = LiquiditySweepEngine()
        self.fvg = FVGEngine()
        self.order_block = OrderBlockEngine()
        self.engine = SMCEngine()

    def analyze(self, candles):
        return self.engine.analyze(
            bos=self.bos.bullish(candles),
            choch=self.choch.bullish(candles),
            liquidity=self.liquidity.buy_side(candles),
            fvg=self.fvg.bullish(candles),
            order_block=self.order_block.bullish(candles),
        )
