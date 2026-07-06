from __future__ import annotations

import numpy as np
import pandas as pd


def sma_crossover_signal(close: pd.Series, fast_window: int, slow_window: int) -> pd.Series:
    """Long-only SMA crossover signal: 1 when fast SMA > slow SMA else 0."""
    if fast_window >= slow_window:
        raise ValueError("fast_window must be smaller than slow_window")

    fast_sma = close.rolling(window=fast_window, min_periods=fast_window).mean()
    slow_sma = close.rolling(window=slow_window, min_periods=slow_window).mean()
    signal = (fast_sma > slow_sma).astype(float).fillna(0.0)
    return signal.rename("signal")


def compute_rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gains = delta.clip(lower=0)
    losses = -delta.clip(upper=0)

    avg_gain = gains.rolling(window=period, min_periods=period).mean()
    avg_loss = losses.rolling(window=period, min_periods=period).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return rsi.fillna(50.0)


def rsi_mean_reversion_signal(
    close: pd.Series,
    period: int = 14,
    lower: float = 30,
    upper: float = 70,
) -> pd.Series:
    """Long-only RSI mean reversion signal.

    Rules:
    - Enter long when RSI < lower.
    - Exit to flat when RSI > upper.
    """
    if lower >= upper:
        raise ValueError("lower must be smaller than upper")

    rsi = compute_rsi(close=close, period=period)
    signal = pd.Series(0.0, index=close.index, name="signal")
    in_position = False

    for idx in close.index:
        if not in_position and rsi.loc[idx] < lower:
            in_position = True
        elif in_position and rsi.loc[idx] > upper:
            in_position = False
        signal.loc[idx] = 1.0 if in_position else 0.0

    return signal

