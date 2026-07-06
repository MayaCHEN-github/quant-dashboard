# SDD Spec (MVP)

## 1. Goal
构建一个**学习向**的迷你量化研究面板，用最少功能展示数据、策略、回测、指标、可视化与 AI 辅助复盘的完整链路。

## 2. In-Scope (今天完成)
1. 输入：股票代码、日期范围、初始资金、手续费、滑点。  
2. 数据：通过 yfinance 下载 OHLCV。  
3. 策略：SMA Crossover、RSI Mean Reversion（long-only）。  
4. 回测：考虑手续费 + 滑点。  
5. 指标：总收益、年化收益、Sharpe、最大回撤、胜率、交易次数。  
6. 可视化：价格+买卖点、权益曲线、回撤曲线、交易日志。  
7. AI Review：自动生成结构化 Prompt，便于贴给任意 LLM 生成复盘。

## 3. Out-of-Scope (本次不做)
- 实盘交易接口
- 高频/分钟级数据
- 参数优化网格搜索
- 多资产组合管理
- 复杂风控模块（如 VaR、仓位动态管理）

## 4. Acceptance Criteria
- 可以运行 `streamlit run app.py` 打开面板。
- 两个策略均可运行并输出指标与图表。
- 成本参数变化会影响回测结果。
- 能生成可复制的 AI Review Prompt。

