"""第5章异象工具测试：F-Score 边界、52 周高点、IVOL 基本性质。"""
import numpy as np
import pandas as pd

from factor_zero.anomalies import (
    piotroski_f_score,
    distance_from_52w_high,
    rolling_ivol,
)


def _frame(value, index=None, columns=None):
    return pd.DataFrame([[value]], index=index, columns=columns)


def test_f_score_all_good_is_nine():
    fund = {
        "roa": _frame(0.10),
        "cfo": _frame(0.12),
        "delta_roa": _frame(0.01),
        "delta_leverage": _frame(-0.10),
        "delta_current_ratio": _frame(0.10),
        "equity_issued": _frame(-0.01),
        "delta_gross_margin": _frame(0.01),
        "delta_asset_turnover": _frame(0.01),
    }
    assert piotroski_f_score(fund).iloc[0, 0] == 9


def test_f_score_all_bad_is_zero():
    fund = {
        "roa": _frame(-0.10),
        "cfo": _frame(-0.12),
        "delta_roa": _frame(-0.01),
        "delta_leverage": _frame(0.10),
        "delta_current_ratio": _frame(-0.10),
        "equity_issued": _frame(0.10),
        "delta_gross_margin": _frame(-0.01),
        "delta_asset_turnover": _frame(-0.01),
    }
    assert piotroski_f_score(fund).iloc[0, 0] == 0


def test_distance_from_52w_high():
    idx = pd.date_range("2020-01-31", periods=5, freq="ME")
    prices = pd.DataFrame({"A": [1.0, 2.0, 3.0, 2.0, 1.0]}, index=idx)
    d = distance_from_52w_high(prices, window=3)
    assert np.isnan(d.iloc[0, 0]) and np.isnan(d.iloc[1, 0])
    np.testing.assert_allclose(d.iloc[2:, 0].values, [1.0, 2/3, 1/3])


def test_rolling_ivol_positive_and_warmup():
    rng = np.random.default_rng(1)
    T = 100
    f = pd.DataFrame({"F": rng.normal(0.001, 0.02, T)})
    ret = pd.DataFrame({"A": 1.0 * f["F"].values + rng.normal(0, 0.01, T)})
    ivol = rolling_ivol(ret, f, window=24)
    assert ivol.iloc[:23, 0].isna().all()
    assert ivol.iloc[23:, 0].notna().all()
    assert (ivol.iloc[23:, 0] > 0).all()
