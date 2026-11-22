"""排序法模块测试：分位分组、组合收益、价差组合、单调性检验。"""
import numpy as np
import pandas as pd

from factor_zero.sorting import quantile_group, sort_portfolios, spread_return, monotonicity_test


def test_quantile_group_ten_groups():
    s = pd.Series(np.arange(100.0))
    g = quantile_group(s, n_groups=10)
    assert g.min() == 1 and g.max() == 10
    assert g.groupby(g).size().between(9, 11).all(), "每组约10个"


def test_quantile_group_monotonic():
    s = pd.Series(np.arange(100.0))
    g = quantile_group(s, n_groups=10)
    # 变量越大组号越大（默认升序）
    assert (g.diff().dropna() >= 0).all()


def test_sort_portfolios_equal_weight():
    # 4 支股票 × 3 期：组1={A,B} 组2={C,D}，等权组合收益 = 组内均值
    ret = pd.DataFrame({
        "A": [0.01, 0.02, 0.03], "B": [0.03, 0.01, 0.02],
        "C": [0.05, 0.06, 0.04], "D": [0.07, 0.04, 0.06],
    })
    groups = pd.DataFrame({
        "A": [1, 1, 1], "B": [1, 1, 1],
        "C": [2, 2, 2], "D": [2, 2, 2],
    })
    port = sort_portfolios(ret, groups, n_groups=2)
    np.testing.assert_allclose(port[1].values, [0.02, 0.015, 0.025])
    np.testing.assert_allclose(port[2].values, [0.06, 0.05, 0.05])


def test_spread_return():
    port = pd.DataFrame({1: [0.01, 0.02], 10: [0.05, 0.04]})
    spread = spread_return(port, high=10, low=1)
    np.testing.assert_allclose(spread.values, [0.04, 0.02])


def test_monotonicity_perfect_positive():
    # 组均值完美递增 → Spearman 秩相关 ≈ 1（浮点精度内）
    port = pd.DataFrame({g: [0.01 * g] for g in range(1, 11)})
    res = monotonicity_test(port)
    assert abs(res["rho"] - 1.0) < 1e-9


def test_long_short_factor_direction():
    from factor_zero.sorting import long_short_factor
    # 2 期、4 只股票：A/B 低排序值，C/D 高排序值；高组每期收益更高
    idx = pd.to_datetime(["2020-01-31", "2020-02-29", "2020-03-31"])
    sort_values = pd.DataFrame({"A": [1, 1, 1], "B": [2, 2, 2],
                                "C": [3, 3, 3], "D": [4, 4, 4]}, index=idx)
    ret = pd.DataFrame({"A": [0.01, 0.01, 0.01], "B": [0.01, 0.01, 0.01],
                        "C": [0.05, 0.05, 0.05], "D": [0.05, 0.05, 0.05]}, index=idx)
    high, _, _ = long_short_factor(sort_values, ret, n_groups=2, high_minus_low=True)
    low, _, _ = long_short_factor(sort_values, ret, n_groups=2, high_minus_low=False)
    assert (high > 0).all()
    np.testing.assert_allclose(high.values, -low.values)
