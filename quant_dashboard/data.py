from __future__ import annotations

import pandas as pd
import yfinance as yf


def fetch_ohlcv(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Download OHLCV data from Yahoo Finance."""
    data = yf.download(
        ticker,
        start=start,
        end=end,
        auto_adjust=False,
        progress=False,
    )
    if data.empty:
        return data

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    expected_cols = ["Open", "High", "Low", "Close", "Volume"]
    missing = [col for col in expected_cols if col not in data.columns]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")

    data = data[expected_cols].copy()
    data.index = pd.to_datetime(data.index).tz_localize(None)
    return data.dropna()

