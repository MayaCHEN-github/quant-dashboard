from __future__ import annotations


def build_learning_review(metrics: dict) -> str:
    scorecard = []
    if metrics["sharpe"] >= 1:
        scorecard.append("风险调整后收益（Sharpe）表现尚可。")
    else:
        scorecard.append("Sharpe 偏低，说明收益波动比不理想。")

    if metrics["max_drawdown"] < -0.2:
        scorecard.append("最大回撤较大，风险控制需要加强。")
    else:
        scorecard.append("最大回撤处于可学习阶段可接受范围。")

    if metrics["win_rate"] >= 0.5:
        scorecard.append("胜率超过 50%，信号方向性有一定价值。")
    else:
        scorecard.append("胜率不高，建议优化入场过滤条件。")

    scorecard.append("建议下一步做参数敏感性测试，并增加止损规则。")
    return "\n".join(f"- {line}" for line in scorecard)
