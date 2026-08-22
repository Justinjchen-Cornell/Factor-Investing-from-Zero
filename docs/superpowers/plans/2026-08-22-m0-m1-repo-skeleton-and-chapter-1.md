# M0+M1 仓库骨架与第1章 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: 使用 superpowers:executing-plans 逐任务执行本计划。步骤用 `- [ ]` 复选框跟踪进度。

**Goal:** 建立 `Factor-Investing-from-Zero` 仓库骨架（README/LICENSE/依赖/数据管道/示例数据/冒烟测试），并交付第1章"因子投资基础"完整三件套（讲义+notebook+练习），验证课程模板。

**Architecture:** 仓库 = 课程内容（chapters/）+ 工具库（src/factor_zero/）+ 数据管道（scripts/ + data/）+ 质量护栏（tests/）。第1章 notebook 用数值模拟把"式(1.3) 统一视角"（E[R]=βλ+α）和"式(1.6) 协方差分解"变成可运行代码；示例数据含教学小样本（书表2.1风格）与 A 股快照（akshare 实下+合成兜底），全部进 git 保证离线可复现。

**Tech Stack:** Python 3.10+（本机 3.14）、pandas 2.3.3、numpy 2.5.0、scipy 1.18.0、statsmodels 0.14.6、matplotlib 3.11.0、akshare 1.18.64、nbformat 5.10.4、nbclient 0.11.0、pytest 9.1.1。

## Global Constraints

- 所有内容**原创讲解**，不复制原书文字；README 需含版权声明。
- 讲义模板标记：`🎯 本章目标`、`📚 先修要求`、`📖 正文`、`📋 本章小结`、`✅ 检查站`。
- 每章三件套：`README.md` + `notebooks/` + `exercises/solutions/`。
- `data/sample/` 进 git（离线可跑）；`data/cache/` 在 .gitignore 中。
- `requirements.txt` 全部依赖锁定 `==` 版本。
- 完成标准：`pytest` 全绿；所有 notebook 用 nbclient 执行通过；每任务独立 commit。
- 中文为主、术语中英对照；顶层 README 双语。
- git 分支 `main`；提交者已配置 `Justinjchen-Cornell`。

---

### Task 1: 项目基础文件（.gitignore / requirements.txt / LICENSE / .gitattributes）

**Files:**
- Create: `.gitignore`
- Create: `.gitattributes`
- Create: `requirements.txt`
- Create: `LICENSE`

**Interfaces:**
- Consumes: 无（首任务）
- Produces: Task 2 的结构测试依赖这四个文件存在；`requirements.txt` 是全项目依赖清单

- [x] **Step 1: 写入 `.gitignore`**

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
venv/

# Jupyter
.ipynb_checkpoints/

# 本项目
data/cache/
*.log
```

- [x] **Step 2: 写入 `.gitattributes`（统一 LF，避免 Windows CRLF 噪音）**

```gitattributes
* text=auto eol=lf
*.png binary
```

- [x] **Step 3: 写入 `requirements.txt`（锁定本机已验证版本）**

```
pandas==2.3.3
numpy==2.5.0
scipy==1.18.0
statsmodels==0.14.6
matplotlib==3.11.0
akshare==1.18.64
nbformat==5.10.4
nbclient==0.11.0
pytest==9.1.1
```

- [x] **Step 4: 写入 `LICENSE`（MIT）**

```
MIT License

Copyright (c) 2026 Justin Chen (Justinjchen-Cornell)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [x] **Step 5: 验证并提交**

Run: `git add .gitignore .gitattributes requirements.txt LICENSE && git commit -m "chore: add project base files (gitignore, license, requirements)"`
Expected: commit 成功，`git status` 干净。

---

### Task 2: 课程结构冒烟测试 + factor_zero 包骨架

**Files:**
- Create: `tests/test_course_structure.py`
- Create: `src/factor_zero/__init__.py`

**Interfaces:**
- Consumes: Task 1 的四个基础文件
- Produces: 结构测试将成为全项目常驻护栏（后续每章都受其约束）；`factor_zero` 是第2章起工具库的包根

- [x] **Step 1: 写入测试（先写测试，TDD）**

```python
"""课程结构冒烟测试：保证仓库骨架与每章「三件套」模板不退化。

这是本项目的常驻护栏——任何里程碑都不得破坏它。
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_repo_skeleton_files_exist():
    for name in [".gitignore", ".gitattributes", "requirements.txt", "LICENSE", "README.md"]:
        assert (ROOT / name).exists(), f"缺少顶层文件 {name}"


def test_requirements_pins_versions():
    reqs = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    pinned = [ln for ln in reqs.splitlines() if ln.strip() and not ln.strip().startswith("#")]
    assert pinned, "requirements.txt 不应为空"
    assert all("==" in ln for ln in pinned), "所有依赖必须锁定版本 (==)"


def test_readme_has_required_sections():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for marker in ["TL;DR", "学习路径", "章节导航", "快速开始", "延伸阅读", "版权"]:
        assert marker in readme, f"README 缺少「{marker}」"


def test_chapters_dir_exists():
    assert (ROOT / "chapters").is_dir(), "缺少 chapters/ 目录"


def test_each_existing_chapter_has_three_part_template():
    chapters = sorted((ROOT / "chapters").glob("0*/"))
    if not chapters:
        return  # M0 阶段尚无章节；M1 起由 test_chapter_01_present 强制至少一章
    for ch in chapters:
        assert (ch / "README.md").exists(), f"{ch.name} 缺讲义 README.md"
        assert (ch / "notebooks").is_dir(), f"{ch.name} 缺 notebooks/"
        assert (ch / "exercises").is_dir(), f"{ch.name} 缺 exercises/"
        assert (ch / "exercises" / "solutions").is_dir(), f"{ch.name} 缺 exercises/solutions/"


def test_chapter_01_present():
    ch01 = ROOT / "chapters" / "01-factor-basics"
    assert ch01.is_dir(), "第1章 chapters/01-factor-basics/ 尚未创建"


def test_chapter_lecture_has_template_markers():
    ch01 = ROOT / "chapters" / "01-factor-basics"
    readme = (ch01 / "README.md").read_text(encoding="utf-8")
    for marker in ["🎯", "📚", "📖", "📋", "✅"]:
        assert marker in readme, f"第1章讲义缺少模板标记 {marker}"
```

