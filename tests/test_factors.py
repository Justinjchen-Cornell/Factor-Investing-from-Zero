"""因子构造测试：与手工计算交叉验证。"""
import numpy as np
import pandas as pd

from factor_zero.factors import (monthly_returns, momentum, book_to_market,
    log_market_cap, earnings_yield)


def test_monthly_returns_manual():
    dates = pd.bdate_range("2020-01-01", "2020-03-31")
    prices = pd.DataFrame({"A": np.linspace(10, 12, len(dates))}, index=dates)
    mr = monthly_returns(prices)
    assert len(mr) == 2
    assert (mr["A"] > 0).all()


def test_momentum_skips_recent_month():
    # 构造 15 个月收益，最后一个月暴涨；动量(12,1) 不应包含最后一个月
    idx = pd.period_range("2020-01", periods=15, freq="M").to_timestamp()
    ret = pd.DataFrame({"A": np.zeros(15)}, index=idx)
    ret.iloc[-1, 0] = 0.50  # 最近一月暴涨 50%
    mom = momentum(ret, lookback=12, skip=1)
    last = mom.dropna().iloc[-1, 0]
    assert abs(last) < 1e-9, "动量应跳过最近一个月，暴涨不应进入"


def test_book_to_market_and_log_size():
    fund = pd.DataFrame({
        "stock": ["A", "A", "B", "B"],
        "trade_date": pd.to_datetime(["2020-01-31", "2020-02-29"] * 2),
        "pb": [2.0, 2.5, 10.0, 8.0],
        "total_mv": [1e10, 1.1e10, 1e9, 0.9e9],
    })
    bm = book_to_market(fund)
    assert abs(bm.loc["2020-01-31", "A"] - 0.5) < 1e-12
    ln = log_market_cap(fund)
    assert abs(ln.loc["2020-02-29", "B"] - np.log(0.9e9)) < 1e-9


def test_earnings_yield():
    fund = pd.DataFrame({
        "stock": ["A", "A", "B", "B"],
        "trade_date": pd.to_datetime(["2020-01-31", "2020-02-29"] * 2),
        "pe": [10.0, 12.5, 20.0, 16.0],
        "total_mv": [1e10, 1.1e10, 1e9, 0.9e9],
    })
    ep = earnings_yield(fund)
    assert abs(ep.loc["2020-01-31", "A"] - 0.1) < 1e-12
    assert abs(ep.loc["2020-02-29", "B"] - 0.0625) < 1e-9
