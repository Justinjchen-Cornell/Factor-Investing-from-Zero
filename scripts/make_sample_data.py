"""生成并刷新示例数据（进 git，读者离线可用）。

教学小样本：确定性合成（对齐原书表 2.1 结构：4 只股票 × 2 个因子）。
A股快照：优先用 akshare 下载真实数据；任一环节失败则回退为合成数据，
manifest.json 记录实际来源，保证管道永不空跑。
"""
from __future__ import annotations

import json
import random
import time
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "sample"

# 90 只 A 股：覆盖大/中/小市值与主要行业（不含科创板 688 与 ST）
STOCKS = [
    "600519", "601318", "600036", "000858", "601398", "600900", "601899",
    "000333", "600030", "000651", "601166", "600276", "002594", "300750",
    "601012", "000568", "600809", "600887", "000001", "600000", "601088",
    "600028", "601857", "600050", "000725", "601668", "600031", "000002",
    "002415", "300059", "601888", "600585", "601601", "600048", "000063",
    "002475", "300760", "603259", "600690", "002304", "300124", "002230",
    "600570", "300015", "002714", "600438", "601100", "300308", "002371",
    "002352", "600741", "000100", "600346", "002027", "601989", "600703",
    "002460", "300274", "002049", "600745", "603501", "002821", "300347",
    "601636", "600188", "601225", "600025", "000983", "600919", "601916",
    "600926", "601995", "300782", "002050", "600183", "002236", "600406",
    "000338", "600309", "601633", "000625", "600104", "601728", "000776",
    "600999", "601688", "601211",
]
START, END = "2018-01-01", "2024-12-31"


def make_teaching_sample() -> pd.DataFrame:
    """原书表 2.1 风格：4 只股票在两个因子上的暴露 + 特质性风险。"""
    return pd.DataFrame({
        "asset": ["stock_1", "stock_2", "stock_3", "stock_4"],
        "factor_a_exposure": [1.2, 1.1, 0.9, 0.8],
        "factor_b_exposure": [0.8, 1.3, -0.8, -1.3],
        "idio_risk": [0.020, 0.015, 0.012, 0.010],
    })


def fetch_daily_chain(code: str) -> pd.DataFrame:
    """使用统一数据源兜底链获取日线（东财→efinance→新浪→腾讯→腾讯直连）。"""
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from data_sources import fetch_daily
    return fetch_daily(code, START, END)


def fetch_fundamentals_chain() -> pd.DataFrame:
    """全市场估值快照（新浪 stock_zh_a_spot）：pb / 总市值。"""
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from data_sources import fetch_fundamentals_snapshot
    return fetch_fundamentals_snapshot()


def synth_daily(code: str, seed: int) -> pd.DataFrame:
    """合成日线：几何随机游走 + 轻微趋势，保证确定性可复现。"""
    rng = np.random.default_rng(seed)
    dates = pd.bdate_range(START, END)
    n = len(dates)
    rets = rng.normal(0.0003, 0.022, n) * (1 + 0.001 * np.arange(n) / n)
    close = 20.0 * np.exp(np.cumsum(rets))
    open_ = close * (1 + rng.normal(0, 0.004, n))
    high = np.maximum(open_, close) * (1 + np.abs(rng.normal(0, 0.006, n)))
    low = np.minimum(open_, close) * (1 - np.abs(rng.normal(0, 0.006, n)))
    volume = rng.integers(50_000, 5_000_000, n)
    return pd.DataFrame({
        "date": dates, "open": open_, "high": high, "low": low,
        "close": close, "volume": volume,
    })


def synth_fundamentals(codes: list[str]) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    rows = []
    for code in codes:
        dates = pd.bdate_range(START, END, freq="ME")
        pb = np.clip(rng.lognormal(0.0, 0.5, len(dates)), 0.3, 20.0)
        mv = np.clip(rng.lognormal(23.0, 1.2, len(dates)), 1e9, 5e12)
        rows.append(pd.DataFrame({"stock": code, "date": dates, "pb": pb, "total_mv": mv}))
    return pd.concat(rows, ignore_index=True)


def main() -> None:
    random.seed(2026)
    SAMPLE.mkdir(parents=True, exist_ok=True)
    daily_dir = SAMPLE / "a_share_snapshot" / "daily"
    daily_dir.mkdir(parents=True, exist_ok=True)

    # 1) 教学小样本
    make_teaching_sample().to_csv(SAMPLE / "teaching_sample.csv", index=False)

    # 2) A股快照：真实数据兜底链，全部失败回退合成
    source = "real"
    fund_frames, ok_codes = [], []
    try:
        for code in STOCKS:
            try:
                df = fetch_daily_chain(code)
                if len(df) < 1200:  # 数据量不足视为失败
                    raise ValueError(f"{code} 数据量不足")
                df.to_csv(daily_dir / f"{code}.csv", index=False)
                ok_codes.append(code)
                print(f"[real] {code} ok ({len(df)} 行)")
            except Exception as exc:  # noqa: BLE001 —— 单只失败不中断
                print(f"[real] {code} 失败: {exc}")
        if len(ok_codes) < 50:
            raise RuntimeError(f"真实数据仅成功 {len(ok_codes)} 只，不足 50，回退合成")
        try:
            fund_frames = [fetch_fundamentals_chain(ok_codes)]
        except Exception as exc:  # noqa: BLE001
            print(f"[warn] 估值快照失败（{exc}），基本面用合成补")
            fund_frames = [synth_fundamentals(ok_codes)]
    except Exception as exc:  # noqa: BLE001
        print(f"[fallback] 使用合成数据: {exc}")
        source = "synthetic"
        fund_frames, ok_codes = [], []
        for i, code in enumerate(STOCKS):
            df = synth_daily(code, seed=1000 + i)
            df.to_csv(daily_dir / f"{code}.csv", index=False)
            ok_codes.append(code)
        fund_frames = [synth_fundamentals(ok_codes)]

    fund = pd.concat(fund_frames, ignore_index=True)
    fund.to_csv(SAMPLE / "a_share_snapshot" / "fundamentals.csv", index=False)

    (SAMPLE / "manifest.json").write_text(json.dumps({
        "project": "Factor-Investing-from-Zero",
        "source": source,
        "generated_at": date.today().isoformat(),
        "stock_count": len(ok_codes),
        "start": START,
        "end": END,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"完成：source={source}, 股票数={len(ok_codes)}")


if __name__ == "__main__":
    main()
