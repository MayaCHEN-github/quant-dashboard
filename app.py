from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from quant_dashboard.backtest import run_backtest
from quant_dashboard.config import BacktestConfig
from quant_dashboard.data import fetch_ohlcv
from quant_dashboard.help_texts import SECTION_HELP, STRATEGY_EXPLAINERS, TERM_HELP
from quant_dashboard.metrics import calculate_buy_and_hold_metrics, calculate_metrics
from quant_dashboard.report import build_learning_review
from quant_dashboard.strategies import (
    bollinger_mean_reversion_signal,
    ema_crossover_signal,
    rsi_mean_reversion_signal,
    sma_crossover_signal,
)


TRADE_COLUMN_LABELS = {
    "entry_date": "买入日期",
    "entry_price": "买入价格",
    "exit_date": "卖出日期",
    "exit_price": "卖出价格",
    "gross_return": "毛收益率（未扣手续费和滑点）",
    "net_return": "净收益率（已扣手续费和滑点）",
    "holding_days": "持有天数",
    "is_win": "是否盈利",
}


@st.cache_data(show_spinner=False)
def load_data(ticker: str, start: str, end: str) -> pd.DataFrame:
    return fetch_ohlcv(ticker=ticker, start=start, end=end)


def build_price_chart(frame: pd.DataFrame, trades: pd.DataFrame, ticker: str) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=frame.index,
            y=frame["Close"],
            mode="lines",
            name=f"{ticker} 收盘价",
            line={"width": 2},
        )
    )

    if not trades.empty:
        entry_points = trades.set_index("entry_date")
        exit_points = trades.set_index("exit_date")
        fig.add_trace(
            go.Scatter(
                x=entry_points.index,
                y=entry_points["entry_price"],
                mode="markers",
                name="买入",
                marker={"symbol": "triangle-up", "size": 10},
            )
        )
        fig.add_trace(
            go.Scatter(
                x=exit_points.index,
                y=exit_points["exit_price"],
                mode="markers",
                name="卖出",
                marker={"symbol": "triangle-down", "size": 10},
            )
        )

    fig.update_layout(title="价格与买卖点", xaxis_title="日期", yaxis_title="价格")
    return fig


def build_equity_chart(frame: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=frame.index, y=frame["equity"], mode="lines", name="总资产"))
    fig.update_layout(title="权益曲线", xaxis_title="日期", yaxis_title="总资产")
    return fig


def build_drawdown_chart(frame: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=frame.index, y=frame["drawdown"], mode="lines", name="回撤"))
    fig.update_layout(title="回撤曲线", xaxis_title="日期", yaxis_title="回撤")
    return fig


