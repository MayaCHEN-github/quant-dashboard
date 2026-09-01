from quant_dashboard.report import build_learning_review


def test_build_learning_review_flags_weak_metrics():
    text = build_learning_review(
        {"sharpe": 0.2, "max_drawdown": -0.25, "win_rate": 0.3}
    )
    assert "Sharpe 偏低" in text
    assert "最大回撤较大" in text
    assert "胜率不高" in text
