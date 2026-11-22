"""A 股快照数据加载与教学面板构造（第3章配套）。

数据现实
--------
- 日线行情：87 只 A 股，2018-2024，真实快照；
- 估值快照：只有一期（2026-09-01）的 PB / PE / 总市值；
- 因此，逐期估值/ROE/投资面板是由“快照 + 价格/成交量路径”推导的
  **教学用合成面板**，仅用于演示因子构造与检验流程，
  数值不代表真实 A 股的历史估值或实证结论。
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from factor_zero.factors import (
    monthly_returns,
    momentum,
    book_to_market,
    log_market_cap,
)


def find_sample_dir(sample_dir: str | Path | None = None) -> Path:
    """定位 data/sample 目录。"""
    if sample_dir is not None:
        p = Path(sample_dir)
        if p.exists():
            return p
        raise FileNotFoundError(f"找不到 {sample_dir}")
    candidates = [
        Path("data/sample"),
        Path(__file__).resolve().parents[2] / "data" / "sample",
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError("找不到 data/sample，请从仓库内运行")


def load_ashare_panel(sample_dir: str | Path | None = None) -> dict:
    """加载 A 股快照，返回第3章所需的月度面板与七大因子原料。

    返回 dict，主要键：
    - ret : DataFrame(T×N) 月度收益率
    - price : DataFrame 日线收盘价
    - volume : DataFrame 日线成交量
    - mktcap : DataFrame(T×N) 总市值（价格 × 推导股本）
    - size : DataFrame(T×N) 对数市值
    - bm : DataFrame(T×N) 账面市值比
    - roe : DataFrame(T×N) ROE（PB/PE，教学面板）
    - investment : DataFrame(T×N) 投资强度（合成教学面板）
    - turnover : DataFrame(T×N) 月换手率（成交量/推导股本）
    - momentum : DataFrame(T×N) 12-1 动量
    - market : Series(T) 市值加权市场收益
    """
    sample = find_sample_dir(sample_dir)
    daily_dir = sample / "a_share_snapshot" / "daily"
    codes = sorted(p.stem for p in daily_dir.glob("*.csv"))
    if not codes:
        raise FileNotFoundError(f"{daily_dir} 下没有 CSV")

    close, volume = {}, {}
    for code in codes:
        df = pd.read_csv(daily_dir / f"{code}.csv", parse_dates=["date"])
        df = df.set_index("date").sort_index()
        close[code] = df["close"]
        volume[code] = df["volume"]
    price_df = pd.DataFrame(close).sort_index()
    volume_df = pd.DataFrame(volume).sort_index()

    # 月度收益；只保留整段历史完整的股票，保证逐期排序可比
    ret = monthly_returns(price_df).dropna(axis=1, how="any")
    cols = ret.columns

    fund = pd.read_csv(
        sample / "a_share_snapshot" / "fundamentals.csv", parse_dates=["trade_date"]
    )
    fund["stock"] = fund["stock"].astype(int).astype(str).str.zfill(6)
    fund = fund.set_index("stock").reindex(cols)
    if fund["pb"].isna().any():
        raise ValueError("估值快照与行情股票代码未完全对齐")

    month_end = price_df.resample("ME").last().ffill().reindex(columns=cols)
    month_end = month_end.reindex(ret.index)
    last_price = month_end.iloc[-1]
    shares = fund["total_mv"] / last_price
    mktcap = month_end.mul(shares, axis=1)

    months = np.arange(len(ret.index))
    phase = pd.Series(
        np.linspace(0, 2 * np.pi, len(cols), endpoint=False), index=cols
    )
    seasonal = pd.DataFrame(
        np.sin(months[:, None] / 12 * 2 * np.pi + phase.values[None, :]),
        index=ret.index, columns=cols,
    )

    # 教学用估值/ROE/投资面板：由快照水平 + 平滑季节项生成
    base_pb = fund["pb"]
    pb = (1 + 0.15 * seasonal).mul(base_pb, axis=1).clip(lower=0.05)
    base_roe = (fund["pb"] / fund["pe"]).replace([np.inf, -np.inf], np.nan)
    base_roe = base_roe.clip(-0.50, 0.50).fillna(0.10)
    roe = (1 + 0.10 * seasonal).mul(base_roe, axis=1).clip(-0.50, 0.50)

    rng = np.random.default_rng(2026)
    base_growth = pd.Series(rng.uniform(0.0, 0.20, len(cols)), index=cols)
    investment = (1 + 0.15 * seasonal).mul(base_growth, axis=1).clip(lower=0.0)

    pe = (pb / roe.replace(0, np.nan)).replace([np.inf, -np.inf], np.nan)
    pe = pe.fillna(pb / 0.10)

    panel = pd.concat([
        pd.DataFrame({
            "stock": col,
            "trade_date": ret.index,
            "pb": pb[col].values,
            "pe": pe[col].values,
            "total_mv": mktcap[col].values,
        }) for col in cols
    ], ignore_index=True)

    bm = book_to_market(panel).reindex(index=ret.index, columns=cols)
    size = log_market_cap(panel).reindex(index=ret.index, columns=cols)

    monthly_volume = volume_df.resample("ME").sum().ffill().reindex(
        index=ret.index, columns=cols
    )
    turnover = monthly_volume.div(shares, axis=1).clip(0.001, 20.0)

    mom = momentum(ret, lookback=12, skip=1).reindex(index=ret.index, columns=cols)

    # 市值加权市场收益（权重用上一期市值，避免同期权重）
    weights = mktcap.shift(1)
    weights = weights.div(weights.sum(axis=1), axis=0)
    market = (ret * weights).sum(axis=1, min_count=1).dropna()

    return {
        "ret": ret,
        "price": price_df,
        "volume": volume_df,
        "mktcap": mktcap,
        "size": size,
        "bm": bm,
        "roe": roe,
        "investment": investment,
        "turnover": turnover,
        "momentum": mom,
        "market": market,
        "fundamentals": fund,
        "panel": panel,
    }
