"""多因子模型定义与比较工具（第4章配套）。

模型因子集
----------
- FF3       : MKT + SMB + HML
- Carhart4  : FF3 + WML（动量）
- NovyMarx4 : MKT + HML + WML + RMW（市场/价值/动量/盈利）
- FF5       : MKT + SMB + HML + RMW + CMA
- HXZ4      : MKT + SMB + RMW + CMA（q-factor：市场/规模/盈利/投资）
- SY4       : MKT + SMB + RMW + WML（近似：RMW/WML 代理 MGMT/PERF）
- DHS3      : MKT + HML + WML（近似：HML/WML 代理 FIN/PEAD）

⚠️ SY4/DHS3 的真实因子（MGMT/PERF、FIN/PEAD）本仓库数据无法精确构造，
这里用现有因子做“近似代理”，只用于演示模型比较流程，不代表原模型。
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from factor_zero.regression import time_series_betas
from factor_zero.sorting import long_short_factor
from factor_zero.statistics import grs_test

MODEL_DEFINITIONS: dict[str, dict] = {
    "FF3": {"factors": ["MKT", "SMB", "HML"], "note": "Fama-French 三因子"},
    "Carhart4": {"factors": ["MKT", "SMB", "HML", "WML"], "note": "FF3 + 动量"},
    "NovyMarx4": {"factors": ["MKT", "HML", "WML", "RMW"], "note": "市场 + 价值 + 动量 + 盈利"},
    "FF5": {"factors": ["MKT", "SMB", "HML", "RMW", "CMA"], "note": "Fama-French 五因子"},
    "HXZ4": {"factors": ["MKT", "SMB", "RMW", "CMA"], "note": "q-factor：市场 + 规模 + 盈利 + 投资"},
    "SY4": {"factors": ["MKT", "SMB", "RMW", "WML"], "note": "近似：RMW/WML 代理 MGMT/PERF"},
    "DHS3": {"factors": ["MKT", "HML", "WML"], "note": "近似：HML/WML 代理 FIN/PEAD"},
}


def model_factor_frame(factors: pd.DataFrame, model: str) -> pd.DataFrame:
    """取出某个模型所需的因子收益列。"""
    if model not in MODEL_DEFINITIONS:
        raise KeyError(f"未知模型 {model}；可选 {list(MODEL_DEFINITIONS)}")
    cols = MODEL_DEFINITIONS[model]["factors"]
    missing = [c for c in cols if c not in factors.columns]
    if missing:
        raise KeyError(f"因子面板缺少列 {missing}")
    return factors[cols].copy()


def build_test_assets(panel: dict, n_groups: int = 5) -> pd.DataFrame:
    """构造 GRS 测试资产：BM / SIZE / MOM 各分 5 组，共 3×5 个组合。"""
    specs = {
        "BM": ("bm", True),
        "SIZE": ("size", False),
        "MOM": ("momentum", True),
    }
    pieces = []
    for prefix, (key, high_minus_low) in specs.items():
        _, port, _ = long_short_factor(
            panel[key], panel["ret"], n_groups=n_groups,
            high_minus_low=high_minus_low,
        )
        port = port.copy()
        port.columns = [f"{prefix}_{i}" for i in port.columns]
        pieces.append(port)
    return pd.concat(pieces, axis=1)


def evaluate_model(
    factors: pd.DataFrame, test_assets: pd.DataFrame, model: str
) -> dict:
    """用 GRS 检验评价一个多因子模型。

    返回：模型名、因子数、GRS F、p 值、平均 |alpha|（年化）、平均 R²、样本期数。
    """
    mf = model_factor_frame(factors, model)
    data = pd.concat([test_assets, mf], axis=1).dropna()
    y = data[test_assets.columns]
    x = data[mf.columns]
    alphas, betas, resid = time_series_betas(y, x)
    F, p = grs_test(alphas.to_numpy(), resid.to_numpy(), x.to_numpy())
    r2 = 1 - resid.var() / y.var()
    return {
        "model": model,
        "k": len(mf.columns),
        "grs_f": float(F),
        "grs_p": float(p),
        "mean_abs_alpha_ann": float(alphas.abs().mean() * 12),
        "avg_r2": float(r2.mean()),
        "periods": int(len(y)),
    }


def compare_models(factors: pd.DataFrame, test_assets: pd.DataFrame) -> pd.DataFrame:
    """对 MODEL_DEFINITIONS 里的全部模型做 GRS 比较。"""
    rows = [evaluate_model(factors, test_assets, name) for name in MODEL_DEFINITIONS]
    return pd.DataFrame(rows).set_index("model")