- [x] **Step 2: 写入 `src/factor_zero/__init__.py`**

```python
"""factor_zero —— 从零开始学因子：方法实现工具库。

本包随课程章节逐步实现（排序法/回归/GMM 等），
每章的 notebook 与练习均可 `import factor_zero` 使用。
"""
```

- [x] **Step 3: 运行测试，确认"预期失败"集合**

Run: `python -m pytest tests/test_course_structure.py -v`
Expected: 5 个失败（README.md 缺失、chapters/ 缺失、第1章缺失、讲义标记缺失 —— 均为**预期失败**，由 Task 5/6 修复）；`test_repo_skeleton_files_exist` 与 `test_requirements_pins_versions` 通过。

- [x] **Step 4: 提交**

Run: `git add tests/test_course_structure.py src/factor_zero/__init__.py && git commit -m "test: add course structure smoke tests and factor_zero package skeleton"`
Expected: 提交成功。失败测试在 Task 5/6 中修复后全绿。

---

### Task 3: 示例数据生成（教学小样本 + A股快照，akshare 实下 + 合成兜底）

**Files:**
- Create: `scripts/make_sample_data.py`
- Create: `tests/test_sample_data.py`
- Generate: `data/sample/teaching_sample.csv`、`data/sample/a_share_snapshot/daily/*.csv`、`data/sample/a_share_snapshot/fundamentals.csv`、`data/sample/manifest.json`

**Interfaces:**
- Consumes: 无（直接调 akshare / numpy）
- Produces: `teaching_sample.csv`（列：asset, factor_a_exposure, factor_b_exposure, idio_risk）—— 第1章 notebook 与第2章排序法教学使用；`a_share_snapshot/` —— 第3章起因子实证使用；`manifest.json` 记录数据来源与生成时间

- [x] **Step 1: 先写数据测试（TDD）**

```python
"""示例数据完整性测试：数据管道产出的文件必须满足课程使用约定。"""
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "data" / "sample"


def test_manifest_exists():
    assert (SAMPLE / "manifest.json").exists()
    meta = json.loads((SAMPLE / "manifest.json").read_text(encoding="utf-8"))
    assert meta["source"] in {"akshare", "synthetic"}
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
    assert {"stock", "date", "pb", "total_mv"}.issubset(fund.columns)
    assert fund["pb"].notna().any(), "pb 不应全为空"
```

