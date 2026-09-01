import pandas as pd
import pytest

from quant_dashboard.strategies import (
    bollinger_mean_reversion_signal,
    ema_crossover_signal,
    sma_crossover_signal,
)


def _sample_close() -> pd.Series:
    idx = pd.date_range("2024-01-01", periods=40, freq="D")
    values = [100 + (i % 7) * 0.8 + (i * 0.2) for i in range(40)]
    return pd.Series(values, index=idx)


def test_ema_signal_shape_and_values():
    close = _sample_close()
    signal = ema_crossover_signal(close, fast_span=6, slow_span=12)
    assert signal.index.equals(close.index)
    assert set(signal.unique()).issubset({0.0, 1.0})


def test_bollinger_signal_shape_and_values():
    close = _sample_close()
    signal = bollinger_mean_reversion_signal(close, window=20, num_std=1.5)
    assert signal.index.equals(close.index)
    assert set(signal.unique()).issubset({0.0, 1.0})


def test_ema_and_sma_window_validation():
    close = _sample_close()
    with pytest.raises(ValueError):
        ema_crossover_signal(close, fast_span=20, slow_span=10)
    with pytest.raises(ValueError):
        sma_crossover_signal(close, fast_window=20, slow_window=10)
