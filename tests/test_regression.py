"""回归模块测试：FM 回归必须能在合成数据上恢复预设的因子溢价。"""
import numpy as np
import pandas as pd

from factor_zero.data_sim import simulate_cross_section
from factor_zero.regression import (
    time_series_betas,
    cross_sectional_lambda,
    fama_macbeth,
)


def test_fm_recovers_true_lambda_noiseless():
    """无噪声极限：FM 应精确恢复预设 lambda（误差 < 1e-8）。"""
    sim = simulate_cross_section(
        n_assets=100, t_periods=120, n_factors=2, noise=0.0, seed=42
    )
    lam_hat, lam_t, se, t = fama_macbeth(sim["ret"], sim["char"])
    np.testing.assert_allclose(lam_hat[1:], sim["lambda"], atol=1e-8)


def test_fm_recovers_true_lambda_with_noise():
    """有噪声：恢复的 lambda 应在 3 倍标准误之内（统计一致性）。"""
    sim = simulate_cross_section(
        n_assets=200, t_periods=240, n_factors=3, noise=0.01, seed=7
    )
    lam_hat, lam_t, se, t = fama_macbeth(sim["ret"], sim["char"])
    for k in range(sim["n_factors"]):
        assert abs(lam_hat[1 + k] - sim["lambda"][k]) < 3 * se[1 + k], (
            f"因子{k} 未在 3se 内恢复 lambda"
        )


def test_fm_identifies_unpriced_factor():
    """预设 lambda=0 的因子，FM 估计值应接近 0。"""
    lam_true = np.array([0.006, 0.0])
    sim = simulate_cross_section(
        n_assets=120, t_periods=180, n_factors=2, noise=0.0,
        seed=11, lambda_values=lam_true,
    )
    lam_hat, lam_t, se, t = fama_macbeth(sim["ret"], sim["char"])
    assert abs(lam_hat[2]) < 1e-8


def test_cross_sectional_lambda_shape():
    sim = simulate_cross_section(n_assets=50, t_periods=60, n_factors=2, seed=1)
    betas = pd.DataFrame(
        sim["beta"], index=sim["ret"].columns, columns=["F1", "F2"]
    )
    mean_ret = sim["ret"].mean(axis=0)
    lam, alphas = cross_sectional_lambda(betas, mean_ret)
    assert len(lam) == 2
    assert len(alphas) == 50


def test_time_series_betas_recovers_beta():
    sim = simulate_cross_section(
        n_assets=20, t_periods=1000, n_factors=2, noise=0.005, seed=3
    )
    fdf = pd.DataFrame(sim["factor_ret"], columns=["F1", "F2"])
    alphas, betas, resid = time_series_betas(sim["ret"], fdf)
    np.testing.assert_allclose(betas.to_numpy(), sim["beta"], atol=0.03)
    assert betas.shape == (sim["n_assets"], sim["n_factors"])
