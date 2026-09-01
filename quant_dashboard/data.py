from __future__ import annotations

import os
from io import StringIO
from contextlib import contextmanager
from urllib import parse, request

import pandas as pd
import yfinance as yf


PROXY_ENV_KEYS = [
    "http_proxy",
    "https_proxy",
    "all_proxy",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
]


@contextmanager
def _proxy_disabled_env():
    backup = {key: os.environ.get(key) for key in PROXY_ENV_KEYS}
    try:
        for key in PROXY_ENV_KEYS:
            os.environ.pop(key, None)
        yield
    finally:
        for key, value in backup.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _download_ohlcv(ticker: str, start: str, end: str) -> pd.DataFrame:
    return yf.download(
        ticker,
        start=start,
        end=end,
        auto_adjust=False,
        progress=False,
    )


def _to_stooq_symbol(ticker: str) -> str | None:
    symbol = ticker.strip().upper()
    if not symbol:
        return None
    if symbol.startswith("^"):
        return None

    if symbol.endswith(".SS") or symbol.endswith(".SZ"):
        # ponytail: Stooq does not use .SS/.SZ, it expects .CN for China A shares.
        return f"{symbol.split('.')[0]}.CN".lower()

    if "." not in symbol:
        return f"{symbol}.US".lower()
    return symbol.lower()


def _download_stooq_ohlcv(ticker: str, start: str, end: str, timeout_seconds: int = 20) -> pd.DataFrame:
    stooq_symbol = _to_stooq_symbol(ticker)
    if not stooq_symbol:
        return pd.DataFrame()

    start_fmt = pd.to_datetime(start).strftime("%Y%m%d")
    end_fmt = pd.to_datetime(end).strftime("%Y%m%d")
    query = parse.urlencode({"s": stooq_symbol, "i": "d", "d1": start_fmt, "d2": end_fmt})
    url = f"https://stooq.com/q/d/l/?{query}"

    with request.urlopen(url, timeout=timeout_seconds) as response:
        raw_csv = response.read().decode("utf-8", errors="ignore")

    if not raw_csv.strip() or "No data" in raw_csv:
        return pd.DataFrame()

    data = pd.read_csv(StringIO(raw_csv))
    if data.empty:
        return data
    if "Date" not in data.columns:
        return pd.DataFrame()
    return data.set_index("Date")


def _normalize_ohlcv(data: pd.DataFrame) -> pd.DataFrame:
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    expected_cols = ["Open", "High", "Low", "Close", "Volume"]
    missing = [col for col in expected_cols if col not in data.columns]
    if missing:
        raise ValueError(f"Missing expected columns: {missing}")

    data = data[expected_cols].copy()
    data.index = pd.to_datetime(data.index).tz_localize(None)
    data = data.sort_index()
    return data.dropna()


def fetch_ohlcv(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Download OHLCV data from Yahoo Finance with Stooq fallback."""
    first_error: Exception | None = None
    try:
        data = _download_ohlcv(ticker=ticker, start=start, end=end)
    except Exception as exc:
        first_error = exc
        data = pd.DataFrame()

    # ponytail: if current proxy blocks Yahoo (common 403 tunnel error), retry once without proxy env.
    if data.empty:
        try:
            with _proxy_disabled_env():
                data = _download_ohlcv(ticker=ticker, start=start, end=end)
        except Exception as exc:
            if first_error is None:
                first_error = exc

    fallback_error: Exception | None = None
    # ponytail: fallback to Stooq when Yahoo is blocked (proxy 403 / DNS failures).
    if data.empty:
        try:
            data = _download_stooq_ohlcv(ticker=ticker, start=start, end=end)
        except Exception as exc:
            fallback_error = exc
            data = pd.DataFrame()

    if data.empty:
        try:
            with _proxy_disabled_env():
                data = _download_stooq_ohlcv(ticker=ticker, start=start, end=end)
        except Exception as exc:
            if fallback_error is None:
                fallback_error = exc

    if data.empty:
        yahoo_err = f"Yahoo错误：{first_error}" if first_error else "Yahoo错误：无详细信息"
        stooq_err = f"Stooq错误：{fallback_error}" if fallback_error else "Stooq错误：无详细信息"
        raise ValueError(
            "主数据源（Yahoo）与备用数据源（Stooq）均返回空数据。请检查："
            "1) 股票代码是否正确（如美股 AAPL、港股 0700.HK、A 股 600519.SS）；"
            "2) 日期区间是否有交易日；"
            "3) 当前网络/代理/DNS是否允许访问数据源。"
            "若遇到代理 403 或 DNS 失败，请在系统/终端里关闭代理变量后重试。"
            f" {yahoo_err}；{stooq_err}"
        )

    return _normalize_ohlcv(data)

