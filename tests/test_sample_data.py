"""示例数据完整性测试：数据管道产出的文件必须满足课程使用约定。"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "sample"


def test_manifest_exists():
    assert (SAMPLE / "manifest.json").exists()
    meta = json.loads((SAMPLE / "manifest.json").read_text(encoding="utf-8"))
    assert meta["source"] in {"akshare", "synthetic", "real"}
    assert meta["stock_count"] >= 50


def test_teaching_sample_schema():
    df = pd.read_csv(SAMPLE / "teaching_sample.csv")
    assert list(df.columns) == ["asset", "factor_a_exposure", "factor_b_exposure", "idio_risk"]
    assert len(df) == 4
    assert df["factor_b_exposure"].sum() == 0, "表2.1中股票3、4在因子B上暴露应相互对冲"


def test_a_share_daily_prices_schema():
    daily = SAMPLE / "a_share_snapshot" / "daily"
    csvs = sorted(daily.glob("*.csv"))
    assert len(csvs) >= 50, f"至少50只股票的日线数据，实际 {len(csvs)}"
    df = pd.read_csv(csvs[0])
    for col in ["date", "open", "high", "low", "close", "volume"]:
        assert col in df.columns, f"缺少列 {col}"
    assert df["close"].notna().all()
    assert df["date"].is_monotonic_increasing


def test_a_share_fundamentals_schema():
    fund = pd.read_csv(SAMPLE / "a_share_snapshot" / "fundamentals.csv")
    # 注意：脚本中已将 akshare 的 trade_date 重命名为 date，两处保持一致
    assert {"stock", "trade_date", "pb", "pe", "total_mv"}.issubset(fund.columns)
    assert fund["pb"].notna().any(), "pb 不应全为空"
