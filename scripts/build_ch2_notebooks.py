"""构建第2章教学 notebooks（用 nbformat 生成 .ipynb，保证可复现）。

用法：python scripts/build_ch2_notebooks.py
生成：
- chapters/02-methodology/notebooks/02.1-portfolio-sorting.ipynb
- chapters/02-methodology/notebooks/02.2-regression-methods.ipynb
- chapters/02-methodology/notebooks/02.3-anomaly-and-grs.ipynb
"""
from __future__ import annotations

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "chapters" / "02-methodology" / "notebooks"

CH2_SETUP = (
    "import sys\n"
    "from pathlib import Path\n\n"
    "def _find_root():\n"
    "    for p in [Path.cwd(), *Path.cwd().parents]:\n"
    "        if (p / 'src' / 'factor_zero').exists():\n"
    "            return p\n"
    "    raise FileNotFoundError('找不到仓库根目录，请从仓库内启动 notebook')\n"
    "ROOT = _find_root()\n"
    "if str(ROOT / 'src') not in sys.path:\n"
    "    sys.path.insert(0, str(ROOT / 'src'))\n\n"
    "import numpy as np\n"
    "import pandas as pd\n"
    "import matplotlib.pyplot as plt\n\n"
    "from factor_zero.sorting import quantile_group, sort_portfolios, spread_return, monotonicity_test\n"
    "from factor_zero.factors import monthly_returns, momentum, book_to_market, log_market_cap\n"
    "from factor_zero.statistics import nw_t_stat\n\n"
    "def _find_sample():\n"
    "    for p in [ROOT / 'data' / 'sample', Path('data/sample'), Path.cwd().parents[2] / 'data' / 'sample']:\n"
    "        if p.exists():\n"
    "            return p\n"
    "    raise FileNotFoundError('找不到 data/sample，请从仓库内启动 notebook')\n"
    "SAMPLE = _find_sample()\n"
    "plt.rcParams['figure.dpi'] = 110\n"
    "plt.rcParams['axes.unicode_minus'] = False\n"
    "plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Noto Sans CJK SC', 'DejaVu Sans']\n"
    "print('✅ 环境就绪，开始学习！')"
)

CH2_DATA = (
    "def load_ashare_snapshot():\n"
    "    \"\"\"加载 87 只 A 股快照，构造教学用月度面板。\n\n"
    "    真实数据：日线收盘价（2018-2024）+ 估值快照（2026-09-01）。\n"
    "    估值快照只有一期；为了演示“逐期排序”，这里用价格路径 + 快照估值\n"
    "    推导一个教学用月度基本面面板（合成，仅用于方法演示，不代表真实历史估值）。\n"
    "    \"\"\"\n"
    "    daily_dir = SAMPLE / 'a_share_snapshot' / 'daily'\n"
    "    codes = sorted(p.stem for p in daily_dir.glob('*.csv'))\n"
    "    prices = {}\n"
    "    for code in codes:\n"
    "        df = pd.read_csv(daily_dir / f'{code}.csv', parse_dates=['date'])\n"
    "        prices[code] = df.set_index('date')['close']\n"
    "    price_df = pd.DataFrame(prices).sort_index()\n\n"
    "    ret = monthly_returns(price_df).dropna(axis=1, how='any')\n"
    "    fund = pd.read_csv(SAMPLE / 'a_share_snapshot' / 'fundamentals.csv', parse_dates=['trade_date'])\n"
    "    fund['stock'] = fund['stock'].astype(int).astype(str).str.zfill(6)\n"
    "    fund = fund.set_index('stock').reindex(ret.columns)\n\n"
    "    month_end = price_df.resample('ME').last().ffill().reindex(columns=ret.columns)\n"
    "    last_price = month_end.iloc[-1]\n"
    "    shares = fund['total_mv'] / last_price\n"
    "    total_mv = month_end.mul(shares, axis=1)\n\n"
    "    base_pb = fund['pb']\n"
    "    months = np.arange(len(month_end))\n"
    "    phase = pd.Series(np.linspace(0, 2 * np.pi, len(ret.columns), endpoint=False), index=ret.columns)\n"
    "    seasonal = pd.DataFrame(\n"
    "        np.sin(months[:, None] / 12 * 2 * np.pi + phase.values[None, :]),\n"
    "        index=month_end.index, columns=ret.columns,\n"
    "    )\n"
    "    pb = (1 + 0.15 * seasonal).mul(base_pb, axis=1).clip(lower=0.05)\n"
    "    pe = pb / 0.10  # 教学用固定 ROE=10%，仅用于补全字段\n\n"
    "    panel = pd.concat([\n"
    "        pd.DataFrame({\n"
    "            'stock': col, 'trade_date': month_end.index,\n"
    "            'pb': pb[col].values, 'pe': pe[col].values, 'total_mv': total_mv[col].values,\n"
    "        }) for col in ret.columns\n"
    "    ], ignore_index=True)\n\n"
    "    bm = book_to_market(panel).reindex(index=ret.index, columns=ret.columns)\n"
    "    mv = log_market_cap(panel).reindex(index=ret.index, columns=ret.columns)\n"
    "    mom = momentum(ret, lookback=12, skip=1).reindex(index=ret.index, columns=ret.columns)\n"
    "    return {'ret': ret, 'bm': bm, 'mv': mv, 'mom': mom, 'price': price_df, 'panel': panel}\n"
)

