from __future__ import annotations

import math

import pandas as pd

from quant_dashboard.config import BacktestConfig


def _safe_annualized_return(total_return: float, periods: int, annualization_factor: int) -> float:
    if periods <= 0:
        return 0.0
    return (1 + total_return) ** (annualization_factor / periods) - 1


def _safe_sharpe(returns: pd.Series, annualization_factor: int) -> float:
    std = returns.std(ddof=0)
    if std == 0 or math.isnan(std):
        return 0.0
    return (returns.mean() / std) * math.sqrt(annualization_factor)


def calculate_metrics(frame: pd.DataFrame, trades: pd.DataFrame, config: BacktestConfig) -> dict:
    equity = frame["equity"]
    drawdown = frame["drawdown"]
    returns = frame["strategy_return"]

    total_return = (equity.iloc[-1] / config.initial_capital) - 1
    annual_return = _safe_annualized_return(
        total_return=total_return,
        periods=len(frame),
        annualization_factor=config.annualization_factor,
    )
    sharpe = _safe_sharpe(returns=returns, annualization_factor=config.annualization_factor)
    max_drawdown = drawdown.min()

    closed_trade_count = len(trades)
    win_rate = float(trades["is_win"].mean()) if closed_trade_count else 0.0

    return {
        "total_return": total_return,
        "annual_return": annual_return,
        "sharpe": sharpe,
        "max_drawdown": max_drawdown,
        "win_rate": win_rate,
        "trade_count": closed_trade_count,
    }


def calculate_buy_and_hold_metrics(close: pd.Series, config: BacktestConfig) -> dict:
    if close.empty:
        return {"total_return": 0.0, "annual_return": 0.0}

    total_return = (close.iloc[-1] / close.iloc[0]) - 1
    annual_return = _safe_annualized_return(
        total_return=total_return,
        periods=len(close),
        annualization_factor=config.annualization_factor,
    )
    return {"total_return": total_return, "annual_return": annual_return}

