from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from quant_dashboard.config import BacktestConfig


@dataclass
class BacktestResult:
    equity_curve: pd.Series
    drawdown_curve: pd.Series
    returns: pd.Series
    position: pd.Series
    trades: pd.DataFrame
    frame: pd.DataFrame


def _build_trade_log(
    close: pd.Series,
    signal: pd.Series,
    commission_rate: float,
    slippage_rate: float,
) -> pd.DataFrame:
    records: list[dict] = []
    prev = 0.0
    entry_date = None
    entry_price = None

    for dt, cur in signal.items():
        if prev == 0.0 and cur == 1.0:
            entry_date = dt
            entry_price = close.loc[dt] * (1 + slippage_rate)
        elif prev == 1.0 and cur == 0.0 and entry_date is not None and entry_price is not None:
            exit_price = close.loc[dt] * (1 - slippage_rate)
            gross_ret = (exit_price / entry_price) - 1
            net_ret = gross_ret - 2 * commission_rate
            records.append(
                {
                    "entry_date": entry_date,
                    "exit_date": dt,
                    "entry_price": round(float(entry_price), 4),
                    "exit_price": round(float(exit_price), 4),
                    "gross_return": gross_ret,
                    "net_return": net_ret,
                    "is_win": net_ret > 0,
                }
            )
            entry_date = None
            entry_price = None
        prev = cur

    return pd.DataFrame(records)


def run_backtest(data: pd.DataFrame, signal: pd.Series, config: BacktestConfig) -> BacktestResult:
    close = data["Close"].copy()
    signal = signal.reindex(close.index).fillna(0.0).astype(float)

    position = signal.shift(1).fillna(0.0)
    close_returns = close.pct_change().fillna(0.0)
    trades_turnover = signal.diff().abs().fillna(signal.abs())

    total_cost_rate = config.commission_rate + config.slippage_rate
    strategy_returns = (position * close_returns) - (trades_turnover * total_cost_rate)

    equity_curve = config.initial_capital * (1 + strategy_returns).cumprod()
    drawdown_curve = (equity_curve / equity_curve.cummax()) - 1

    frame = pd.DataFrame(
        {
            "Close": close,
            "signal": signal,
            "position": position,
            "asset_return": close_returns,
            "strategy_return": strategy_returns,
            "equity": equity_curve,
            "drawdown": drawdown_curve,
        }
    )

    trades = _build_trade_log(
        close=close,
        signal=signal,
        commission_rate=config.commission_rate,
        slippage_rate=config.slippage_rate,
    )
    return BacktestResult(
        equity_curve=equity_curve,
        drawdown_curve=drawdown_curve,
        returns=strategy_returns,
        position=position,
        trades=trades,
        frame=frame,
    )