# 保持源码可读：直接复用上面定义的长字符串
def _code(s: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(s)


def _md(s: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(s)


def build_2_1() -> nbf.NotebookNode:
    """02.1 投资组合排序法：BM 单变量排序 + 双重排序控市值。"""
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    c = []
    c.append(_md(
        "# 🎓 第2章 第1课：投资组合排序法 —— 分班考试\n\n"
        "**本节目标**：用“分班考试”的比喻，跑通排序法的完整流程。\n\n"
        "对应原书 2.1 节。我们会做三件事：\n\n"
        "1. **单变量排序**：按 BM（账面市值比）分 10 组，看组均收益是否单调；\n"
        "2. **价差组合**：高组 − 低组 = 价值因子收益率，用 Newey-West t 检验看显著性；\n"
        "3. **双重排序**：控制市值后，BM 还有没有增量解释力。\n\n"
        "> ⚠️ 数据说明：日线价格是真实 A 股快照；估值只有一期快照，notebook 用价格路径推导了一个**教学用月度估值面板**。收益大小仅用于演示方法，不代表真实 A 股结论。"
    ))
    c.append(_code(CH2_SETUP))
    c.append(_md(
        "## 0) 加载数据：把日线变成月度面板\n\n"
        "`load_ashare_snapshot()` 做四件事：\n\n"
        "- 读取 87 只股票的日线收盘价；\n"
        "- 月末重采样 → 月度收益率（丢掉有缺失的股票，保留 81 只完整样本）；\n"
        "- 用估值快照 + 价格路径推导教学用月度 PB / 总市值；\n"
        "- 构造 BM、对数市值、12-1 动量三个因子面板。"
    ))
    c.append(_code(CH2_DATA + "\ndata = load_ashare_snapshot()\nprint('月收益:', data['ret'].shape)\nprint('BM:', data['bm'].shape, '| 对数市值:', data['mv'].shape, '| 动量:', data['mom'].shape)\ndata['ret'].tail(2).round(4)"))
    c.append(_md(
        "## 1) 单变量排序：按 BM 分 10 组\n\n"
        "**排序法只假设“变量高低 ≈ 因子暴露高低”**，不假设任何数学关系（2.1.2 节）。\n\n"
        "做法：用 **t 月末的 BM** 分组，看 **t+1 月** 的组合收益——避免未来函数。"
    ))
    c.append(_code(
        "ret, bm = data['ret'], data['bm']\n"
        "common_idx = ret.index.intersection(bm.index)\n"
        "group_dict, port_dates = {}, []\n"
        "for t in range(len(common_idx) - 1):\n"
        "    d, d_next = common_idx[t], common_idx[t + 1]\n"
        "    g = quantile_group(bm.loc[d].dropna(), n_groups=10)\n"
        "    group_dict[d_next] = g\n"
        "    port_dates.append(d_next)\n"
        "groups = pd.DataFrame(group_dict).T.reindex(index=ret.index)\n"
        "port = sort_portfolios(ret, groups, n_groups=10)\n"
        "print('组合收益矩阵:', port.shape)\n"
        "port.tail(3).round(4)"
    ))
    c.append(_code(
        "means = port.mean()\n"
        "res = monotonicity_test(port)\n"
        "print(f'Spearman 秩相关: {res[\"rho\"]:.3f}  （≈1 单调上升；≈-1 单调下降；接近 0 无明显单调）')\n\n"
        "fig, ax = plt.subplots(figsize=(8, 4))\n"
        "means.plot(kind='bar', ax=ax, color='#5B8C5A')\n"
        "ax.set_title('按 BM 分 10 组的月均收益（1=低BM，10=高BM）')\n"
        "ax.set_xlabel('组别'); ax.set_ylabel('月均收益')\n"
        "plt.tight_layout(); plt.show()\n"
        "means.round(4)"
    ))
    c.append(_md(
        "> 🔍 **先别失望**：本例的估值面板是教学合成数据，没有刻意制造“价值溢价”，所以 rank 相关可能为负、价差可能不显著。这正好说明：排序法是一把尺子，结果要由数据说话，不能预设结论。\n"
    ))
    c.append(_md(
        "### 价差组合：高 BM − 低 BM\n\n"
        "价差组合（做多高组、做空低组）的收益率，就是**价值因子的收益率**。\n"
        "用 Newey-West 调整后的 t 值判断：这是“真实力”还是“运气”。"
    ))
    c.append(_code(
        "spread = spread_return(port, high=10, low=1).dropna()\n"
        "t_val, se = nw_t_stat(spread)\n"
        "print(f'价差组合月均收益: {spread.mean()*100:.3f}%')\n"
        "print(f'Newey-West 调整后 t = {t_val:.2f}')\n"
        "print('|t| > 2 → 在 95% 置信下显著' if abs(t_val) > 2 else '|t| ≤ 2 → 不显著，不能排除运气')"
    ))
    c.append(_md(
        "## 2) 双重排序：控制市值\n\n"
        "高 BM 组会不会恰好全是小盘股？用**条件双重排序**：\n\n"
        "1. 先按市值分 5 层；\n"
        "2. 每层内部再按 BM 分 5 组；\n"
        "3. 在每一层内算 BM 价差（组5 − 组1），再看各层结果。\n\n"
        "这样市值被“控制住”了，BM 的效果更干净。"
    ))
    c.append(_code(
        "mv, bm, ret = data['mv'], data['bm'], data['ret']\n"
        "common = ret.index.intersection(bm.index).intersection(mv.index)\n"
        "spreads_by_size = {}\n"
        "for t in range(len(common) - 1):\n"
        "    d, dn = common[t], common[t + 1]\n"
        "    size_g = quantile_group(mv.loc[d].dropna(), n_groups=5)\n"
        "    for s in range(1, 6):\n"
        "        inside = size_g[size_g == s].index\n"
        "        if len(inside) < 5:\n"
        "            continue\n"
        "        bm_inside = bm.loc[d, inside].dropna()\n"
        "        g = quantile_group(bm_inside, n_groups=5)\n"
        "        sub_ret = ret.loc[dn, g.index]\n"
        "        sub_ret_df = sub_ret.to_frame().T.copy(); sub_ret_df.index = [dn]\n"
        "        g_df = g.to_frame().T.copy(); g_df.index = [dn]\n"
        "        port_s = sort_portfolios(sub_ret_df, g_df, n_groups=5)\n"
        "        spreads_by_size.setdefault(s, []).append(port_s.iloc[0, 4] - port_s.iloc[0, 0])\n\n"
        "print('市值层内 BM 价差月均收益（每层 = 控制市值后的 BM 效果）:')\n"
        "all_spreads = []\n"
        "for s in sorted(spreads_by_size):\n"
        "    vals = pd.Series(spreads_by_size[s])\n"
        "    all_spreads.extend(vals.tolist())\n"
        "    print(f'  市值第{s}层: {vals.mean()*100:+.3f}%/月 (共{len(vals)}期)')\n"
        "print(f'  五层平均: {pd.Series(all_spreads).mean()*100:+.3f}%/月')"
    ))
    c.append(_md(
        "## ✋ 试一试\n\n"
        "1. 把单变量排序改成按**动量**排序（`data['mom']`），价差组合还显著吗？\n"
        "2. 把 `n_groups=10` 改成 5，单调性和价差会怎么变？\n"
        "3. 双重排序里把“先市值、后 BM”改成“先 BM、后市值”，结果有什么不同？\n\n"
        "## ✅ 本节小结\n\n"
        "- 排序法绕开了“暴露未知”的循环：**变量高低 ≈ 暴露高低**；\n"
        "- 价差组合 = 因子收益率；NW t 检验判断显著性；\n"
        "- 双重排序控制其他因子（这里是市值），看**增量解释力**；\n"
        "- 示例数据为教学面板，收益大小不代表真实 A 股结论。\n\n"
        "> 下一课：三种回归方法——时序、截面、Fama-MacBeth，用已知真相的数据验证。"
    ))
    nb.cells = c
    return nb


def build_2_2() -> nbf.NotebookNode:
    """02.2 三种回归：时序 / 截面 / Fama-MacBeth。"""
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    c = []
    c.append(_md(
        "# 🎓 第2章 第2课：三种回归 —— 时序 / 截面 / Fama-MacBeth\n\n"
        "**本节目标**：先造一个“已知真相”的世界，再看三种方法能不能把真相挖回来。\n\n"
        "对应原书 2.2 节。\n\n"
        "- **时序回归** → 恢复 β（敏感度）；\n"
        "- **截面回归** → 恢复 λ（因子身价）；\n"
        "- **FM 回归** → 恢复 λ + 正确标准误。\n\n"
        "> 口诀：**截面回归 = 先均值再回归；FM = 先回归再均值。**"
    ))
    c.append(_code(CH2_SETUP + "\n\nfrom factor_zero.data_sim import simulate_cross_section\nfrom factor_zero.regression import time_series_betas, cross_sectional_lambda, fama_macbeth"))
    c.append(_md(
        "## 0) 造一个已知真相的世界\n\n"
        "我们预设每只股票的 β 和因子溢价 λ，生成收益数据。\n"
        "因为真相已知，才能判断方法准不准。"
    ))
    c.append(_code(
        "sim = simulate_cross_section(n_assets=200, t_periods=240, n_factors=3, noise=0.01, seed=7)\n"
        "print('预设的真相 λ =', sim['lambda'].round(5))\n"
        "print('收益矩阵:', sim['ret'].shape, '| 特征矩阵:', sim['char'].shape)"
    ))
    c.append(_md(
        "## 1) 时序回归：恢复 β\n\n"
        "对每个资产：$r_{it} = \alpha_i + \beta_i' f_t + \varepsilon_{it}$。\n"
        "估计出的 β 应该接近预设值。"
    ))
    c.append(_code(
        "fdf = pd.DataFrame(sim['factor_ret'], columns=['F1', 'F2', 'F3'])\n"
        "alphas, betas, resid = time_series_betas(sim['ret'], fdf)\n"
        "err = np.abs(betas.to_numpy() - sim['beta']).max()\n"
        "print(f'β 恢复最大误差: {err:.5f}（越小越准）')\n"
        "betas.head(5).round(3)"
    ))
    c.append(_md(
        "## 2) 截面回归：恢复 λ\n\n"
        "第二步：平均收益 ~ β，斜率就是 λ。\n\n"
        "注意：这里的 β 是**估计值**（生成回归变量），严格说需要 Shanken 修正（2.2.2 节）；\n"
        "这里先用朴素 OLS 感受数量级。"
    ))
    c.append(_code(
        "mean_ret = sim['ret'].mean(axis=0)\n"
        "lam_cs, alphas_cs = cross_sectional_lambda(betas, mean_ret)\n"
        "print('截面回归 λ =', lam_cs.round(5))\n"
        "print('预设真相 λ =', sim['lambda'].round(5))\n"
        "print('误差        =', (lam_cs - sim['lambda']).round(5))"
    ))
    c.append(_md(
        "## 3) Fama-MacBeth：恢复 λ + 标准误\n\n"
        "每一期单独做截面回归，得到 T 个 λ_t，再平均——这就是“先回归、再均值”。\n"
        "标准误用 Newey-West 修正。"
    ))
    c.append(_code(
        "lam_fm, lam_t, se, t_stat = fama_macbeth(sim['ret'], sim['char'])\n"
        "res = pd.DataFrame({\n"
        "    'FM λ': lam_fm[1:],\n"
        "    '真相 λ': sim['lambda'],\n"
        "    '标准误': se[1:],\n"
        "    't 值': t_stat[1:],\n"
        "}, index=['F1', 'F2', 'F3'])\n"
        "res.round(4)"
    ))
    c.append(_code(
        "print('每个因子 |t| > 2 → 在 95% 置信下显著')\n"
        "print('全部显著 ✓' if (np.abs(t_stat[1:]) > 2).all() else '有不显著的因子 ✗')"
    ))
    c.append(_md(
        "## 4) 上 A 股快照：FM 检验价值 / 规模 / 动量\n\n"
        "用第 2.1 节构造的因子（BM、对数市值、动量）当特征，跑 FM。\n"
        "**注意**：这是教学面板，结果不代表真实 A 股结论；重点是看懂流程。\n\n"
        "特征先做截面 z-score，便于比较系数大小。"
    ))
    c.append(_code(CH2_DATA + "\ndata = load_ashare_snapshot()\nret, bm, mv, mom = data['ret'], data['bm'], data['mv'], data['mom']\nidx = ret.index.intersection(bm.index).intersection(mv.index).intersection(mom.index)\nret, bm, mv, mom = ret.loc[idx], bm.loc[idx], mv.loc[idx], mom.loc[idx]\n\ndef zscore(df):\n    return df.sub(df.mean(axis=1), axis=0).div(df.std(axis=1), axis=0)\n\nX = np.stack([zscore(bm), zscore(mv), zscore(mom)], axis=2)\nX = np.nan_to_num(X, nan=0.0)  # 动量前 12 个月缺失 → 视为截面平均\nlam_fm, lam_t, se, t_stat = fama_macbeth(ret, X)\nres = pd.DataFrame({\n    'λ': lam_fm[1:],\n    '标准误': se[1:],\n    't 值': t_stat[1:],\n}, index=['价值(BM)', '规模(ln市值)', '动量'])\nres.round(4)"))
    c.append(_md(
        "## ✋ 试一试\n\n"
        "1. 把 `simulate_cross_section` 的 `n_factors` 改成 5，看 FM 还能不能恢复全部 λ；\n"
        "2. 用 `lambda_values=np.array([0.006, 0.004, 0.0])` 造一个“没被定价”的因子，看它的 t 值；\n"
        "3. 把 A 股 FM 的 `mom` 换成滞后一期，结果变多少？\n\n"
        "## ✅ 本节小结\n\n"
        "- 三种回归的关系：**时序求 β → 截面求 λ**；FM = 截面回归的逐期版；\n"
        "- FM 在已知真相数据上能恢复预设 λ（含标准误），方法可信；\n"
        "- 真实数据上因子显著性会随样本、区间、数据处理变化——这就是第3章要做的事。\n\n"
        "> 下一课：异象检验 + GRS + 正交化。"
    ))
    nb.cells = c
    return nb


def build_2_3() -> nbf.NotebookNode:
    """02.3 异象检验 + GRS + 正交化。"""
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    c = []
    c.append(_md(
        "# 🎓 第2章 第3课：异象检验 + GRS + 正交化\n\n"
        "**本节目标**：当一次医生，做三件事。\n\n"
        "1. **造一个异象**：给某资产注入真实 α，看时序回归能不能把它揪出来（含 NW 修正）；\n"
        "2. **GRS 体检**：三个因子够不够？\n"
        "3. **正交化**：去掉重复信息后，因子还剩多少增量。\n\n"
        "对应原书 2.4~2.6 节。"
    ))
    c.append(_code(CH2_SETUP + "\n\nfrom factor_zero.statistics import newey_west_vcov, grs_test\nfrom factor_zero.regression import time_series_betas"))
    c.append(_md(
        "## 0) 造一个异象\n\n"
        "8 个资产、3 个因子，给资产 0 注入 **0.8%/月** 的真实 α，其余为 0。\n"
        "如果方法有效，时序回归应该能在资产 0 上看到显著 α；但即使真实 α=0，也可能有约 5% 的假阳性——所以还要看 GRS 和多重检验。"
    ))
    c.append(_code(
        "rng = np.random.default_rng(99)\n"
        "T, N, K = 240, 8, 3\n"
        "beta = rng.uniform(0.5, 1.5, size=(N, K))\n"
        "lam = np.array([0.006, 0.004, 0.002])\n"
        "f = rng.multivariate_normal(lam, np.diag([0.02**2] * K), size=T)\n"
        "alpha_true = np.zeros(N)\n"
        "alpha_true[0] = 0.008\n"
        "r = alpha_true + f @ beta.T + rng.normal(0, 0.01, size=(T, N))\n"
        "print('注入真相：资产0 α=0.8%/月，其余为0')"
    ))
    c.append(_md(
        "## 1) 时序回归检验异象（2.4.1 节）\n\n"
        "对每个资产回归 $r = \alpha + \beta f + \varepsilon$。\n"
        "对比 **OLS 标准误 vs Newey-West 标准误**。"
    ))
    c.append(_code(
        "fdf = pd.DataFrame(f, columns=['F1', 'F2', 'F3'])\n"
        "alphas, betas, resid = time_series_betas(pd.DataFrame(r, columns=[f'a{i}' for i in range(N)]), fdf)\n"
        "rows = []\n"
        "X = np.column_stack([np.ones(T), f])\n"
        "for i in range(N):\n"
        "    e = resid.iloc[:, i].to_numpy()\n"
        "    vcov_ols = np.linalg.inv(X.T @ X) * (e @ e / (T - K - 1))\n"
        "    vcov_nw = newey_west_vcov(X, e)\n"
        "    rows.append({\n"
        "        '资产': f'a{i}',\n"
        "        'α估计(%/月)': alphas.iloc[i] * 100,\n"
        "        'OLS t': alphas.iloc[i] / np.sqrt(vcov_ols[0, 0]),\n"
        "        'NW t': alphas.iloc[i] / np.sqrt(vcov_nw[0, 0]),\n"
        "        '真相α(%/月)': alpha_true[i] * 100,\n"
        "    })\n"
        "pd.DataFrame(rows).round(3)"
    ))
    c.append(_md(
        "> 🔍 **注意假阳性**：即使真实 α=0，8 个资产里也可能有 1–2 个 |t| 略大于 2 的“假阳性”（约 5% 概率）。\n"
        "> 所以不能逐个看 t 值就下结论，还要看 **GRS 联合检验**和多重检验校正。\n"
    ))
    c.append(_md(
        "## 2) GRS 体检：3 因子模型够吗？（2.5.1 节）\n\n"
        "GRS 联合检验所有 α 是否为零。\n"
        "异象存在 → 模型被拒绝（p 值小）。"
    ))
    c.append(_code(
        "F, p = grs_test(alphas.to_numpy(), resid.to_numpy(), f)\n"
        "print(f'GRS F = {F:.3f}, p 值 = {p:.6f}')\n"
        "print('p < 0.05 → 模型被拒绝：存在模型解释不了的异象' if p < 0.05 else 'p ≥ 0.05 → 模型通过体检')"
    ))
    c.append(_md(
        "## 3) 正交化：只听增量信息（2.6 节）\n\n"
        "假设 F2 和 F3 高度相关——把 F3 对 F2 回归，**残差 = F3 的纯新增信息**。\n"
        "正交化后，F3 与 F2 的相关系数应接近 0。"
    ))
    c.append(_code(
        "f2 = f[:, 1]\n"
        "f3_corr = 0.9 * f2 + rng.normal(0, 0.01, T)  # 人为制造高度相关\n"
        "coef = np.polyfit(f2, f3_corr, 1)\n"
        "f3_orth = f3_corr - (coef[0] * f2 + coef[1])\n"
        "print(f'正交化前 F2 与 F3 的相关系数: {np.corrcoef(f2, f3_corr)[0, 1]:.4f}')\n"
        "print(f'正交化后 F2 与 F3 的相关系数: {np.corrcoef(f2, f3_orth)[0, 1]:.10f}')\n"
        "print('→ 正交化后相关性归零，残差就是 F3 独有的信息')"
    ))
    c.append(_md(
        "## ✋ 试一试\n\n"
        "1. 把 `alpha_true[0]` 改成 0，GRS 的 p 值会怎么变？\n"
        "2. 把注入 α 改成 0.003（0.3%/月），NW t 还能显著吗？\n"
        "3. 把 `f3_corr = 0.9*f2 + ...` 的 0.9 改成 0.3，正交化前后相关系数怎么变？\n\n"
        "## ✅ 本节小结\n\n"
        "- **异象检验** = 回归 α 显著 ≠ 0（别忘了 NW 眼镜）；\n"
        "- **GRS** = 把一群资产的 α 打包查，模型好不好看 p 值；\n"
        "- **正交化** = 残差即增量，业界构建因子前的标准动作。\n\n"
        "> 下一章：把这些方法用到 A 股七大因子上（第3章）。"
    ))
    nb.cells = c
    return nb


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    notebooks = {
        "02.1-portfolio-sorting": build_2_1(),
        "02.2-regression-methods": build_2_2(),
        "02.3-anomaly-and-grs": build_2_3(),
    }
    for name, nb in notebooks.items():
        path = OUT / f"{name}.ipynb"
        nbf.write(nb, str(path))
        print(f"built {path}")


if __name__ == "__main__":
    main()
