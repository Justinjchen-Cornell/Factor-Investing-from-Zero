"""投资组合排序法（portfolio sort）——第2章 2.1 节的代码实现。

思想：用排序变量（如 BM）的高低代替因子暴露的高低，
按分位分组构建投资组合，多空价差组合的收益率就是因子收益率。
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def quantile_group(sort_values: pd.Series, n_groups: int = 10) -> pd.Series:
    """按变量取值分位分组，返回组号 1(最低) .. n_groups(最高)。

    排序法只假设变量与因子暴露相关，不假设任何数学关系（2.1.2 节）。
    """
    pct = sort_values.rank(pct=True)
    return np.ceil(pct * n_groups).clip(1, n_groups).astype(int)


def sort_portfolios(
    ret: pd.DataFrame,
    groups: pd.DataFrame,
    n_groups: int,
    weights: str = "equal",
    mktcap: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """按分组计算各投资组合的收益率时序。

    参数
    ----
    ret : DataFrame(日期 × 股票) 收益率
    groups : DataFrame(日期 × 股票) 每期每只股票的分组号
    n_groups : 分组数 L
    weights : "equal"（等权）或 "value"（市值加权，需 mktcap）
    mktcap : DataFrame(日期 × 股票) 市值，value 加权时必传

    返回
    ----
    DataFrame(日期 × 组号 1..n_groups)，每列是一个组合的收益率时序。
    """
    out = pd.DataFrame(index=ret.index, columns=list(range(1, n_groups + 1)), dtype=float)
    for g in range(1, n_groups + 1):
        mask = (groups == g)
        if weights == "equal":
            count = mask.sum(axis=1).replace(0, np.nan)
            out[g] = (ret * mask).sum(axis=1) / count
        elif weights == "value":
            cap = mktcap.where(mask)
            total = cap.sum(axis=1)
            w = cap.div(total, axis=0)
            out[g] = (ret * w).sum(axis=1)
        else:
            raise ValueError(f"weights 仅支持 equal/value，收到 {weights}")
    return out


def spread_return(port_ret: pd.DataFrame, high: int, low: int = 1) -> pd.Series:
    """价差组合（spread portfolio）：做多高组、做空低组，收益率 = 因子收益率。"""
    return port_ret[high] - port_ret[low]


def monotonicity_test(port_ret: pd.DataFrame) -> dict:
    """单调性检验（2.1.2 节）：组合均收益与分组的 Spearman 秩相关系数。"""
    group_order = list(port_ret.columns)
    means = port_ret.mean().reindex(group_order)
    rho = means.rank().corr(pd.Series(range(1, len(group_order) + 1), index=group_order))
    return {"rho": rho, "group_means": means}
