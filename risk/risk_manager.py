"""
GTI AI
Risk Manager
Version 1.0
"""


class RiskManager:
    """
    Calculates trading risk and position sizing.
    """

    @staticmethod
    def risk_amount(balance: float, risk_percent: float) -> float:
        """
        Returns the amount to risk.
        """
        return balance * (risk_percent / 100)

    @staticmethod
    def risk_reward(entry: float, stop_loss: float, take_profit: float) -> float:
        """
        Calculates Risk:Reward ratio.
        """
        risk = abs(entry - stop_loss)
        reward = abs(take_profit - entry)

        if risk == 0:
            return 0.0

        return round(reward / risk, 2)

    @staticmethod
    def position_size(
        balance: float,
        risk_percent: float,
        stop_loss_points: float,
        value_per_point: float,
    ) -> float:
        """
        Calculates suggested position size.
        """
        if stop_loss_points <= 0 or value_per_point <= 0:
            return 0.0

        risk = RiskManager.risk_amount(balance, risk_percent)

        return round(
            risk / (stop_loss_points * value_per_point),
            2,
        )
