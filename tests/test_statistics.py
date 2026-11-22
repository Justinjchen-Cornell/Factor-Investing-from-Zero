"""统计量模块测试：NW 方差-协方差矩阵与 statsmodels 交叉验证、GRS 统计量。"""
import numpy as np
import pandas as pd

from factor_zero.statistics import newey_west_vcov, nw_t_stat, ts_regression, grs_test


def test_newey_west_matches_statsmodels():
    rng = np.random.default_rng(7)
    T, K = 300, 2
    X = rng.normal(size=(T, K))
    X[:, 0] = 1.0  # 截距
    # 制造自相关残差
    eps = np.zeros(T)
    for t in range(1, T):
        eps[t] = 0.6 * eps[t - 1] + rng.normal(0, 1)
    import statsmodels.api as sm
    m = sm.OLS(eps + X @ np.array([1.0, 2.0]), X).fit(cov_type="HAC", cov_kwds={"maxlags": 4})
    # 两边必须用同一个 OLS 残差（而非生成的 eps）——与 statsmodels 对齐
    ols_resid = np.asarray(m.resid)
    vcov = newey_west_vcov(X, ols_resid, max_lag=4)
    np.testing.assert_allclose(vcov, m.cov_params(), rtol=1e-6)


def test_nw_t_stat_manual():
    rng = np.random.default_rng(11)
    series = pd.Series(rng.normal(0.001, 0.02, size=120))
    t, se = nw_t_stat(series)
    assert np.isclose(se, np.sqrt(newey_west_vcov(np.ones((120, 1)), series - series.mean())[0, 0]))


def test_ts_regression_recovers_betas():
    rng = np.random.default_rng(3)
    T = 500
    f = rng.normal(0.001, 0.02, size=(T, 2))
    true_beta = np.array([1.2, -0.5])
    r = 0.001 + f @ true_beta + rng.normal(0, 0.01, size=T)
    alpha, betas, resid = ts_regression(r, pd.DataFrame(f, columns=["F1", "F2"]))
    assert abs(alpha - 0.001) < 0.001
    np.testing.assert_allclose(betas, true_beta, atol=0.05)


def test_grs_no_alpha_not_rejected():
    rng = np.random.default_rng(5)
    T, N, K = 240, 6, 3
    f = rng.normal(0.001, 0.02, size=(T, K))
    beta = rng.uniform(0.5, 1.5, size=(N, K))
    resid = rng.normal(0, 0.01, size=(T, N))
    r = f @ beta.T + resid  # (T, N)，真实 alpha = 0
    alphas, resid_stack = [], np.zeros((T, N))
    for i in range(N):
        a, _, e = ts_regression(r[:, i], pd.DataFrame(f, columns=[f"F{k}" for k in range(K)]))
        alphas.append(a)
        resid_stack[:, i] = e
    F, p = grs_test(np.array(alphas), resid_stack, f)
    assert p > 0.05, f"alpha=0 时 GRS 不应拒绝，p={p:.4f}"


def test_factor_summary_keys_and_t_sign():
    from factor_zero.statistics import factor_summary
    rng = np.random.default_rng(0)
    r = pd.Series(rng.normal(0.005, 0.02, size=120))
    s = factor_summary(r)
    for key in ["mean_ann", "vol_ann", "sharpe", "t_stat", "max_drawdown", "win_rate"]:
        assert key in s
    assert s["t_stat"] > 0
    assert -1 <= s["max_drawdown"] <= 0
