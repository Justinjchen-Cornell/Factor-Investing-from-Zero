"""组合构建、风险模型与归因工具（第7章配套）。

- build_style_exposures : 把因子面板转成风格暴露（截面 z-score）
- factor_covariance     : 因子协方差（滚动窗口，年化）
- portfolio_risk        : 组合风险分解（因子风险 + 特质风险）
- min_variance_weights  : 最小方差组合（长仓/权重上限）
- max_sharpe_weights    : 最大 Sharpe 组合（长仓/权重上限）
- style_regression      : Sharpe 风格回归（组合收益 ~ 因子收益）
- smart_beta_weights    : Smart Beta 加权（等权/分数加权/风险加权）
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.optimize import minimize

FACTOR_ORDER = ["MKT", "SMB", "HML", "WML", "RMW", "CMA", "TURN"]


def _zs(series: pd.Series) -> pd.Series:
    std = series.std()
    if not np.isfinite(std) or std < 1e-12:
        return series * 0.0
    return (series - series.mean()) / std


def build_style_exposures(
    panel: dict, date, beta: pd.DataFrame | None = None
) -> pd.DataFrame:
    """构造某期的风格暴露（N×K，列顺序见 FACTOR_ORDER）。

    方向约定与第3章因子收益一致：
    SMB=-z(size), HML=z(bm), WML=z(momentum), RMW=z(roe),
    CMA=-z(investment), TURN=-z(turnover), MKT=z(beta)（未给 beta 时取 1）。
    """
    B = pd.DataFrame(index=panel["ret"].columns)
    B["SMB"] = -_zs(panel["size"].loc[date])
    B["HML"] = _zs(panel["bm"].loc[date])
    B["WML"] = _zs(panel["momentum"].loc[date])
    B["RMW"] = _zs(panel["roe"].loc[date])
    B["CMA"] = -_zs(panel["investment"].loc[date])
    B["TURN"] = -_zs(panel["turnover"].loc[date])
    B["MKT"] = _zs(beta.loc[date]) if beta is not None else 1.0
    return B[FACTOR_ORDER].dropna()


def factor_covariance(
    factor_ret: pd.DataFrame, date, window: int = 36, annualize: bool = True
) -> pd.DataFrame:
    """用 date 及之前的 window 期因子收益估计因子协方差。"""
    cov = factor_ret.loc[:date].tail(window)[FACTOR_ORDER].cov()
    if annualize:
        cov *= 12
    return cov


def specific_variance(ivol: pd.DataFrame, date, exposures_index) -> pd.Series:
    """从年化 IVOL 面板取某期特质波动率平方（特质方差）。"""
    sv = ivol.loc[date].reindex(exposures_index) ** 2
    if sv.isna().any():
        sv = sv.fillna(sv.median())
    return sv


def portfolio_risk(
    weights: pd.Series,
    exposures: pd.DataFrame,
    factor_cov: pd.DataFrame,
    spec_var: pd.Series,
) -> dict:
    """组合风险分解：总波动、因子波动、特质波动、各因子贡献。"""
    w = pd.Series(weights).reindex(exposures.index).fillna(0.0)
    Bp = w.to_numpy() @ exposures.to_numpy()
    fcov = factor_cov.loc[exposures.columns, exposures.columns].to_numpy()
    factor_var = float(Bp @ fcov @ Bp)
    specific_var = float(np.sum(w.to_numpy() ** 2 * spec_var.reindex(exposures.index).to_numpy()))
    total_var = factor_var + specific_var
    total_vol = np.sqrt(max(total_var, 0.0))
    factor_vol = np.sqrt(max(factor_var, 0.0))
    specific_vol = np.sqrt(max(specific_var, 0.0))
    factor_contrib = pd.Series(
        Bp * (fcov @ Bp) / total_vol if total_vol > 0 else np.zeros_like(Bp),
        index=exposures.columns,
    )
    specific_contrib = specific_var / total_vol if total_vol > 0 else 0.0
    return {
        "total_vol": total_vol,
        "factor_vol": factor_vol,
        "specific_vol": specific_vol,
        "specific_contrib": float(specific_contrib),
        "factor_contrib": factor_contrib,
    }


def _optimize(objective, n: int, long_only: bool, max_weight: float):
    x0 = np.ones(n) / n
    bounds = [(0.0, max_weight)] * n if long_only else [(None, None)] * n
    cons = [{"type": "eq", "fun": lambda w: np.sum(w) - 1.0}]
    res = minimize(objective, x0, method="SLSQP", bounds=bounds, constraints=cons,
                   options={"maxiter": 1000, "ftol": 1e-12})
    if not res.success:
        raise RuntimeError(f"优化失败: {res.message}")
    return res.x


def min_variance_weights(
    cov: pd.DataFrame, long_only: bool = True, max_weight: float = 1.0
) -> pd.Series:
    """最小方差组合。"""
    arr = cov.to_numpy()
    w = _optimize(lambda x: x @ arr @ x, len(arr), long_only, max_weight)
    return pd.Series(w, index=cov.index)


def max_sharpe_weights(
    mu: pd.Series, cov: pd.DataFrame, risk_free: float = 0.0,
    long_only: bool = True, max_weight: float = 1.0,
) -> pd.Series:
    """最大 Sharpe 组合（μ 与 cov 需同频率、同资产顺序）。"""
    mu_arr = mu.reindex(cov.index).to_numpy()
    cov_arr = cov.to_numpy()

    def neg_sharpe(w):
        vol = np.sqrt(max(w @ cov_arr @ w, 1e-18))
        return -(w @ mu_arr - risk_free) / vol

    w = _optimize(neg_sharpe, len(mu_arr), long_only, max_weight)
    return pd.Series(w, index=cov.index)


def style_regression(
    port_ret: pd.Series, factor_ret: pd.DataFrame
) -> tuple[float, pd.Series, float, pd.Series]:
    """Sharpe 风格回归：r_p = α + Σ β_k f_k + ε。

    返回 (alpha, betas, R², 残差)。
    """
    data = pd.concat([port_ret.rename("port"), factor_ret], axis=1).dropna()
    y = data["port"].to_numpy()
    X = np.column_stack([np.ones(len(data)), data[factor_ret.columns].to_numpy()])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    resid = y - X @ coef
    ss_res = float(resid @ resid)
    ss_tot = float(np.sum((y - y.mean()) ** 2))
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
    return (
        float(coef[0]),
        pd.Series(coef[1:], index=factor_ret.columns),
        float(r2),
        pd.Series(resid, index=data.index),
    )


def smart_beta_weights(
    scores: pd.Series, method: str = "equal", risk: pd.Series | None = None
) -> pd.Series:
    """Smart Beta 加权：等权 / 分数加权 / 风险加权（1/vol）。"""
    s = pd.Series(scores).dropna()
    if s.empty:
        raise ValueError("scores 为空")
    if method == "equal":
        return pd.Series(1.0 / len(s), index=s.index)
    if method == "score":
        pos = s.clip(lower=0.0)
        if pos.sum() <= 0:
            return pd.Series(1.0 / len(s), index=s.index)
        return pos / pos.sum()
    if method == "risk":
        if risk is None:
            raise ValueError("risk 加权需要 risk（波动率）序列")
        inv = 1.0 / risk.reindex(s.index).replace(0, np.nan)
        inv = inv.fillna(inv.median())
        return inv / inv.sum()
    raise ValueError(f"未知加权方法 {method}")
