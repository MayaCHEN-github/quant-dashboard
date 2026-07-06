from dataclasses import dataclass


@dataclass
class BacktestConfig:
    initial_capital: float = 10_000.0
    commission_rate: float = 0.001
    slippage_rate: float = 0.001
    annualization_factor: int = 252

