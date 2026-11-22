"""统计量工具：Newey-West 调整、单序列 t 检验、时序回归、GRS 检验。

对应原书第2章 2.2.1（时序回归/GRS）与 2.4.3（Newey-West）。
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def newey_west_vcov(X: np.ndarray, eps: np.ndarray, max_lag: int | None = None) -> np.ndarray:
    """Newey-West 异方差自相关相合协方差矩阵（式 2.63~2.64）。

    修正了残差存在自相关和异方差时 OLS 标准误被低估的问题。
    """
    X = np.asarray(X)
    eps = np.asarray(eps)
    T, K = X.shape
    if max_lag is None:
        max_lag = int(np.floor(4 * (T / 100) ** (2 / 9)))  # NW(1994) 自适应规则
    Xe = X * eps[:, None]
    S = Xe.T @ Xe  # White 部分（仅异方差）
    for j in range(1, max_lag + 1):
        w = 1 - j / (max_lag + 1)  # Bartlett 核权重
        S += w * (Xe[j:].T @ Xe[:-j] + Xe[:-j].T @ Xe[j:])
    XtX_inv = np.linalg.inv(X.T @ X)
    return XtX_inv @ S @ XtX_inv


def nw_t_stat(series: pd.Series, max_lag: int | None = None) -> tuple[float, float]:
    """单收益率序列的经 Newey-West 调整的 t 检验（2.4.4 节）。

    返回 (t 值, 标准误)。X = 1 的 NW 回归即对均值序列做 HAC 修正。
    """
    T = len(series)
    resid = (series - series.mean()).to_numpy()
    X = np.ones((T, 1))
    vcov = newey_west_vcov(X, resid, max_lag)
    se = np.sqrt(vcov[0, 0])
    return series.mean() / se, se


def ts_regression(
    asset_ret: np.ndarray, factor_ret: pd.DataFrame
) -> tuple[float, np.ndarray, np.ndarray]:
    """单资产时序回归：r_t = alpha + beta' f_t + eps_t（式 2.13）。

    返回 (alpha, betas, 残差序列)。
    """
    T = len(asset_ret)
    X = np.column_stack([np.ones(T), factor_ret.to_numpy()])
    coef, *_ = np.linalg.lstsq(X, asset_ret, rcond=None)
    alpha, betas = coef[0], coef[1:]
    resid = asset_ret - X @ coef
    return float(alpha), betas, resid


def grs_test(
    alphas: np.ndarray, residuals: np.ndarray, factor_ret: np.ndarray
) -> tuple[float, float]:
    """GRS 检验（Gibbons-Ross-Shanken 1989）：联合检验所有 alpha 是否为零。

    返回 (F 统计量, p 值)。原假设：alpha 全部为 0（模型完美）。
    """
    T, N = residuals.shape
    K = factor_ret.shape[1]
    mu = factor_ret.mean(axis=0)
    Sigma_f = np.cov(factor_ret, rowvar=False)
    Sigma_e = np.cov(residuals, rowvar=False)
    scalar = (T - N - K) / N * (1 + mu @ np.linalg.inv(Sigma_f) @ mu) ** (-1)
    F = scalar * (alphas @ np.linalg.inv(Sigma_e) @ alphas)
    p = 1 - stats.f.cdf(F, N, T - N - K)
    return float(F), float(p)


def factor_summary(factor_ret: pd.Series, periods_per_year: int = 12) -> dict:
    """因子收益率序列的绩效汇总（第3章配套）。

    返回年化收益、年化波动、Sharpe、NW t 值、最大回撤、胜率。
    """
    r = factor_ret.dropna()
    if len(r) < 2:
        return {}
    mean_ann = float(r.mean() * periods_per_year)
    vol_ann = float(r.std() * np.sqrt(periods_per_year))
    sharpe = mean_ann / vol_ann if vol_ann > 1e-12 else np.nan
    t_stat, _ = nw_t_stat(r)
    nav = (1 + r).cumprod()
    mdd = float((nav / nav.cummax() - 1).min())
    return {
        "mean_ann": mean_ann,
        "vol_ann": vol_ann,
        "sharpe": float(sharpe),
        "t_stat": float(t_stat),
        "max_drawdown": mdd,
        "win_rate": float((r > 0).mean()),
    }
