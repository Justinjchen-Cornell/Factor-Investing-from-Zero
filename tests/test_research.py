"""第6章研究工具测试：p-hacking、发表衰减、过拟合、情绪信号。"""
import numpy as np
import pandas as pd

from factor_zero.research import (
    simulate_random_factors,
    p_hacking_summary,
    publication_decay_experiment,
    polynomial_train_test_mse,
    sentiment_signal,
)


def test_p_hacking_summary_counts():
    factors = simulate_random_factors(n_factors=2000, n_periods=120, seed=1)
    summary = p_hacking_summary(factors["t_stat"])
    assert list(summary["threshold"]) == [2.0, 3.0, 3.4]
    assert (summary["count"] >= 0).all()
    assert summary.loc[summary["threshold"] == 2.0, "count"].iloc[0] >= summary.loc[summary["threshold"] == 3.4, "count"].iloc[0]


def test_publication_decay_shape():
    df = publication_decay_experiment(n_simulations=50, seed=2)
    assert len(df) == 50
    assert set(["in_sample", "full_sample", "decay"]).issubset(df.columns)
    assert df["in_sample"].notna().all()


def test_polynomial_overfitting():
    df = polynomial_train_test_mse(degrees=(1, 9), n=200, noise=0.3, seed=42)
    high = df[df["degree"] == 9].iloc[0]
    assert high["train_mse"] < high["test_mse"]


def test_sentiment_signal_shape():
    idx = pd.date_range("2020-01-31", periods=30, freq="ME")
    ret = pd.DataFrame({"A": np.linspace(-0.05, 0.05, 30)}, index=idx)
    turnover = pd.DataFrame({"A": np.linspace(0.1, 1.0, 30)}, index=idx)
    panel = {"ret": ret, "turnover": turnover}
    s = sentiment_signal(panel)
    assert s.shape == ret.shape
    assert s.iloc[1:].notna().all().all()
