"""第7章组合工具测试：暴露、优化、风险分解、风格回归、Smart Beta。"""
import numpy as np
import pandas as pd

from factor_zero.portfolio import (
    FACTOR_ORDER,
    build_style_exposures,
    portfolio_risk,
    min_variance_weights,
    max_sharpe_weights,
    style_regression,
    smart_beta_weights,
)


def _panel():
    idx = pd.date_range("2020-01-31", periods=3, freq="ME")
    cols = ["A", "B", "C", "D"]
    rng = np.random.default_rng(0)
    def frame():
        return pd.DataFrame(rng.normal(size=(3, 4)), index=idx, columns=cols)
    return {
        "ret": frame(), "size": frame(), "bm": frame(), "momentum": frame(),
        "roe": frame(), "investment": frame(), "turnover": frame(),
    }


def test_build_style_exposures_columns():
    panel = _panel()
    B = build_style_exposures(panel, panel["ret"].index[-1])
    assert list(B.columns) == FACTOR_ORDER
    assert B.shape[0] == 4


def test_min_variance_weights_sum_and_long_only():
    rng = np.random.default_rng(1)
    A = rng.normal(size=(5, 5))
    cov = pd.DataFrame(A @ A.T + np.eye(5) * 0.1, columns=list("abcde"), index=list("abcde"))
    w = min_variance_weights(cov)
    assert abs(w.sum() - 1) < 1e-6
    assert (w >= -1e-8).all()
    eq = np.ones(5) / 5
    assert w @ cov.to_numpy() @ w <= eq @ cov.to_numpy() @ eq + 1e-8


def test_max_sharpe_weights_sum():
    rng = np.random.default_rng(2)
    A = rng.normal(size=(4, 4))
    cov = pd.DataFrame(A @ A.T + np.eye(4) * 0.1, columns=list("abcd"), index=list("abcd"))
    mu = pd.Series([0.1, 0.08, 0.06, 0.04], index=list("abcd"))
    w = max_sharpe_weights(mu, cov)
    assert abs(w.sum() - 1) < 1e-6


def test_portfolio_risk_contributions_sum():
    rng = np.random.default_rng(3)
    B = pd.DataFrame(rng.normal(size=(4, 3)), columns=FACTOR_ORDER[:3], index=list("abcd"))
    fcov = pd.DataFrame(np.eye(3) * 0.04, columns=B.columns, index=B.columns)
    spec = pd.Series([0.01] * 4, index=B.index)
    w = pd.Series([0.25] * 4, index=B.index)
    res = portfolio_risk(w, B, fcov, spec)
    assert res["total_vol"] > 0
    assert abs(res["factor_contrib"].sum() + res["specific_contrib"] - res["total_vol"]) < 1e-8


def test_style_regression_recovers_betas():
    rng = np.random.default_rng(4)
    T = 300
    f = pd.DataFrame(rng.normal(size=(T, 2)), columns=["F1", "F2"])
    true = np.array([1.2, -0.5])
    r = 0.001 + f.to_numpy() @ true + rng.normal(0, 0.01, T)
    alpha, betas, r2, resid = style_regression(pd.Series(r), f)
    np.testing.assert_allclose(betas.to_numpy(), true, atol=0.05)
    assert r2 > 0.8


def test_smart_beta_weights_sum():
    scores = pd.Series([1.0, 2.0, 3.0], index=list("abc"))
    for method in ["equal", "score"]:
        w = smart_beta_weights(scores, method=method)
        assert abs(w.sum() - 1) < 1e-9
    w = smart_beta_weights(scores, method="risk", risk=pd.Series([0.1, 0.2, 0.4], index=list("abc")))
    assert abs(w.sum() - 1) < 1e-9
