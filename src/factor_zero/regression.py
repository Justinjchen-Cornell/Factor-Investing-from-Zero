"""多因子模型的三种回归检验（第2章 2.2 节）。

- time_series_betas：时序回归，估计每个资产的因子暴露 beta（式 2.13）
- cross_sectional_lambda：两步截面回归，估计因子溢价 lambda（式 2.18）
- fama_macbeth：Fama-MacBeth 回归，"先回归、再均值"（式 2.36~2.40）

约定
----
ret : DataFrame(T×N)，index=日期，columns=资产
factor_ret : DataFrame(T×K)，index=日期，columns=因子
betas : DataFrame(N×K)，index=资产，columns=因子
characteristics : ndarray(T×N×K)，时变暴露（公司特征）
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from factor_zero.statistics import newey_west_vcov


def _ts_regression_single(
    y: np.ndarray, f: np.ndarray
) -> tuple[float, np.ndarray, np.ndarray]:
    """单资产时序回归，允许 y 或 f 中含缺失值。"""
    y = np.asarray(y, dtype=float)
    f = np.asarray(f, dtype=float)
    mask = np.isfinite(y) & np.all(np.isfinite(f), axis=1)
    if mask.sum() <= f.shape[1] + 1:
        return np.nan, np.full(f.shape[1], np.nan), np.full(len(y), np.nan)
    X = np.column_stack([np.ones(mask.sum()), f[mask]])
    coef, *_ = np.linalg.lstsq(X, y[mask], rcond=None)
    resid = np.full(len(y), np.nan)
    resid[mask] = y[mask] - X @ coef
    return float(coef[0]), coef[1:], resid


def time_series_betas(
    ret: pd.DataFrame, factor_ret: pd.DataFrame
) -> tuple[pd.Series, pd.DataFrame, pd.DataFrame]:
    """对每个资产独立做时序回归 r_it = alpha_i + beta_i' f_t + eps_it。

    返回
    ----
    alphas : Series(N)，每个资产的 alpha
    betas : DataFrame(N×K)，index=资产，columns=因子
    residuals : DataFrame(T×N)，index=日期，columns=资产
    """
    ret = ret.copy()
    factor_ret = factor_ret.reindex(ret.index)
    alphas, betas, resid = {}, {}, {}
    for asset in ret.columns:
        alpha, beta_vec, e = _ts_regression_single(
            ret[asset].to_numpy(), factor_ret.to_numpy()
        )
        alphas[asset] = alpha
        betas[asset] = beta_vec
        resid[asset] = e
    beta_df = pd.DataFrame.from_dict(
        betas, orient="index", columns=factor_ret.columns
    )
    return (
        pd.Series(alphas, name="alpha"),
        beta_df,
        pd.DataFrame(resid, index=ret.index, columns=ret.columns),
    )


def cross_sectional_lambda(
    betas: pd.DataFrame, mean_ret: pd.Series
) -> tuple[np.ndarray, np.ndarray]:
    """截面回归：mean_ret = lambda' beta + alpha（式 2.18，无截距）。

    参数
    ----
    betas : DataFrame(N×K)，index=资产，columns=因子
    mean_ret : Series(N)，每个资产的平均收益

    返回
    ----
    (lambda: K 维, alphas: N 维)
    """
    y = mean_ret.reindex(betas.index).to_numpy(dtype=float)
    B = betas.to_numpy(dtype=float)
    mask = np.isfinite(y) & np.all(np.isfinite(B), axis=1)
    if mask.sum() <= B.shape[1]:
        raise ValueError("有效资产数量不足，无法做截面回归")
    lam, *_ = np.linalg.lstsq(B[mask], y[mask], rcond=None)
    alphas = y - B @ lam
    return lam, alphas


def fama_macbeth(
    ret: pd.DataFrame,
    characteristics: np.ndarray,
    max_lag: int | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Fama-MacBeth 回归（2.2.4 节）：每期截面回归，再对 lambda_t 求均值。

    参数
    ----
    ret : DataFrame(T×N) 收益率
    characteristics : ndarray(T×N×K) 时变因子暴露（公司特征）
    max_lag : Newey-West 最大滞后阶数（None 用自适应规则）

    返回
    ----
    (lambda 均值(K+1 含截距), lambda 时序(T×(K+1)), 标准误, t 值)
    """
    T, N, K = characteristics.shape
    if ret.shape != (T, N):
        raise ValueError(f"ret 形状应为 {(T, N)}，实际 {ret.shape}")

    X = np.concatenate([np.ones((T, N, 1)), characteristics], axis=2)
    lam_t = np.full((T, K + 1), np.nan)
    for t in range(T):
        y = ret.iloc[t].to_numpy(dtype=float)
        Xt = X[t]
        mask = np.isfinite(y) & np.all(np.isfinite(Xt), axis=1)
        if mask.sum() <= K + 1:
            continue
        coef, *_ = np.linalg.lstsq(Xt[mask], y[mask], rcond=None)
        lam_t[t] = coef

    lam_mean = np.nanmean(lam_t, axis=0)
    se = np.full(K + 1, np.nan)
    for k in range(K + 1):
        series = pd.Series(lam_t[:, k]).dropna()
        if len(series) < 2:
            continue
        resid = series.to_numpy() - series.mean()
        vcov = newey_west_vcov(np.ones((len(series), 1)), resid, max_lag)
        se[k] = np.sqrt(vcov[0, 0])
    t_stat = lam_mean / se
    return lam_mean, lam_t, se, t_stat
