import pandas as pd
import pytest

from quant_dashboard.data import fetch_ohlcv


def _valid_frame() -> pd.DataFrame:
    idx = pd.date_range("2024-01-01", periods=3, freq="D")
    return pd.DataFrame(
        {
            "Open": [1.0, 2.0, 3.0],
            "High": [1.2, 2.2, 3.2],
            "Low": [0.8, 1.8, 2.8],
            "Close": [1.1, 2.1, 3.1],
            "Volume": [100, 120, 130],
        },
        index=idx,
    )


def test_fetch_ohlcv_retry_without_proxy(monkeypatch: pytest.MonkeyPatch):
    calls = {"count": 0}

    def fake_download(*args, **kwargs):
        calls["count"] += 1
        return pd.DataFrame() if calls["count"] == 1 else _valid_frame()

    monkeypatch.setattr("quant_dashboard.data.yf.download", fake_download)

    result = fetch_ohlcv("AAPL", "2024-01-01", "2024-01-10")
    assert not result.empty
    assert calls["count"] == 2


def test_fetch_ohlcv_fallback_to_stooq_when_yahoo_empty(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("quant_dashboard.data.yf.download", lambda *args, **kwargs: pd.DataFrame())
    monkeypatch.setattr("quant_dashboard.data._download_stooq_ohlcv", lambda *args, **kwargs: _valid_frame())

    result = fetch_ohlcv("0700.HK", "2024-01-01", "2024-01-10")
    assert not result.empty
    assert list(result.columns) == ["Open", "High", "Low", "Close", "Volume"]


def test_fetch_ohlcv_raises_clear_error_when_all_sources_empty(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("quant_dashboard.data.yf.download", lambda *args, **kwargs: pd.DataFrame())
    monkeypatch.setattr("quant_dashboard.data._download_stooq_ohlcv", lambda *args, **kwargs: pd.DataFrame())

    with pytest.raises(ValueError, match="备用数据源"):
        fetch_ohlcv("AAPL", "2024-01-01", "2024-01-10")