def main() -> None:
    st.set_page_config(page_title="Mini Quant Research Dashboard", layout="wide")
    st.title("Mini Quant Research Dashboard")
    st.caption(
        "这是一个用历史数据练习量化交易思路的小工具。",
        help=SECTION_HELP["页面简介"],
    )
    st.caption("学习向：yfinance + pandas + Streamlit + Plotly")

    with st.sidebar:
        st.header("参数设置")
        ticker = (
            st.text_input("股票代码", value="AAPL", help=TERM_HELP["股票代码"]).upper().strip()
        )
        default_start = date.today() - timedelta(days=365 * 2)
        start_date = st.date_input("开始日期", value=default_start, help=TERM_HELP["开始日期"])
        end_date = st.date_input("结束日期", value=date.today(), help=TERM_HELP["结束日期"])

        initial_capital = st.number_input(
            "初始资金",
            min_value=1000.0,
            value=10_000.0,
            step=1000.0,
            help=TERM_HELP["初始资金"],
        )
        commission_pct = st.number_input(
            "手续费 (%)",
            min_value=0.0,
            value=0.10,
            step=0.01,
            help=TERM_HELP["手续费"],
        )
        slippage_pct = st.number_input(
            "滑点 (%)",
            min_value=0.0,
            value=0.10,
            step=0.01,
            help=TERM_HELP["滑点"],
        )

        strategy_name = st.selectbox(
            "策略",
            options=[
                "SMA Crossover",
                "EMA Crossover",
                "RSI Mean Reversion",
                "Bollinger Mean Reversion",
            ],
            help=TERM_HELP["策略"],
        )
        run_clicked = st.button("运行回测", type="primary", help=TERM_HELP["回测"])

    if not run_clicked:
        st.info("请在左侧设置参数后点击“运行回测”。")
        return

    if start_date >= end_date:
        st.error("开始日期必须早于结束日期。")
        return

    try:
        data = load_data(ticker=ticker, start=str(start_date), end=str(end_date))
    except Exception as exc:
        st.error(f"下载数据失败: {exc}")
        return

    if data.empty:
        st.warning("未获取到数据，请检查股票代码或日期范围。")
        return

    strategy_params: dict
    if strategy_name == "SMA Crossover":
        col1, col2 = st.columns(2)
        with col1:
            fast_window = st.number_input(
                "SMA 快线窗口",
                min_value=2,
                value=20,
                step=1,
                help=TERM_HELP["SMA 快线窗口"],
            )
        with col2:
            slow_window = st.number_input(
                "SMA 慢线窗口",
                min_value=3,
                value=50,
                step=1,
                help=TERM_HELP["SMA 慢线窗口"],
            )
        strategy_params = {"fast_window": int(fast_window), "slow_window": int(slow_window)}
        signal = sma_crossover_signal(
            close=data["Close"],
            fast_window=strategy_params["fast_window"],
            slow_window=strategy_params["slow_window"],
        )
    elif strategy_name == "EMA Crossover":
        col1, col2 = st.columns(2)
        with col1:
            fast_span = st.number_input(
                "EMA 快线周期",
                min_value=2,
                value=12,
                step=1,
            )
        with col2:
            slow_span = st.number_input(
                "EMA 慢线周期",
                min_value=3,
                value=26,
                step=1,
            )
        strategy_params = {"fast_span": int(fast_span), "slow_span": int(slow_span)}
        signal = ema_crossover_signal(
            close=data["Close"],
            fast_span=strategy_params["fast_span"],
            slow_span=strategy_params["slow_span"],
        )
    elif strategy_name == "RSI Mean Reversion":
        col1, col2, col3 = st.columns(3)
        with col1:
            period = st.number_input(
                "RSI 周期",
                min_value=2,
                value=14,
                step=1,
                help=TERM_HELP["RSI 周期"],
            )
        with col2:
            lower = st.number_input(
                "RSI 下限",
                min_value=1.0,
                max_value=49.0,
                value=30.0,
                step=1.0,
                help=TERM_HELP["RSI 下限"],
            )
        with col3:
            upper = st.number_input(
                "RSI 上限",
                min_value=51.0,
                max_value=99.0,
                value=70.0,
                step=1.0,
                help=TERM_HELP["RSI 上限"],
            )
        strategy_params = {"period": int(period), "lower": float(lower), "upper": float(upper)}
        signal = rsi_mean_reversion_signal(
            close=data["Close"],
            period=strategy_params["period"],
            lower=strategy_params["lower"],
            upper=strategy_params["upper"],
        )
    else:
        col1, col2 = st.columns(2)
        with col1:
            window = st.number_input(
                "布林带窗口",
                min_value=5,
                value=20,
                step=1,
            )
        with col2:
            num_std = st.number_input(
                "布林带倍数",
                min_value=0.5,
                value=2.0,
                step=0.1,
            )
        strategy_params = {"window": int(window), "num_std": float(num_std)}
        signal = bollinger_mean_reversion_signal(
            close=data["Close"],
            window=strategy_params["window"],
            num_std=strategy_params["num_std"],
        )

    config = BacktestConfig(
        initial_capital=float(initial_capital),
        commission_rate=float(commission_pct) / 100,
        slippage_rate=float(slippage_pct) / 100,
    )

    result = run_backtest(data=data, signal=signal, config=config)
    metrics = calculate_metrics(frame=result.frame, trades=result.trades, config=config)
    benchmark = calculate_buy_and_hold_metrics(close=data["Close"], config=config)

    st.subheader("核心指标", help=SECTION_HELP["核心指标"])
    m1, m2, m3 = st.columns(3)
    m4, m5, m6 = st.columns(3)
    m1.metric("总收益", f"{metrics['total_return']:.2%}", help=TERM_HELP["总收益"])
    m2.metric("年化收益", f"{metrics['annual_return']:.2%}", help=TERM_HELP["年化收益"])
    m3.metric("Sharpe", f"{metrics['sharpe']:.2f}", help=TERM_HELP["Sharpe"])
    m4.metric("最大回撤", f"{metrics['max_drawdown']:.2%}", help=TERM_HELP["最大回撤"])
    m5.metric("胜率", f"{metrics['win_rate']:.2%}", help=TERM_HELP["胜率"])
    m6.metric("交易次数", str(metrics["trade_count"]), help=TERM_HELP["交易次数"])

    st.caption(
        f"对照 Buy & Hold：总收益 {benchmark['total_return']:.2%}，"
        f"年化收益 {benchmark['annual_return']:.2%}",
        help=TERM_HELP["Buy & Hold"],
    )

    st.subheader("价格与买卖点", help=SECTION_HELP["价格与买卖点"])
    st.plotly_chart(build_price_chart(result.frame, result.trades, ticker=ticker), use_container_width=True)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("权益曲线", help=SECTION_HELP["权益曲线"])
        st.plotly_chart(build_equity_chart(result.frame), use_container_width=True)
    with c2:
        st.subheader("回撤曲线", help=SECTION_HELP["回撤曲线"])
        st.plotly_chart(build_drawdown_chart(result.frame), use_container_width=True)

    st.subheader("交易日志", help=SECTION_HELP["交易日志"])
    if result.trades.empty:
        st.info(f"没有完整的开平仓交易。{TERM_HELP['开平仓交易']}")
    else:
        st.caption(
            "每一行是一笔“买入到卖出”的完整模拟交易，不是实时交易记录。"
            "交易条数由历史区间、策略规则和参数共同决定。"
        )
        trade_view = result.trades.copy()
        trade_view["holding_days"] = (
            pd.to_datetime(trade_view["exit_date"]) - pd.to_datetime(trade_view["entry_date"])
        ).dt.days
        trade_view["gross_return"] = trade_view["gross_return"].map(lambda x: f"{x:.2%}")
        trade_view["net_return"] = trade_view["net_return"].map(lambda x: f"{x:.2%}")
        trade_view["is_win"] = trade_view["is_win"].map(lambda x: "是" if bool(x) else "否")
        trade_view = trade_view.rename(columns=TRADE_COLUMN_LABELS)
        st.dataframe(trade_view, use_container_width=True)

    st.markdown("**本地学习总结：**")
    st.markdown(build_learning_review(metrics))

    st.subheader("策略小白说明", help=SECTION_HELP["策略小白说明"])
    st.markdown(STRATEGY_EXPLAINERS.get(strategy_name, ""))


if __name__ == "__main__":
    main()

