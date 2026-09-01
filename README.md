# mini-quant-backtester

A lightweight quantitative research dashboard for testing technical trading strategies on historical market data.  
It implements a vectorized backtesting engine, risk-adjusted performance metrics, transaction cost simulation, and interactive Streamlit visualizations.

## Why this project
这是一个**学习向**项目：用尽量少的复杂金融概念，演示完整工程链路：
- 数据获取（yfinance）
- 策略实现（SMA / RSI）
- 向量化回测（含手续费/滑点）
- 绩效指标与可视化
- 规则驱动的本地学习总结

## MVP Features
1. 输入股票代码、日期范围、初始资金、手续费、滑点  
2. 下载 OHLCV 历史数据  
3. 四种策略：SMA Crossover、EMA Crossover、RSI Mean Reversion、Bollinger Mean Reversion  
4. 指标：总收益、年化收益、Sharpe、最大回撤、胜率、交易次数  
5. 图表：价格+买卖点、权益曲线、回撤曲线、交易日志  
6. 本地学习总结：根据回测指标给出规则驱动的复盘提示  

## Project Structure
```
.
├── app.py
├── quant_dashboard
│   ├── backtest.py
│   ├── config.py
│   ├── data.py
│   ├── metrics.py
│   ├── report.py
│   └── strategies.py
├── tests
│   ├── test_backtest.py
│   └── test_metrics.py
└── docs
    ├── sdd-spec.md
    └── sdd-design.md
```

## Quick Start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Run Tests
```bash
pytest -q
```

## SDD Docs
- `docs/sdd-spec.md`: 需求规格（范围、验收标准）
- `docs/sdd-design.md`: 设计说明（分层、数据流、回测逻辑）
