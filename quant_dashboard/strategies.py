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


def ema_crossover_signal(close: pd.Series, fast_span: int, slow_span: int) -> pd.Series:
    """Long-only EMA crossover signal: 1 when fast EMA > slow EMA else 0."""
    if fast_span >= slow_span:
        raise ValueError("fast_span must be smaller than slow_span")

    fast_ema = close.ewm(span=fast_span, adjust=False, min_periods=fast_span).mean()
    slow_ema = close.ewm(span=slow_span, adjust=False, min_periods=slow_span).mean()
    signal = (fast_ema > slow_ema).astype(float).fillna(0.0)
    return signal.rename("signal")


def bollinger_mean_reversion_signal(
    close: pd.Series,
    window: int = 20,
    num_std: float = 2.0,
) -> pd.Series:
    """Long-only Bollinger mean-reversion signal.

    Rules:
    - Enter long when close < lower band.
    - Exit to flat when close > middle band.
    """
    if window < 2:
        raise ValueError("window must be at least 2")
    if num_std <= 0:
        raise ValueError("num_std must be positive")

    middle = close.rolling(window=window, min_periods=window).mean()
    std = close.rolling(window=window, min_periods=window).std(ddof=0)
    lower = middle - (num_std * std)

    signal = pd.Series(0.0, index=close.index, name="signal")
    in_position = False
    for idx in close.index:
        price = close.loc[idx]
        if not in_position and price < lower.loc[idx]:
            in_position = True
        elif in_position and price > middle.loc[idx]:
            in_position = False
        signal.loc[idx] = 1.0 if in_position else 0.0
    return signal

