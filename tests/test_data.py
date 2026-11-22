"""第3章数据面板测试：形状、对齐、核心面板无缺失。"""
from factor_zero.data import load_ashare_panel


def test_load_ashare_panel_shapes_and_alignment():
    d = load_ashare_panel()
    n_dates, n_stocks = d["ret"].shape
    assert n_stocks >= 50
    assert n_dates >= 60
    for key in ["mktcap", "size", "bm", "roe", "investment", "turnover"]:
        assert d[key].shape == d["ret"].shape, f"{key} 形状不匹配"
        assert d[key].isna().sum().sum() == 0, f"{key} 不应有缺失"
    assert set(d["ret"].columns) == set(d["mktcap"].columns)
    assert len(d["market"]) >= n_dates - 1


def test_factor_returns_build():
    from factor_zero.factors import build_factor_returns
    d = load_ashare_panel()
    factors = build_factor_returns(d, n_groups=10)
    for col in ["MKT", "SMB", "HML", "WML", "RMW", "CMA", "TURN"]:
        assert col in factors.columns
        assert factors[col].notna().sum() > 30, f"{col} 有效样本太少"