- [x] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_sample_data.py -v`
Expected: 全部 FAIL（`data/sample/` 尚不存在）。

- [x] **Step 3: 写入 `scripts/make_sample_data.py`**

```python
"""生成并刷新示例数据（进 git，读者离线可用）。

教学小样本：确定性合成（对齐原书表 2.1 结构：4 只股票 x 2 个因子）。
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


def fetch_akshare_daily(code: str) -> pd.DataFrame:
    """akshare 日线；失败抛异常由上层兜底。"""
    import akshare as ak

    df = ak.stock_zh_a_hist(
        symbol=code, period="daily",
        start_date=START.replace("-", ""), end_date=END.replace("-", ""),
        adjust="qfq",
    )
    return pd.DataFrame({
        "date": pd.to_datetime(df["日期"]),
        "open": df["开盘"],
        "high": df["最高"],
        "low": df["最低"],
        "close": df["收盘"],
        "volume": df["成交量"],
    }).sort_values("date").reset_index(drop=True)

def fetch_akshare_fundamentals(code: str) -> pd.DataFrame:
    """akshare 估值指标（乐咕乐股）：pb / 总市值 等。"""
    import akshare as ak

    df = ak.stock_a_indicator_lg(symbol=code)
    df = df.rename(columns={"trade_date": "date"})
    df = df[["date", "pb", "total_mv"]].dropna(subset=["pb"])
    df["stock"] = code
    return df[["stock", "date", "pb", "total_mv"]].sort_values("date").reset_index(drop=True)


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

    # 2) A股快照：akshare 实下，失败回退合成
    source = "akshare"
    fund_frames, ok_codes = [], []
    try:
        for code in STOCKS:
            try:
                df = fetch_akshare_daily(code)
                fund = fetch_akshare_fundamentals(code)
                if len(df) < 1200 or len(fund) < 60:  # 数据量不足视为失败
                    raise ValueError(f"{code} 数据量不足")
                df.to_csv(daily_dir / f"{code}.csv", index=False)
                fund_frames.append(fund)
                ok_codes.append(code)
                print(f"[akshare] {code} ok ({len(df)} 行)")
            except Exception as exc:  # noqa: BLE001 —— 单只失败不中断
                print(f"[akshare] {code} 失败: {exc}")
            time.sleep(0.15)
        if len(ok_codes) < 50:
            raise RuntimeError(f"akshare 仅成功 {len(ok_codes)} 只，不足 50，回退合成")
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
```

- [x] **Step 4: 运行生成脚本**

Run: `python scripts/make_sample_data.py`
Expected: 输出每只股票 `[akshare] xxx ok (N 行)`，结尾 `完成：source=akshare, 股票数≈90`；`data/sample/` 下生成 4 类文件。若网络失败则 `source=synthetic`（同样满足测试）。

- [x] **Step 5: 运行数据测试确认通过**

Run: `python -m pytest tests/test_sample_data.py -v`
Expected: 4 个测试全部 PASS。

- [x] **Step 6: 提交**

Run: `git add scripts/make_sample_data.py tests/test_sample_data.py data/sample && git commit -m "feat: add sample data pipeline and generated sample datasets"`
Expected: 提交成功。⚠️ 确认 `data/cache/` 未被加入（.gitignore 生效）。

---

### Task 4: 全市场下载脚本（供读者扩展）

**Files:**
- Create: `scripts/download_data.py`

**Interfaces:**
- Consumes: `data/cache/`（.gitignore 已排除）
- Produces: `data/cache/daily/{code}.csv` —— 读者自行扩展数据时使用；与本课程代码接口一致（列：date, open, high, low, close, volume）

- [x] **Step 1: 写入脚本**

```python
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
    import akshare as ak

    df = ak.stock_zh_a_hist(
        symbol=code, period="daily",
        start_date=start.replace("-", ""), end_date=end.replace("-", ""),
        adjust="qfq",
    )
    return pd.DataFrame({
        "date": pd.to_datetime(df["日期"]),
        "open": df["开盘"], "high": df["最高"],
        "low": df["最低"], "close": df["收盘"], "volume": df["成交量"],
    }).sort_values("date").reset_index(drop=True)


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
```

- [x] **Step 2: 验证 CLI**

Run: `python scripts/download_data.py --help`
Expected: 打印 usage 说明，退出码 0。

- [x] **Step 3: 提交**

Run: `git add scripts/download_data.py && git commit -m "feat: add full-market download script for readers"`
Expected: 提交成功。

---

### Task 5: 双语首页 README.md

**Files:**
- Create: `README.md`

**Interfaces:**
- Consumes: Task 1 基础文件；Task 2 的 `test_readme_has_required_sections` 将在此修复
- Produces: 项目门面（GitHub 首页渲染）；含"章节导航"供 M1 后章节链接持续更新

- [x] **Step 1: 写入 README.md**

```markdown
# Factor-Investing-from-Zero · 从零开始学因子

> 一本把《因子投资：方法与实践》讲成"开源课程"的仓库 —— 每一章都有讲义、可运行的代码和练习。
> *An open course built from "Factor Investing: Methods and Practice" — lecture + code + exercises for every chapter.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Chapters](https://img.shields.io/badge/Chapters-7-green)
![Data](https://img.shields.io/badge/Data-A%E8%82%A1%20sample%20offline--ready-brightgreen)

---

## TL;DR / 一句话

**因子是资产收益率的"营养成分"：一只股票 = 一组因子暴露 x 因子溢价 + 独有的定价误差。**
**A stock is a basket of factor exposures: E[R] = βλ + α.**

本仓库用"比喻式精讲 + 可运行代码 + 检查站练习"三件套，带你从零认识因子、学会方法、读懂 A 股实证、最终上手实践。

---

## 学习路径 / Learning Path

| 阶段 | 章节 | 你将学会 |
|---|---|---|
| 基础 | [第1章 因子投资基础](chapters/01-factor-basics/) | 一个公式看懂因子/多因子模型/异象 |
| 方法论 | [第2章 因子投资方法论](chapters/02-methodology/) | 排序法、Fama-MacBeth 回归、GRS、Newey-West…… |
| 实证 | [第3章 主流因子解读](chapters/03-mainstream-factors/) | A股七大因子的来龙去脉与实证 |
| 实证 | [第4章 多因子模型](chapters/04-multi-factor-models/) | 七大模型 + A股被定价的因子 |
| 实证 | [第5章 异象研究](chapters/05-anomalies/) | F-Score、基本面锚定反转、特质波动率 |
| 进阶 | [第6章 因子研究现状](chapters/06-current-research/) | p-hacking、因子动物园、行为金融、机器学习 |
| 实践 | [第7章 因子投资实践](chapters/07-practice/) | 组合优化、Smart Beta、风格归因、结业项目 |

> 进度：📗 第1章已发布 ｜ 📙 第2~7章建设中

---

## 快速开始 / Quick Start

```bash
git clone https://github.com/Justinjchen-Cornell/Factor-Investing-from-Zero.git
cd Factor-Investing-from-Zero
pip install -r requirements.txt
jupyter lab chapters/01-factor-basics/notebooks/
```

所有示例数据已内置（`data/sample/`），**无需联网即可跑通全部课程代码**。

## 数据说明 / Data

- `data/sample/`：预生成示例数据（教学小样本 + A股快照，进 git，离线可用）
- `data/cache/`：可选下载的全市场数据（`python scripts/download_data.py --all-sample`）

## 延伸阅读 / Further Reading

- 原书《因子投资：方法与实践》及其参考文献（石川、刘洋溢、连祥斌，电子工业出版社 2020）
- 原书配套网站：https://factorwar.com
- [Microsoft qlib](https://github.com/microsoft/qlib) —— AI 量化平台（进阶机器学习因子研究）
- [QuantSkills](https://github.com/quantskills) —— 因子分析 Agent 技能
- [alphalens-reloaded](https://github.com/stefan-jansen/alphalens-reloaded) —— IC/分位分析参考实现
- [PyPortfolioOpt](https://github.com/robertmartin8/PyPortfolioOpt) —— 组合优化参考

## 版权声明 / Copyright

本项目是《因子投资：方法与实践》（石川、刘洋溢、连祥斌著，电子工业出版社，2020）的
**学习笔记、代码复现与原创讲解**，不复制原书正文；原书版权归作者与出版社所有。
示例数据仅含公开行情与财报字段，仅用于教学。
*This project contains original lecture notes, code reproductions and interpretations based on the book
"Factor Investing: Methods and Practice". All rights of the book belong to its authors and publisher.*
```

- [x] **Step 2: 运行结构测试**

Run: `python -m pytest tests/test_course_structure.py -v`
Expected: `test_repo_skeleton_files_exist`、`test_requirements_pins_versions`、`test_readme_has_required_sections` 通过；章节相关 3 个测试仍失败（预期，Task 6 修复）。

- [x] **Step 3: 提交**

Run: `git add README.md && git commit -m "docs: add bilingual README homepage"`
Expected: 提交成功。

---

### Task 6: 第1章讲义 chapters/01-factor-basics/README.md

**Files:**
- Create: `chapters/01-factor-basics/README.md`
- Create: `chapters/01-factor-basics/notebooks/.gitkeep`（目录占位，Task 7 放真 notebook）
- Create: `chapters/01-factor-basics/exercises/solutions/.gitkeep`

**Interfaces:**
- Consumes: Task 2 的讲义标记测试
- Produces: 课程模板范本（M1 之后的章节照此撰写）；notebook 与练习的"母版"

- [x] **Step 1: 写入讲义（原创讲解 + 比喻式，对照原书第1章）**

```markdown
# 第1章 因子投资基础

> 对应原书：第1章（1.1~1.4 节）｜ 配套代码：`notebooks/01.1-unified-view.ipynb` ｜ 练习：`exercises/`

## 🎯 本章目标

学完本章，你将能够：

1. 用一个公式（E[R] = βλ + α）说清楚"因子、多因子模型、异象"三者的关系；
2. 说出因子的严格定义与两个必要条件，并用类比向别人解释"什么是因子"；
3. 区分学术界眼中的"定价因子/异象因子"与业界眼中的"因子"；
4. 解释"截面角度 vs 时序角度"，以及因子模型为什么是协方差矩阵的"降维"；
5. 梳理因子投资的学术起源（CAPM → APT → FF3 → GMM）与业界发展（风格指数 → Smart Beta ETF）；
6. 在 notebook 中用代码重现式(1.3) 与式(1.6) 的数值世界。

## 📚 先修要求

- Python 基础（能跑 notebook、会看 pandas DataFrame）
- 一点概率统计（均值、方差、协方差、回归的概念即可，公式不用会推）
- 无需金融学背景 —— 本章就是从零建立金融学世界观

## 📖 正文

### 1.1 一个公式：因子投资的"世界观"

#### 1.1.1 从 CAPM 说起

20 世纪 60 年代，资本资产定价模型（CAPM）第一次用数学画出了"风险-收益"关系：

    E[Ri] - Rf = βi x (E[RM] - Rf)          (1.1)

- Ri：资产 i 的收益率；Rf：无风险收益率（如国债利率）；RM：市场组合收益率；
- βi = cov(Ri, RM)/var(RM)：资产对市场风险的**暴露**——市场涨 1%，它平均跟涨多少。

> 🍚 **食物类比**：米饭、肉、奶看起来是三种食物，但本质上都是"碳水+蛋白质+脂肪"的组合。
> 股票也一样——形态上千差万别，收益本质上都能归结为有限几个**因子**（营养成分）的组合。
> 你吃多少营养（β）、营养值多少钱（λ），决定了你的身体（收益）如何。

但市场只有一个"营养"吗？不是。便宜股、小盘股长期跑赢，说明还有其他被定价的风险。
Ross (1976) 提出套利定价理论（APT），把公式推广成**多因子模型**：

    E[Ri] = βi1λ1 + βi2λ2 + … + βiKλK = βi·λ   (1.2)

- βi：资产在 K 个因子上的**暴露**（你配了多少这种风险）；
- λ：因子的**预期收益率**（因子溢价）——市场为承受这种风险支付的"工资"。

#### 1.1.2 定价误差 α 与"统一视角"

现实中等式(1.2) 两边往往不相等，多出来的部分叫**定价误差 αi**：

    E[Ri] = βi·λ + αi                       (1.3)

**这就是全书的地图。** 因子投资的一切内容都围绕式(1.3) 展开：

| 成分 | 叫什么 | 通俗理解 |
|---|---|---|
| λ（连同β） | 因子 + 多因子模型 | 市场"为什么"付钱给你——系统性风险的补偿 |
| αi | 异象（anomaly） | 市场"付错的钱"——错误定价带来的超额收益 |

**三个关键定义（背下来）：**

1. **因子**：众多资产共同暴露的某种系统性风险，是收益率背后的驱动力；因子收益率是这种风险的风险溢价，是这些资产的**共性收益**。
2. **多因子模型**：若干因子放在一起构成定价模型。两个选择原则：① 因子间要**低相关**（高度相关的因子代表同一类风险）；② **简约法则**——主流模型通常只有 3~5 个因子。
3. **异象**：给定多因子模型后，若按某特征构建的多空组合仍能获得**模型解释不了的显著正收益（α > 0）**，该组合就是异象，构建它的变量叫**异象变量**。

> 🎮 **游戏类比**：因子 = 角色的属性（攻击/暴击/攻速）。预期输出 = 属性值（β）× 属性价格（λ）。
> 同样的配装，有人打出了"额外伤害"——那部分就是 α（异象）。学术界想搞清楚：这 α 是因为
> 我们漏看了某种属性（风险），还是系统有 Bug（错误定价）？

#### 1.1.3 学术界 vs 业界：同一个"因子"，两种用法

- **学术界**严格区分：模型里的叫**定价因子**，α 代表的是**异象因子**；关心"这因子能否解释收益率的截面差异"。
- **业界**不区分，都叫因子：只关心**扣掉交易成本后能不能赚钱**。
- 记住这句话：**一个因子是异象还是定价因子，取决于你用什么模型去解释它。**

#### 1.1.4 截面角度 vs 时序角度

- **截面（cross-section）**：为什么北京的房子比鹤岗贵？——研究**不同资产**预期收益率的差异（β 和 λ 的关系）。多因子模型是"关于均值的模型"。
- **时序（time-series）**：北京房价今年比去年涨了多少？——研究**同一资产**收益率随时间的变化。衍生出两大主题：
  1. **方差模型**：对式(1.3) 取协方差矩阵，得到

        Σ = βΣλβ′ + Σε                       (1.6)

     它是因子投资的"降维魔法"：3000 支股票的协方差矩阵是 3000×3000，但因子只有 K 个，
     **通过因子算协方差，把 3000×3000 变成 K×K**。业界著名的 Barra 模型（CNE6：1 个国家因子 +
     9 个风格因子 + 行业因子）就是这么干的。
  2. **因子择时**：因子收益时好时坏，能不能"好使的时候多配、不好使的时候躲开"？（第7章详解）

### 1.2 因子投资的学术起源

- **1934** Graham & Dodd《证券分析》：价值溢价的雏形。
- **1960s** CAPM（Treynor/Sharpe/Lintner/Mossin）→ **1976** APT（Ross）：因子分析的工具箱。
- **1970s** 异象爆发：Basu (1977) 便宜股效应、Banz (1981) 小市值效应——CAPM 解释不了它们。
- **Fama 的贡献**：① 联合假说（Fama 1970）——要检验市场是否有效，必须先有正确的定价模型；
  ② Fama-MacBeth 回归（1973）——检验 CAPM 的统计方法，如今是因子研究最常用的工具；
  ③ Fama-French 三因子模型（1993）——市场 + 规模(SMB) + 价值(HML)，多因子模型的鼻祖。
- **Hansen 的贡献**：广义矩估计 GMM（1982）——检验基于消费的模型（CCAPM）与多因子模型的强大工具。
- **Shiller 的贡献**：噪音交易者模型（1984）——行为金融学的起点：价格过度波动来自非理性行为。
- 三位大师共享 **2013 年诺贝尔经济学奖**。

**"因子动物园"警告（记住这三个数字）：**

| 事实 | 出处 |
|---|---|
| 学术界已挖出 **400+** 个因子，多数是数据窥探（先看数据再编故事）的产物 | Cochrane (2011) |
| 因子显著性的 t 值门槛被抬高：**2.0 → 3.0** | Harvey et al. (2016) |
| 进一步抬高到 **3.4**；97 个因子发表后收益平均**衰减 50%+** | Chordia et al. (2020)、McLean & Pontiff (2016) |

### 1.3 因子投资的业界发展

**管理人视角（5 个关键词）：**
1. **收益预测 vs 风险管理**：因子模型既能选股（截面），也能算协方差控风险（时序）。
2. **因子拥挤**：用的人越多，因子越不赚钱；2007 年 8 月美股量化基金集体清仓引发流动性危机。
3. **因子择时**：两派之争——Research Affiliates 主张"按因子估值"择时，AQR 主张"按因子动量"择时。
4. **α vs β 收益**：管理人的超额收益中约 **80% 来自因子暴露（β）**，只有 20% 来自真正的 α 能力。
5. **创新**：另类数据（舆情/专利/新闻）+ 机器学习 = 新的收益源。

**投资者视角：**
- 1987 年 Russell 推出最早的风格指数（价值/成长）→ 1992 年先锋推出价值指数基金 →
  今天 Smart Beta ETF 规模已超 **6500 亿美元**（2018 年估算）。
- ⚠️ 但选 ETF 很难：Choi et al. (2009) 实验发现，连金融专业学生都会忽视费率、追逐历史高收益的 ETF。

### 1.4 本书（本项目）的地图

第1~2章 打地基（世界观 + 方法论）→ 第3~5章 A股实证（因子/多因子模型/异象）→ 第6~7章 进阶（研究现状 + 投资实践）。
**全书第2~6章都嵌套在第1章的式(1.3) 框架内**——这就是"统一视角"。

## 📋 本章小结

| 概念 | 一句话 |
|---|---|
| 因子 | 众多资产共同暴露的系统性风险，长期有正的风险溢价（共性收益） |
| 因子暴露 β | 资产在该风险上的敞口大小 |
| 因子溢价 λ | 市场为承受该风险支付的预期回报 |
| 多因子模型 | βλ 部分：若干低相关因子组成的定价模型（3~5 个，简约法则） |
| 异象 α | 模型解释不了、显著大于零的超额收益 |
| 统一视角 | 一切因子投资内容 = 式(1.3) 的 λ 部分或 α 部分，截面或时序角度 |
| 方差模型 | Σ = βΣλβ′ + Σε：因子模型 = 协方差矩阵降维（Barra） |
| 数据窥探 | 先看数据再提假设 → 假因子泛滥 → 因子动物园 |

## ✅ 检查站（自测题）

1. 一句话说清：因子、多因子模型、异象三者的区别和关系。
2. 为什么说因子投资的关键是式(1.3)？β 和 λ 各代表什么？
3. 学术界和业界对"因子"的看法有何分歧？分歧的根源是什么？
4. 为什么学术界挖出的 400+ 因子大多不可信？"数据窥探"是什么意思？
5. 用一句话解释：为什么说多因子模型是"降维"？（提示：式 1.6）
6. 管理人的超额收益中 α 和 β 大约各占多少？这对普通投资者有什么启示？

> 答案见 `exercises/solutions/`。本章配套代码见 `notebooks/01.1-unified-view.ipynb`——
> 用数字亲手验证 βλ+α 的世界。
```

- [x] **Step 2: 创建占位目录并运行结构测试**

Run: `mkdir -p chapters/01-factor-basics/notebooks chapters/01-factor-basics/exercises/solutions && touch chapters/01-factor-basics/notebooks/.gitkeep chapters/01-factor-basics/exercises/solutions/.gitkeep && python -m pytest tests/test_course_structure.py -v`
Expected: 结构测试全部通过（README 标记 ✓、第1章三件套 ✓）。Task 2 的预期失败至此全部修复。

- [x] **Step 3: 提交**

Run: `git add chapters/01-factor-basics && git commit -m "feat(ch1): add chapter 1 lecture (factor basics)"`
Expected: 提交成功。

---

### Task 7: 第1章 notebook（01.1-unified-view.ipynb）+ notebook 执行护栏

**Files:**
- Create: `scripts/build_notebooks.py`（notebook 构建器，后续章节复用此模式）
- Create: `chapters/01-factor-basics/notebooks/01.1-unified-view.ipynb`（由构建器生成）
- Create: `tests/test_notebooks.py`（执行护栏：所有 notebook 必须能跑通）

**Interfaces:**
- Consumes: `data/sample/teaching_sample.csv`（Task 3）
- Produces: 可执行 notebook（含图，演示式 1.3 与式 1.6）；后续每章的 notebook 都通过 `build_notebooks.py` 追加构建函数

- [x] **Step 1: 写入构建器 `scripts/build_notebooks.py`（含第1章 notebook 完整内容）**

```python
"""构建课程 notebooks（用 nbformat 生成 .ipynb，保证可复现）。

