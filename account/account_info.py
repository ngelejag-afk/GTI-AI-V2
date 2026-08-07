class AccountInfo:
    def __init__(self, *args, **kwargs):
        self.balance = 10000.0
        self.equity = 10000.0
        self.margin = 0.0
        self.free_margin = 10000.0

    def __getitem__(self, item):
        return getattr(self, item, None)

    def get_account_info(self, *args, **kwargs):
        return {
            "balance": self.balance,
            "equity": self.equity,
            "free_margin": self.free_margin,
            "margin": self.margin
        }

    @classmethod
    def get(cls, *args, **kwargs):
        return cls()
