"""合成横截面数据生成器：已知真相，用于验证方法正确性。

生成过程（对照式 1.3）：
    1) 随机生成每只资产的因子暴露 beta（N×K）与真实因子溢价 lambda（K 维）；
    2) 按 r_it = beta_i' f_t + eps_it 生成收益时序，其中因子收益 f_t ~ N(lambda, Sigma_f)；
    3) 特征 char 直接用 beta（"公司特征=真实暴露"的理想情形，便于方法验证）。

这不是市场模拟器，而是"方法校准器"：因为真相已知，我们才能判断
FM 是否恢复了 lambda、GRS 是否在 alpha=0 时正确不拒绝。
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def simulate_cross_section(
    n_assets: int = 200,
    t_periods: int = 120,
    n_factors: int = 2,
    noise: float = 0.01,
    seed: int = 42,
    lambda_values: np.ndarray | None = None,
) -> dict:
    """生成一个已知真相的横截面收益面板。

    参数
    ----
    n_assets : 资产数量 N
    t_periods : 期数 T
    n_factors : 因子数量 K
    noise : 特质波动率（0 表示无噪声，可精确恢复参数）
    seed : 随机种子
    lambda_values : 可选，自定义每个因子的真实溢价；None 时随机生成

    返回
    ----
    dict，包含：
    - ret : DataFrame(T×N) 收益率
    - beta : ndarray(N×K) 真实因子暴露
    - lambda : ndarray(K) 真实因子溢价
    - factor_ret : ndarray(T×K) 因子收益时序
    - char : ndarray(T×N×K) 特征（此处等于 beta 的重复）
    - n_assets, n_factors
    """
    rng = np.random.default_rng(seed)
    beta = rng.uniform(0.5, 1.5, size=(n_assets, n_factors))
    if lambda_values is None:
        lam = rng.uniform(0.002, 0.010, size=n_factors)  # 月均因子溢价（已知真相）
    else:
        lam = np.asarray(lambda_values, dtype=float)
        if lam.shape != (n_factors,):
            raise ValueError(f"lambda_values 形状应为 ({n_factors},)，实际 {lam.shape}")

    sigma_f = np.diag(np.full(n_factors, 0.02 ** 2))
    factor_ret = rng.multivariate_normal(lam, sigma_f, size=t_periods)
    # 让"已实现的因子收益"样本均值恰好等于预设 lambda：
    # 这样在 noise=0 时，FM 应精确恢复真相，便于验证方法本身。
    factor_ret = factor_ret - factor_ret.mean(axis=0) + lam
    idio = rng.normal(0, noise, size=(t_periods, n_assets))
    ret = factor_ret @ beta.T + idio
    char = np.repeat(beta[None, :, :], t_periods, axis=0)  # T×N×K

    return {
        "ret": pd.DataFrame(ret, columns=[f"a{i}" for i in range(n_assets)]),
        "beta": beta,
        "lambda": lam,
        "factor_ret": factor_ret,
        "char": char,
        "n_assets": n_assets,
        "n_factors": n_factors,
    }
