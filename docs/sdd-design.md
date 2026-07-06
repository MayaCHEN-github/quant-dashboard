# SDD Design (MVP)

## 1. Architecture
采用简化分层设计，便于学习与扩展：

- `data.py`: 下载与清洗 OHLCV
- `strategies.py`: 信号生成（SMA / RSI）
- `backtest.py`: 向量化回测引擎 + 交易日志
- `metrics.py`: 绩效指标
- `report.py`: AI Review Prompt 与学习型总结
- `app.py`: Streamlit UI + Plotly 图表

## 2. Data Flow
用户参数 -> 拉取行情 -> 生成信号 -> 回测 -> 计算指标 -> 图表与日志 -> AI Prompt。

## 3. Backtest Logic
1. `position = signal.shift(1)`：次日执行，减少未来函数问题。  
2. `strategy_return = position * asset_return - turnover * (commission + slippage)`。  
3. `equity = initial_capital * cumprod(1 + strategy_return)`。  
4. `drawdown = equity / rolling_max(equity) - 1`。  

## 4. Trade Log Rules
- 0 -> 1 记为开仓
- 1 -> 0 记为平仓
- 记录 entry/exit 日期、价格、毛收益、净收益、是否盈利

## 5. Test Strategy
- 指标计算返回合理值（含 trade_count / win_rate）。
- 在同一价格序列下，加入成本后权益低于无成本场景。

