"""异象研究工具（第5章配套）。

- piotroski_f_score : Piotroski (2000) 九信号 F-Score
- make_teaching_fundamentals : 教学用合成财务面板（真实财报数据缺失时的替代）
- distance_from_52w_high : 价格 / 过去 12 个月最高价（52 周高点锚定）
- rolling_ivol : 滚动 FF3 回归残差波动率（特质波动率）

⚠️ 数据说明：本仓库没有完整财报数据，F-Score 的九项信号由教学合成面板生成；
52 周高点与 IVOL 使用真实价格快照，但样本仅 87 只股票。所有结果仅用于演示方法。
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def piotroski_f_score(fund: dict) -> pd.DataFrame:
    """Piotroski (2000) 九信号 F-Score，输入为同形状的财务面板 dict。

    需要的键
    --------
    roa, cfo, delta_roa, delta_leverage, delta_current_ratio,
    equity_issued, delta_gross_margin, delta_asset_turnover

    计分（每项 1 分，共 9 分）
    ------------------------
    1. ROA > 0
    2. CFO > 0
    3. ΔROA > 0
    4. CFO > ROA（应计质量）
    5. ΔLeverage < 0（杠杆下降）
    6. ΔCurrent ratio > 0（流动性改善）
    7. Equity issued <= 0（没有增发）
    8. ΔGross margin > 0（毛利率改善）
    9. ΔAsset turnover > 0（周转率改善）
    """
    required = [
        "roa", "cfo", "delta_roa", "delta_leverage", "delta_current_ratio",
        "equity_issued", "delta_gross_margin", "delta_asset_turnover",
    ]
    missing = [k for k in required if k not in fund]
    if missing:
        raise KeyError(f"F-Score 缺少字段 {missing}")

    score = (
        (fund["roa"] > 0).astype(int)
        + (fund["cfo"] > 0).astype(int)
        + (fund["delta_roa"] > 0).astype(int)
        + (fund["cfo"] > fund["roa"]).astype(int)
        + (fund["delta_leverage"] < 0).astype(int)
        + (fund["delta_current_ratio"] > 0).astype(int)
        + (fund["equity_issued"] <= 0).astype(int)
        + (fund["delta_gross_margin"] > 0).astype(int)
        + (fund["delta_asset_turnover"] > 0).astype(int)
    )
    # 任一输入缺失 → 总分缺失，避免把“不知道”当成 0 分
    valid = fund[required[0]].notna()
    for k in required[1:]:
        valid = valid & fund[k].notna()
    return score.where(valid)


def make_teaching_fundamentals(panel: dict, seed: int = 2026) -> dict:
    """生成教学用合成财务面板（宽表 dict），用于演示 F-Score。

    真实财报数据缺失；这里用潜在质量 + 平滑季节项 + 噪声生成九项信号。
    仅用于演示 F-Score 的计算与排序流程，不代表真实公司财务。
    """
    ret = panel["ret"]
    dates, cols = ret.index, ret.columns
    rng = np.random.default_rng(seed)
    months = np.arange(len(dates))
    phase = np.linspace(0, 2 * np.pi, len(cols), endpoint=False)
    seasonal = pd.DataFrame(
        np.sin(months[:, None] / 12 * 2 * np.pi + phase[None, :]),
        index=dates, columns=cols,
    )

    base_roa = pd.Series(rng.normal(0.06, 0.03, len(cols)), index=cols)
    roa = (base_roa + 0.01 * seasonal
           + rng.normal(0, 0.005, (len(dates), len(cols))))
    roa = pd.DataFrame(roa, index=dates, columns=cols).clip(-0.2, 0.3)

    cfo = roa + rng.normal(0.01, 0.01, (len(dates), len(cols)))
    fund = {
        "roa": roa,
        "cfo": pd.DataFrame(cfo, index=dates, columns=cols),
        "delta_roa": roa - roa.shift(12),
        "delta_leverage": pd.DataFrame(rng.normal(0, 0.03, (len(dates), len(cols))), index=dates, columns=cols),
        "delta_current_ratio": pd.DataFrame(rng.normal(0, 0.05, (len(dates), len(cols))), index=dates, columns=cols),
        "equity_issued": pd.DataFrame(rng.normal(0, 0.02, (len(dates), len(cols))), index=dates, columns=cols),
        "delta_gross_margin": pd.DataFrame(rng.normal(0, 0.02, (len(dates), len(cols))), index=dates, columns=cols),
        "delta_asset_turnover": pd.DataFrame(rng.normal(0, 0.02, (len(dates), len(cols))), index=dates, columns=cols),
    }
    return fund


def distance_from_52w_high(prices: pd.DataFrame, window: int = 12) -> pd.DataFrame:
    """价格 / 过去 window 期最高价（月度数据默认 12 个月）。

    返回值越接近 1，表示越靠近 52 周高点；越小表示离高点越远。
    """
    rolling_max = prices.rolling(window, min_periods=window).max()
    return prices / rolling_max


def rolling_ivol(
    ret: pd.DataFrame,
    factor_ret: pd.DataFrame,
    window: int = 24,
    annualize: bool = True,
) -> pd.DataFrame:
    """滚动多因子回归的残差波动率（特质波动率 IVOL）。

    对每只股票、每个窗口做 r = α + β'f + ε，取残差标准差；
    默认年化（×√12）。信号只使用窗口内数据，不包含未来信息。
    """
    ret = ret.copy()
    factor_ret = factor_ret.reindex(ret.index)
    dates = ret.index
    out = pd.DataFrame(np.nan, index=dates, columns=ret.columns)
    X_all = np.column_stack([np.ones(len(factor_ret)), factor_ret.to_numpy(dtype=float)])

    for col in ret.columns:
        y_all = ret[col].to_numpy(dtype=float)
        for t in range(window, len(dates) + 1):
            y = y_all[t - window:t]
            X = X_all[t - window:t]
            mask = np.isfinite(y) & np.all(np.isfinite(X), axis=1)
            if mask.sum() <= X.shape[1] + 1:
                continue
            coef, *_ = np.linalg.lstsq(X[mask], y[mask], rcond=None)
            resid = y[mask] - X[mask] @ coef
            vol = resid.std(ddof=1)
            if annualize:
                vol *= np.sqrt(12)
            out.iloc[t - 1, out.columns.get_loc(col)] = vol
    return out
