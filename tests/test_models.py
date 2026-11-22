"""第4章多因子模型测试：模型定义、测试资产、GRS 比较。"""
import pytest

from factor_zero.data import load_ashare_panel
from factor_zero.factors import build_factor_returns
from factor_zero.models import (
    MODEL_DEFINITIONS,
    model_factor_frame,
    build_test_assets,
    evaluate_model,
    compare_models,
)


@pytest.fixture(scope="module")
def panel():
    return load_ashare_panel()


@pytest.fixture(scope="module")
def factors(panel):
    return build_factor_returns(panel)


@pytest.fixture(scope="module")
def assets(panel):
    return build_test_assets(panel, n_groups=5)


def test_model_definitions_complete():
    for name, spec in MODEL_DEFINITIONS.items():
        assert spec.get("factors"), f"{name} 缺 factors"
        assert spec.get("note"), f"{name} 缺 note"


def test_model_factor_frame():
    import pandas as pd
    f = pd.DataFrame(columns=["MKT", "SMB", "HML", "WML", "RMW", "CMA", "TURN"])
    ff3 = model_factor_frame(f, "FF3")
    assert list(ff3.columns) == ["MKT", "SMB", "HML"]
    ff5 = model_factor_frame(f, "FF5")
    assert list(ff5.columns) == ["MKT", "SMB", "HML", "RMW", "CMA"]


def test_build_test_assets_shape(assets):
    assert assets.shape[1] == 15
    assert all(c.startswith(("BM_", "SIZE_", "MOM_")) for c in assets.columns)


def test_evaluate_model_keys(factors, assets):
    res = evaluate_model(factors, assets, "FF3")
    for key in ["model", "k", "grs_f", "grs_p", "mean_abs_alpha_ann", "avg_r2", "periods"]:
        assert key in res
    assert res["k"] == 3
    assert res["grs_f"] >= 0
    assert 0 <= res["grs_p"] <= 1
    assert res["periods"] > 30


def test_compare_models_shape(factors, assets):
    res = compare_models(factors, assets)
    assert len(res) == len(MODEL_DEFINITIONS)
    assert set(res.index) == set(MODEL_DEFINITIONS)
    assert (res["grs_f"] >= 0).all()
    assert ((res["grs_p"] >= 0) & (res["grs_p"] <= 1)).all()
