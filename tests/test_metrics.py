import pandas as pd

from quant_dashboard.config import BacktestConfig
from quant_dashboard.metrics import calculate_metrics


def test_calculate_metrics_core_fields():
    idx = pd.date_range("2024-01-01", periods=4, freq="D")
    frame = pd.DataFrame(
        {
            "equity": [10000, 10100, 9900, 10200],
            "drawdown": [0.0, 0.0, -0.0198, 0.0],
            "strategy_return": [0.0, 0.01, -0.0198, 0.0303],
        },
        index=idx,
    )
    trades = pd.DataFrame({"is_win": [True, False, True]})
    cfg = BacktestConfig(initial_capital=10000)

    metrics = calculate_metrics(frame=frame, trades=trades, config=cfg)

    assert "sharpe" in metrics
    assert metrics["trade_count"] == 3
    assert 0 <= metrics["win_rate"] <= 1

