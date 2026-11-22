"""常用风格因子构造（第2章 2.1 节配套；第3章会扩展为全部七大因子）。

所有函数返回 DataFrame(日期 × 股票)，与 sorting 模块接口衔接。
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def monthly_returns(prices: pd.DataFrame, freq: str = "ME") -> pd.DataFrame:
    """月末价格序列 → 月度收益率（跳过首月）。

    对月末价格先做前向填充，避免停牌/缺失月份产生伪缺失；
    再显式 fill_method=None，避免 pandas 未来版本的行为变化。
    """
    month_end = prices.resample(freq).last().ffill()
    return month_end.pct_change(fill_method=None).dropna(how="all")


def momentum(monthly_ret: pd.DataFrame, lookback: int = 12, skip: int = 1) -> pd.DataFrame:
    """动量因子：过去 lookback 月累计收益（跳过最近 skip 月，Jegadeesh-Titman 惯例）。"""
    return (1 + monthly_ret).rolling(lookback).apply(np.prod, raw=True).shift(skip) - 1


def book_to_market(fundamentals: pd.DataFrame) -> pd.DataFrame:
    """账面市值比 BM = 1 / PB。fundamentals 列：stock, trade_date, pb, total_mv。"""
    f = fundamentals.copy()
    f = f.rename(columns={"trade_date": "date"})
    f["bm"] = 1.0 / f["pb"]
    return f.pivot(index="date", columns="stock", values="bm")


def log_market_cap(fundamentals: pd.DataFrame) -> pd.DataFrame:
    """对数市值（削弱右偏，4.2.1 节惯例）。fundamentals 列：stock, trade_date, total_mv。"""
    f = fundamentals.copy()
    f = f.rename(columns={"trade_date": "date"})
    f["ln_mv"] = np.log(f["total_mv"])
    return f.pivot(index="date", columns="stock", values="ln_mv")

def earnings_yield(fundamentals: pd.DataFrame) -> pd.DataFrame:
    """盈利市值比 EP = 1/PE（中国版三因子的价值指标，Liu et al. 2019）。

    fundamentals 列：stock, trade_date, pe, total_mv。PE 必须为正（亏损股已剔除）。
    """
    f = fundamentals.copy()
    f = f.rename(columns={"trade_date": "date"})
    f["ep"] = 1.0 / f["pe"]
    return f.pivot(index="date", columns="stock", values="ep")
