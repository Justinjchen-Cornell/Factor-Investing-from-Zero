"""按股票代码列表下载日线数据到 data/cache/（不进 git，读者自用扩展）。

用法：
    python scripts/download_data.py --stocks 600519,000858
    python scripts/download_data.py --all-sample
    python scripts/download_data.py --start 2018-01-01 --end 2024-12-31 --stocks 600519
"""
from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache"


def download(code: str, start: str, end: str) -> pd.DataFrame:
    import sys as _sys
    from pathlib import Path as _Path
    _sys.path.insert(0, str(_Path(__file__).resolve().parent))
    from data_sources import fetch_daily
    return fetch_daily(code, start, end)


def main() -> None:
    parser = argparse.ArgumentParser(description="下载 A 股日线到 data/cache/（本地缓存，不进 git）")
    parser.add_argument("--stocks", type=str, default="", help="逗号分隔的股票代码，如 600519,000858")
    parser.add_argument("--all-sample", action="store_true", help="下载示例数据中的全部股票")
    parser.add_argument("--start", default="2018-01-01")
    parser.add_argument("--end", default=str(date.today()))
    args = parser.parse_args()

    if args.all_sample:
        codes = [p.stem for p in (ROOT / "data" / "sample" / "a_share_snapshot" / "daily").glob("*.csv")]
    elif args.stocks:
        codes = [c.strip() for c in args.stocks.split(",") if c.strip()]
    else:
        parser.error("必须提供 --stocks 或 --all-sample")

    out = CACHE / "daily"
    out.mkdir(parents=True, exist_ok=True)
    for code in codes:
        target = out / f"{code}.csv"
        if target.exists():
            print(f"[skip] {code} 已存在")
            continue
        try:
            df = download(code, args.start, args.end)
            df.to_csv(target, index=False)
            print(f"[ok] {code} ({len(df)} 行 -> {target})")
        except Exception as exc:  # noqa: BLE001
            print(f"[fail] {code}: {exc}")


if __name__ == "__main__":
    main()