用法：python scripts/build_notebooks.py   # 构建全部
后续章节在文件末尾追加对应的 build_0X_Y() 函数即可。
"""
from __future__ import annotations

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]

MAGIC_SETUP = (
    "import numpy as np\nimport pandas as pd\nimport matplotlib.pyplot as plt\n\n"
    "# 数据目录：兼容从仓库根目录或 chapters/xx/notebooks 目录启动\n"
    "from pathlib import Path\n"
    "def _find_sample():\n"
    "    for p in [Path('data/sample'), Path.cwd().parents[2] / 'data' / 'sample']:\n"
    "        if p.exists():\n"
    "            return p\n"
    "    raise FileNotFoundError('找不到 data/sample，请从仓库根目录启动 notebook')\n"
    "SAMPLE = _find_sample()\n"
    "plt.rcParams['figure.dpi'] = 110"
)

def build_01_1() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    cells = []
    cells.append(nbf.v4.new_markdown_cell(
        "# 1.1 统一视角：用代码重现 E[R] = βλ + α\n\n"
        "对应原书第1章 1.1 节。本 notebook 的目标：\n\n"
        "1. 用教学小样本（4 只股票 × 2 个因子）计算预期收益 E[R] = βλ；\n"
        "2. 加入 α 制造一个「异象」，并在图上看出定价误差；\n"
        "3. 模拟因子收益率时序，验证协方差分解 Σ = βΣλβ′ + Σε。\n"
    ))
    cells.append(nbf.v4.new_code_cell(MAGIC_SETUP))
    cells.append(nbf.v4.new_markdown_cell(
        "## 第 0 步：加载教学小样本\n\n"
        "数据是原书表 2.1 的结构：4 只股票在因子 A、B 上的暴露（beta）与各自的特质性风险（idio risk）。"
    ))
    cells.append(nbf.v4.new_code_cell(
        "teach = pd.read_csv(SAMPLE / 'teaching_sample.csv')\nteach"
    ))
    cells.append(nbf.v4.new_markdown_cell(
        "## 第 1 步：预期收益 = 暴露 × 因子溢价\n\n"
        "设因子溢价（月均）：λ_A = 0.8%，λ_B = 0.4%。\n"
        "**预期收益 = 暴露矩阵 β 与溢价向量 λ 的矩阵乘法。**"
    ))
    cells.append(nbf.v4.new_code_cell(
        "lam = np.array([0.008, 0.004])  # 因子溢价 λ（月均）\n"
        "beta = teach[['factor_a_exposure', 'factor_b_exposure']].to_numpy()\n"
        "er_model = beta @ lam  # 多因子模型隐含的预期收益\n"
        "pd.Series(er_model, index=teach['asset'], name='E[R]_model').round(4)"
    ))
    cells.append(nbf.v4.new_markdown_cell(
        "## 第 2 步：加入 α —— 制造一个「异象」\n\n"
        "给 stock_2 一个显著为正的定价误差 α=1.2%/月，它就成了多因子模型解释不了的「异象」：\n"
        "**同样的暴露，更高的预期收益。**"
    ))
    cells.append(nbf.v4.new_code_cell(
        "alpha = np.array([0.0, 0.012, 0.0, 0.0])  # 只有 stock_2 有 α\n"
        "er_actual = er_model + alpha\n"
        "out = pd.DataFrame({'asset': teach['asset'], 'E[R]_model': er_model,\n"
        "                    'alpha': alpha, 'E[R]_actual': er_actual})\n"
        "out.round(4)"
    ))
    cells.append(nbf.v4.new_markdown_cell(
        "## 第 3 步：画出来 —— 定价误差看得见\n\n"
        "横轴：因子 A 上的暴露；纵轴：预期收益。模型隐含的关系是过原点的直线（斜率 λ_A）；\n"
        "**点到直线的垂直距离就是 α** —— 这就是书中图 2.3 的截面视角。"
    ))
    nb.cells = cells
    return nb

def build_01_1_plot_cells(nb) -> None:
    nb.cells.append(nbf.v4.new_code_cell(
        "fig, ax = plt.subplots(figsize=(7, 5))\n"
        "xs = np.linspace(0.6, 1.3, 10)\n"
        "ax.plot(xs, xs * lam[0], 'k--', label='E[R] = β·λ（模型直线）')\n"
        "for i, row in out.iterrows():\n"
        "    b = beta[i, 0]\n"
        "    marker = 'o' if row['alpha'] == 0 else '^'\n"
        "    ax.scatter(b, row['E[R]_actual'], s=120, marker=marker,\n"
        "               label=f\"{row['asset']}\" + ('（异象 ⭐）' if row['alpha'] != 0 else ''))\n"
        "    if row['alpha'] != 0:\n"
        "        ax.vlines(b, row['E[R]_model'], row['E[R]_actual'], color='red', linewidth=2)\n"
        "        ax.annotate('α = 1.2%/月', xy=(b, row['E[R]_model']),\n"
        "                    xytext=(b + 0.02, row['E[R]_model'] + 0.001), color='red')\n"
        "ax.set_xlabel('因子 A 暴露 β_A')\n"
        "ax.set_ylabel('预期收益 E[R]（月均）')\n"
        "ax.set_title('统一视角：E[R] = βλ + α')\n"
        "ax.legend(fontsize=8)\n"
        "plt.tight_layout(); plt.show()"
    ))


def build_01_1_time_cells(nb) -> None:
    nb.cells.append(nbf.v4.new_markdown_cell(
        "## 第 4 步：时序模拟 —— 协方差分解 Σ = βΣλβ′ + Σε\n\n"
        "从截面切到时序：模拟 T=120 个月的因子收益与个股收益，验证：\n"
        "**用因子算出的协方差结构 ≈ 真实的协方差矩阵**（降维的根据）。"
    ))
    nb.cells.append(nbf.v4.new_code_cell(
        "rng = np.random.default_rng(42)\n"
        "T = 120\n"
        "cov_lam = np.array([[0.0009, 0.0001], [0.0001, 0.0004]])  # 因子协方差\n"
        "lam_t = rng.multivariate_normal(lam, cov_lam, size=T)     # 因子收益时序\n"
        "idio = rng.normal(0, teach['idio_risk'].to_numpy(), size=(T, 4))  # 特质噪声\n"
        "ret = alpha + beta @ lam_t.T + idio   # 个股收益时序（式 1.5 的数值版）\n"
        "print('个股收益的样本协方差 Σ:')\n"
        "print(np.cov(ret.T).round(5))"
    ))
    nb.cells.append(nbf.v4.new_code_cell(
        "# 用因子重建协方差：Σ_hat = βΣλβ' + Σε\n"
        "sigma_eps = np.diag(teach['idio_risk'].to_numpy() ** 2)\n"
        "sigma_hat = beta @ cov_lam @ beta.T + sigma_eps\n"
        "sigma_true = np.cov(ret.T)\n"
        "err = np.abs(sigma_hat - sigma_true).max()\n"
        "print(f'重建协方差 vs 真实协方差的最大绝对误差: {err:.5f}')\n"
        "print('=> 协方差分解 Σ = βΣλβ′ + Σε 成立，这就是「因子=降维」的数学依据')"
    ))
    nb.cells.append(nbf.v4.new_markdown_cell(
        "## 小结\n\n"
        "- 预期收益是**截面**概念：E[R] = βλ，暴露高 → 预期收益高；\n"
        "- **α ≠ 0** 的资产 = 异象（多因子模型解释不了的部分）；\n"
        "- 协方差是**时序**概念：Σ = βΣλβ′ + Σε，因子把 N×N 的协方差问题降成 K×K；\n"
        "- 回到第1章检查站：现在你能用自己的话说清这三个概念了吗？"
    ))


def main() -> None:
    nb = build_01_1()
    build_01_1_plot_cells(nb)
    build_01_1_time_cells(nb)
    path = ROOT / "chapters" / "01-factor-basics" / "notebooks" / "01.1-unified-view.ipynb"
    path.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(nb, str(path))
    print(f"built {path}")


if __name__ == "__main__":
    main()
```

- [x] **Step 2: 运行构建器并确认 notebook 生成**

Run: `python scripts/build_notebooks.py`
Expected: `built .../notebooks/01.1-unified-view.ipynb`；文件存在且可被 `nbformat.read` 解析。

- [x] **Step 3: 写入执行护栏测试 `tests/test_notebooks.py`**

```python
"""Notebook 执行护栏：仓库内所有 notebook 必须能从头跑到尾（课程完成标准之一）。"""
from pathlib import Path

import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]


def _all_notebooks():
    return sorted((ROOT / "chapters").glob("*/notebooks/*.ipynb"))


def test_at_least_one_notebook():
    assert _all_notebooks(), "chapters 下还没有任何 notebook"


def test_all_notebooks_execute():
    for nb_path in _all_notebooks():
        nb = nbformat.read(nb_path, as_version=4)
        client = NotebookClient(nb, timeout=300, kernel_name="python3",
                                resources={"metadata": {"path": str(ROOT)}})
        client.execute()
        # nbclient 遇到异常会直接抛出，走到这里即视为执行成功
```

- [x] **Step 4: 运行执行护栏**

Run: `python -m pytest tests/test_notebooks.py -v`
Expected: 2 个测试 PASS（notebook 从头执行成功，输出含图）。

- [x] **Step 5: 提交**

Run: `git add scripts/build_notebooks.py tests/test_notebooks.py chapters/01-factor-basics/notebooks && git commit -m "feat(ch1): add unified-view notebook with executable guard"`
Expected: 提交成功。

---

### Task 8: 第1章练习与答案

**Files:**
- Create: `chapters/01-factor-basics/exercises/EXERCISES.md`
- Create: `chapters/01-factor-basics/exercises/solutions/SOLUTIONS.md`
- Delete: `chapters/01-factor-basics/exercises/solutions/.gitkeep`、`chapters/01-factor-basics/notebooks/.gitkeep`

**Interfaces:**
- Consumes: 讲义（Task 6）与 notebook（Task 7）
- Produces: 读者自测材料；检查站答案

- [x] **Step 1: 写入 `EXERCISES.md`**

```markdown
# 第1章 练习

> 建议先独立完成，再看 `solutions/SOLUTIONS.md`。

## 练习 1：概念自述（口头题）

用你自己的话 + 一个生活类比，向一个完全不懂金融的朋友解释：
因子、多因子模型、异象。要求每个概念不超过 3 句话。

## 练习 2：手算预期收益（计算题）

已知因子溢价 λ = [0.8%, 0.4%]（月均），某资产的因子暴露 β = [1.2, 0.5]。

1. 该资产在多因子模型下的预期收益 E[R] 是多少（月均）？
2. 如果它的实际预期收益是 1.5%/月，它的定价误差 α 是多少？它算不算一个"异象"？为什么？

## 练习 3：选择因子（判断题）

以下三组因子，哪组更适合放进同一个多因子模型？为什么？

- A 组：价值（BM）与盈利（ROE）
- B 组：价值（BM）与估值（EP）
- C 组：规模（市值）与市值对数

## 练习 4：读图（分析题）

打开 `notebooks/01.1-unified-view.ipynb`，把 `alpha` 数组全部改成 0 重新运行：

1. 图中红色竖线发生了什么变化？
2. 这说明了 α 在"截面视角"下的几何含义？

## 练习 5：降维（思维题）

假设市场上有 3000 支股票、10 个风格因子：

1. 直接估计资产协方差矩阵需要多少个参数？
2. 用因子模型（式 1.6）呢？
3. 这个数量级差异说明了什么？（提示：Barra CNE6）
```

- [x] **Step 2: 写入 `SOLUTIONS.md`**

```markdown
# 第1章 练习参考答案

## 练习 1（示例答案）

- **因子**：食物是"米饭、肉、菜"，但身体真正需要的是"碳水、蛋白质、维生素"——因子就是资产的"营养成分"：股票们共同暴露的系统性风险，长期有正的溢价。
- **多因子模型**：把几个营养（因子）放进一份"配餐表"（定价模型），任何一道菜（股票）的营养构成都能用它算出"标准营养值"（βλ）。
- **异象**：按配餐表算出的营养值明明只有 X，这道菜实际效果却远超 X（α>0）——要么配料表漏了某类营养（风险），要么这菜有猫腻（错误定价）。

## 练习 2

1. E[R] = 1.2×0.008 + 0.5×0.004 = 0.0096 + 0.0020 = **1.16%/月**。
2. α = 1.5% − 1.16% = **0.34%/月**。
   是否算异象要看统计检验（t 值），但 0.34%/月 的差距意味着模型可能漏了风险或存在错误定价——它具备"异象候选"的特征，需要第2章的方法来正式检验。

## 练习 3

**A 组**最合适。理由：
- B 组中 BM = 1/PB，EP = 1/PE，二者高度相关，代表同一类"估值"风险——放进同一模型会重复计功（第2章"正交化"会处理这类问题）；
- C 组中"市值"与"市值对数"是同一变量的单调变换，几乎完全相关；
- 低相关、每个因子有独立增量贡献，才符合多因子模型的"简约法则"。

## 练习 4

1. 红色竖线（α 标记）全部消失——所有点都落在模型直线上，模型"完美"解释所有资产；
2. α 在截面视角下就是"资产预期收益到模型直线（E[R]=βλ）的垂直距离"——距离为零说明没有定价误差，也就没有异象。

## 练习 5

1. 3000×3000 协方差矩阵：对称矩阵约 3000×3000/2 ≈ **450 万个**参数（还要满足正定，实际更难估）；
2. 因子模型只需：因子协方差 K×K ≈ 55 个参数 + 因子暴露矩阵 3000×10 = 3 万个参数（β 可由公司特征近似），且可解释；
3. 这就是"降维"：把不可估计的问题变成可估计、可解释的问题——Barra 用 1 国 + 9 风格 + 行业因子刻画 3000+ 股票的风险结构。
```

- [x] **Step 3: 删除 .gitkeep 占位并验证**

Run: `rm chapters/01-factor-basics/notebooks/.gitkeep chapters/01-factor-basics/exercises/solutions/.gitkeep && python -m pytest tests/ -v`
Expected: 全部测试 PASS（结构、数据、notebook 执行）。

- [x] **Step 4: 提交**

Run: `git add -A chapters/01-factor-basics && git commit -m "feat(ch1): add exercises and solutions"`
Expected: 提交成功。

---

### Task 9: 全量验证 + 首次发布到 GitHub

**Files:** 无新增（全量验证 + 远端发布）

**Interfaces:**
- Consumes: Task 1~8 全部产物
- Produces: `origin/main` 上的首个可公开版本（对应设计文档 M0+M1）

- [x] **Step 1: 配置 git 凭据助手（gh 已登录）**

Run: `gh auth setup-git`
Expected: 输出 `✓ Set up git to use GitHub as credential helper` 之类的成功提示。

- [x] **Step 2: 全量测试**

Run: `python -m pytest tests/ -v`
Expected: 全部 PASS（约 12 个测试）。

- [x] **Step 3: 最终检查仓库状态**

Run: `git status` 与 `git log --oneline`
Expected: 工作区干净；日志包含 Task 1~8 的提交。

- [x] **Step 4: 添加远端并推送**

Run: `git remote add origin https://github.com/Justinjchen-Cornell/Factor-Investing-from-Zero.git && git push -u origin main`
Expected: `main -> main` 推送成功；`gh repo view Justinjchen-Cornell/Factor-Investing-from-Zero` 可看到 README 渲染。

- [x] **Step 5: 验收打卡（对照设计文档 DoD）**

- [x] 讲义无 TODO，公式用代码块/LaTeX 标记，标注原书小节 ✅（Task 6 内容自查）
- [x] notebook 执行通过 ✅（Task 7 护栏测试）
- [x] 练习与检查站有答案 ✅（Task 8）
- [x] pytest 全绿 ✅（Step 2）
- [x] 内容原创、README 含版权声明 ✅（Task 5）
- [x] 提醒用户：发布完成后轮换 GitHub token（安全）

**M0+M1 完成。下一计划：M2（第2章方法论，排序法/FM/GRS/NW + factor_zero 核心实现）。**
