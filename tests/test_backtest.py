import pandas as pd

from quant_dashboard.backtest import run_backtest
from quant_dashboard.config import BacktestConfig


def test_backtest_costs_reduce_equity():
    idx = pd.date_range("2024-01-01", periods=5, freq="D")
    data = pd.DataFrame({"Close": [100, 102, 101, 103, 104]}, index=idx)
    signal = pd.Series([0, 1, 1, 0, 0], index=idx)

    no_cost = BacktestConfig(initial_capital=10000, commission_rate=0.0, slippage_rate=0.0)
    with_cost = BacktestConfig(initial_capital=10000, commission_rate=0.002, slippage_rate=0.002)

    result_no_cost = run_backtest(data, signal, no_cost)
    result_with_cost = run_backtest(data, signal, with_cost)

    assert result_with_cost.equity_curve.iloc[-1] < result_no_cost.equity_curve.iloc[-1]


def test_backtest_generates_trade_log():
    idx = pd.date_range("2024-01-01", periods=6, freq="D")
    data = pd.DataFrame({"Close": [100, 101, 102, 101, 100, 103]}, index=idx)
    signal = pd.Series([0, 1, 1, 0, 1, 0], index=idx)
    cfg = BacktestConfig()

    result = run_backtest(data, signal, cfg)

    assert len(result.trades) == 2
    assert set(["entry_date", "exit_date", "net_return", "is_win"]).issubset(result.trades.columns)

