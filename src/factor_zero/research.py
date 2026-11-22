"""因子研究现状的实验工具（第6章配套）。

- simulate_random_factors : 纯噪声因子的 t 值分布（数据窥探）
- p_hacking_summary       : 不同 t 阈值下的“显著因子”数量
- publication_decay_experiment : 挑选最优区间后的样本外衰减
- polynomial_train_test_mse : 多项式拟合的训练/测试误差（过拟合）
- sentiment_signal        : 换手率 + 近期收益的投资者情绪代理
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def simulate_random_factors(
    n_factors: int = 1000, n_periods: int = 120, seed: int = 2020
) -> pd.DataFrame:
    """生成纯噪声因子，返回每个因子的均值与 t 值。

    这些因子在真实世界里不存在任何溢价；用于演示“数据窥探”
    会挖出多少假显著因子。
    """
    rng = np.random.default_rng(seed)
    returns = rng.normal(0, 0.02, size=(n_periods, n_factors))
    means = returns.mean(axis=0)
    ses = returns.std(axis=0, ddof=1) / np.sqrt(n_periods)
    return pd.DataFrame({
        "factor": np.arange(n_factors),
        "mean": means,
        "t_stat": means / ses,
    })


def p_hacking_summary(
    t_stats: pd.Series | np.ndarray,
    thresholds: tuple[float, ...] = (2.0, 3.0, 3.4),
) -> pd.DataFrame:
    """统计不同 |t| 阈值下的“显著因子”数量和比例。"""
    t = np.asarray(t_stats, dtype=float)
    rows = []
    for thr in thresholds:
        sig = np.abs(t) > thr
        rows.append({
            "threshold": thr,
            "count": int(sig.sum()),
            "share": float(sig.mean()),
        })
    return pd.DataFrame(rows)


def publication_decay_experiment(
    n_simulations: int = 500,
    true_premium: float = 0.004,
    noise: float = 0.03,
    t_periods: int = 240,
    in_sample: int = 60,
    seed: int = 7,
) -> pd.DataFrame:
    """模拟“挑选表现最好的区间发表”后的样本外衰减。

    每次模拟：
    1. 生成 T 期真实溢价 + 噪声；
    2. 选表现最好的 in_sample 窗口作为“发表前”；
    3. 用全样本均值作为“发表后/长期真相”；
    4. 计算衰减 = 1 - 全样本均值 / 发表前均值。
    """
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(n_simulations):
        ret = rng.normal(true_premium, noise, size=t_periods)
        starts = range(0, t_periods - in_sample)
        best = max(starts, key=lambda s: ret[s:s + in_sample].mean())
        in_mean = ret[best:best + in_sample].mean()
        full_mean = ret.mean()
        decay = 1 - full_mean / in_mean if abs(in_mean) > 1e-12 else np.nan
        rows.append({"in_sample": in_mean, "full_sample": full_mean, "decay": decay})
    return pd.DataFrame(rows)


def polynomial_train_test_mse(
    degrees: tuple[int, ...] = (1, 3, 9),
    n: int = 200,
    noise: float = 0.3,
    test_ratio: float = 0.3,
    seed: int = 42,
) -> pd.DataFrame:
    """在“非线性真实关系 + 噪声”上拟合不同阶数多项式，比较训练/测试 MSE。

    高阶多项式会记住训练集噪声：训练 MSE 很低、测试 MSE 很高（过拟合）。
    """
    rng = np.random.default_rng(seed)
    x = np.linspace(-3, 3, n)
    y = 0.5 * x + 0.8 * np.sin(1.5 * x) + rng.normal(0, noise, n)
    idx = rng.permutation(n)
    split = int(n * (1 - test_ratio))
    train, test = idx[:split], idx[split:]
    rows = []
    for d in degrees:
        coef = np.polyfit(x[train], y[train], d)
        train_mse = np.mean((np.polyval(coef, x[train]) - y[train]) ** 2)
        test_mse = np.mean((np.polyval(coef, x[test]) - y[test]) ** 2)
        rows.append({"degree": d, "train_mse": train_mse, "test_mse": test_mse})
    return pd.DataFrame(rows)


def sentiment_signal(panel: dict) -> pd.DataFrame:
    """投资者情绪代理：换手率 z-score + 上期收益 z-score。

    高值 = 高换手 + 近期上涨（情绪偏热）；低值 = 低换手 + 近期下跌。
    """
    ret = panel["ret"]
    turnover = panel["turnover"]

    def zscore(df: pd.DataFrame) -> pd.DataFrame:
        std = df.std(axis=1).replace(0, np.nan)
        return df.sub(df.mean(axis=1), axis=0).div(std, axis=0)

    sentiment = zscore(turnover) + zscore(ret.shift(1))
    return sentiment.fillna(0.0)
