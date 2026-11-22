"""构建第3章教学 notebooks（用 nbformat 生成 .ipynb，保证可复现）。

用法：python scripts/build_ch3_notebooks.py
生成：
- chapters/03-mainstream-factors/notebooks/03.1-data-and-factors.ipynb
- chapters/03-mainstream-factors/notebooks/03.2-factor-sorting.ipynb
- chapters/03-mainstream-factors/notebooks/03.3-performance-and-robustness.ipynb
"""
from __future__ import annotations

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "chapters" / "03-mainstream-factors" / "notebooks"

CH3_SETUP = (
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
    "from factor_zero.data import load_ashare_panel\n"
    "from factor_zero.factors import build_factor_returns\n"
    "from factor_zero.statistics import factor_summary, nw_t_stat\n"
    "from factor_zero.sorting import long_short_factor, monotonicity_test\n\n"
    "FACTOR_NAMES = ['MKT', 'SMB', 'HML', 'WML', 'RMW', 'CMA', 'TURN']\n"
    "FACTOR_CN = {'MKT': '市场', 'SMB': '规模', 'HML': '价值',\n"
    "             'WML': '动量', 'RMW': '盈利', 'CMA': '投资', 'TURN': '换手率'}\n\n"
    "plt.rcParams['figure.dpi'] = 110\n"
    "plt.rcParams['axes.unicode_minus'] = False\n"
    "plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Noto Sans CJK SC', 'DejaVu Sans']\n"
    "print('✅ 环境就绪，开始学习！')"
)

FACTOR_NAMES = ["MKT", "SMB", "HML", "WML", "RMW", "CMA", "TURN"]
FACTOR_CN = {
    "MKT": "市场", "SMB": "规模", "HML": "价值",
    "WML": "动量", "RMW": "盈利", "CMA": "投资", "TURN": "换手率",
}


def _code(s: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(s)


def _md(s: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(s)


def build_3_1() -> nbf.NotebookNode:
    """03.1 数据处理 + 七大因子构造。"""
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    c = []
    c.append(_md(
        "# 🎓 第3章 第1课：数据处理与七大因子构造\n\n"
        "**本节目标**：从原始日线出发，走完因子研究的第一步——把数据变成可比较的月度面板，再构造七大因子。\n\n"
        "对应原书 3.1 节（数据处理）与 3.2~3.8 节（七大因子）。\n\n"
        "> ⚠️ 数据说明：日线行情是真实 A 股快照；估值只有一期快照，ROE/投资等逐期面板是**教学用合成面板**。\n"
        "> 本 notebook 演示方法与流程，数值不代表真实 A 股的历史实证结论。"
    ))
    c.append(_code(CH3_SETUP))
    c.append(_md(
        "## 1) 数据处理：从日线到月度面板\n\n"
        "因子研究的第一步不是“算因子”，而是**把数据处理干净**。原书 3.1 节的流程：\n\n"
        "1. 月度调仓，用月末收盘价算月收益；\n"
        "2. 剔除 ST/*ST、退市、负净资产、次新股；\n"
        "3. 缩尾（1%/99%）处理极端值；\n"
        "4. 剔除一字涨跌停；\n"
        "5. 保留金融股（银行/券商/保险），不做行业剔除。\n\n"
        "本仓库的示例数据只有 87 只股票的快照，无法完整执行 2~4 步；notebook 保留**完整历史**的 81 只股票，\n"
        "并在因子层面做极端值裁剪。真实研究请按原书流程补齐。"
    ))
    c.append(_code(
        "panel = load_ashare_panel()\n"
        "print('股票数:', panel['ret'].shape[1])\n"
        "print('月份数:', panel['ret'].shape[0])\n"
        "print('时间范围:', panel['ret'].index.min().date(), '→', panel['ret'].index.max().date())\n"
        "panel['ret'].head(3).round(4)"
    ))
    c.append(_md(
        "## 2) 七大因子：定义与方向\n\n"
        "| 代码 | 因子 | 构造 | 方向（多空组合） |\n"
        "|---|---|---|---|\n"
        "| MKT | 市场 | 市值加权市场收益 | 示意，未减无风险利率 |\n"
        "| SMB | 规模 | 对数市值排序 | 小市值 − 大市值 |\n"
        "| HML | 价值 | BM = 1/PB 排序 | 高 BM − 低 BM |\n"
        "| WML | 动量 | 12-1 月累计收益排序 | 高动量 − 低动量 |\n"
        "| RMW | 盈利 | ROE 排序 | 高 ROE − 低 ROE |\n"
        "| CMA | 投资 | 投资强度排序 | 低投资 − 高投资 |\n"
        "| TURN | 换手率 | 月换手率排序 | 低换手 − 高换手 |\n\n"
        "> 方向很重要：同一个变量，做多高组还是低组，得到的因子收益符号完全不同。\n"
        "> 这里按“经济逻辑上预期为正”的方向定义；实际显著性和符号要由数据检验。"
    ))
    c.append(_code(
        "factors = build_factor_returns(panel, n_groups=10)\n"
        "factors.head(3).round(4)"
    ))
    c.append(_md("### 因子绩效速览\n\n用第2章的 NW t 检验，先看每个因子的年化收益、波动、Sharpe 和显著性。"))
    c.append(_code(
        "rows = {}\n"
        "for col in factors.columns:\n"
        "    s = factor_summary(factors[col].dropna())\n"
        "    if s:\n"
        "        rows[col] = s\n"
        "summary = pd.DataFrame(rows).T\n"
        "summary.index = [f'{k}（{FACTOR_CN.get(k, k)}）' for k in summary.index]\n"
        "summary.columns = ['年化收益', '年化波动', 'Sharpe', 'NW t', '最大回撤', '胜率']\n"
        "summary.round(4)"
    ))
    c.append(_md(
        "## 3) 看净值：七个因子的累计表现\n\n"
        "把每个因子看成一条可交易的多空组合，画累计净值（1 元起）。\n"
        "注意：示例面板是教学数据，曲线形状只用于演示。"
    ))
    c.append(_code(
        "nav = (1 + factors).cumprod()\n"
        "fig, axes = plt.subplots(2, 4, figsize=(16, 7), sharex=True)\n"
        "for ax, col in zip(axes.flat, FACTOR_NAMES):\n"
        "    nav[col].dropna().plot(ax=ax, color='#5B7FA6')\n"
        "    ax.set_title(f'{col}（{FACTOR_CN[col]}）')\n"
        "    ax.axhline(1, color='gray', lw=.8, ls='--')\n"
        "    ax.tick_params(axis='x', rotation=30, labelsize=8)\n"
        "for ax in axes.flat[len(FACTOR_NAMES):]:\n"
        "    ax.axis('off')\n"
        "plt.tight_layout(); plt.show()"
    ))
    c.append(_md(
        "## 4) 因子相关性：它们是不是在说同一件事？\n\n"
        "如果两个因子高度相关，它们可能只是同一个风险的两种叫法。\n"
        "相关性矩阵是判断“因子冗余”的第一眼。"
    ))
    c.append(_code(
        "corr = factors.corr()\n"
        "fig, ax = plt.subplots(figsize=(7, 6))\n"
        "im = ax.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1)\n"
        "ax.set_xticks(range(len(corr))); ax.set_xticklabels(corr.columns)\n"
        "ax.set_yticks(range(len(corr))); ax.set_yticklabels(corr.index)\n"
        "for i in range(len(corr)):\n"
        "    for j in range(len(corr)):\n"
        "        ax.text(j, i, f'{corr.iloc[i, j]:.2f}', ha='center', va='center', fontsize=8)\n"
        "plt.colorbar(im, ax=ax, shrink=.8)\n"
        "ax.set_title('七大因子收益率相关性')\n"
        "plt.tight_layout(); plt.show()"
    ))
    c.append(_md(
        "## ✋ 试一试\n\n"
        "1. 把 `build_factor_returns` 的 `n_groups` 从 10 改成 5，因子收益和相关性会怎么变？\n"
        "2. 把 `TURN` 的方向反过来（高换手 − 低换手），均值和 t 值符号怎么变？\n"
        "3. 把 `MKT` 换成等权市场收益，和市值加权差多少？\n\n"
        "## ✅ 本节小结\n\n"
        "- 因子研究先做数据：月度化、对齐、剔除异常、缩尾；\n"
        "- 七大因子都可以用“排序 → 分组 → 多空”统一构造；\n"
        "- 方向是定义的一部分：做多高组还是低组，符号完全不同；\n"
        "- 相关性矩阵是判断因子冗余的第一眼。\n\n"
        "> 下一课：七个因子的分组单调性与多空组合细节。"
    ))
    nb.cells = c
    return nb


def build_3_2() -> nbf.NotebookNode:
    """03.2 分组单调性与多空组合。"""
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    c = []
    c.append(_md(
        "# 🎓 第3章 第2课：分组单调性与多空组合\n\n"
        "**本节目标**：对每个因子做“分班考试”，看两件事：\n\n"
        "1. **单调性**：组号越高，收益是否越高（或越低）？\n"
        "2. **多空组合**：高组 − 低组的收益是否显著？\n\n"
        "对应原书 3.2~3.8 节的因子实证框架。"
    ))
    c.append(_code(CH3_SETUP))
    c.append(_code(
        "panel = load_ashare_panel()\n"
        "ret = panel['ret']\n"
        "specs = {\n"
        "    'SMB': ('size', False),      # 小市值 − 大市值\n"
        "    'HML': ('bm', True),         # 高BM − 低BM\n"
        "    'WML': ('momentum', True),   # 高动量 − 低动量\n"
        "    'RMW': ('roe', True),        # 高ROE − 低ROE\n"
        "    'CMA': ('investment', False),# 低投资 − 高投资\n"
        "    'TURN': ('turnover', False), # 低换手 − 高换手\n"
        "}\n"
        "ports, rows = {}, {}\n"
        "for name, (key, high) in specs.items():\n"
        "    f, port, groups = long_short_factor(panel[key], ret, n_groups=10, high_minus_low=high)\n"
        "    ports[name] = port\n"
        "    rho = monotonicity_test(port)['rho']\n"
        "    s = factor_summary(f)\n"
        "    rows[name] = {'Spearman rho': rho, '年化多空': s['mean_ann'], 'NW t': s['t_stat']}\n"
        "table = pd.DataFrame(rows).T\n"
        "table.round(4)"
    ))
    c.append(_md(
        "### 怎么读这张表？\n\n"
        "- **rho ≈ +1**：组号越高收益越高（完美单调上升）；**rho ≈ −1**：完美单调下降；\n"
        "- **年化多空**：按因子定义方向（见表）的多空组合年化收益；\n"
        "- **NW t**：|t| > 2 才在 95% 置信下显著。\n\n"
        "> 注意：**rho 的符号取决于排序变量的方向**。SMB 的排序变量是市值，rho 为负表示“市值越小、收益越高”，对应 SMB（小减大）为正；HML 同理。\n"
        "> 示例面板是教学数据，符号和显著性只用于演示，不代表真实 A 股结论。"
    ))
    c.append(_code(
        "fig, axes = plt.subplots(2, 3, figsize=(16, 8))\n"
        "for ax, (name, port) in zip(axes.flat, ports.items()):\n"
        "    means = port.mean() * 100\n"
        "    means.plot(kind='bar', ax=ax, color='#5B8C5A')\n"
        "    rho = table.loc[name, 'Spearman rho']\n"
        "    ax.set_title(f'{name} 分组月均收益（rho={rho:.2f}）')\n"
        "    ax.set_xlabel('组别（1=低，10=高）')\n"
        "    ax.set_ylabel('月均收益（%）')\n"
        "plt.tight_layout(); plt.show()"
    ))
    c.append(_md(
        "## 双重排序：控制市值后，价值因子还剩多少？\n\n"
        "高 BM 组可能恰好全是小盘股。用**条件双重排序**：\n\n"
        "1. 先按市值分 3 层；\n"
        "2. 每层内部按 BM 分 5 组；\n"
        "3. 在每层内算 BM 价差（组5 − 组1）。\n\n"
        "如果在每一层内 BM 价差都还在，说明价值因子不是规模的“马甲”。"
    ))
    c.append(_code(
        "from factor_zero.sorting import quantile_group, sort_portfolios\n"
        "common = ret.index.intersection(panel['bm'].index).intersection(panel['size'].index)\n"
        "spreads = {1: [], 2: [], 3: []}\n"
        "for t in range(len(common) - 1):\n"
        "    d, dn = common[t], common[t + 1]\n"
        "    sg = quantile_group(panel['size'].loc[d].dropna(), n_groups=3)\n"
        "    for layer in [1, 2, 3]:\n"
        "        inside = sg[sg == layer].index\n"
        "        if len(inside) < 5:\n"
        "            continue\n"
        "        bm_in = panel['bm'].loc[d, inside].dropna()\n"
        "        g = quantile_group(bm_in, n_groups=5)\n"
        "        sub_ret = ret.loc[[dn], g.index]\n"
        "        sub_g = g.to_frame().T.copy(); sub_g.index = [dn]\n"
        "        port_s = sort_portfolios(sub_ret, sub_g, n_groups=5)\n"
        "        spreads[layer].append(port_s.iloc[0, 4] - port_s.iloc[0, 0])\n\n"
        "for layer in [1, 2, 3]:\n"
        "    s = pd.Series(spreads[layer])\n"
        "    t_nw, _ = nw_t_stat(s)\n"
        "    print(f'市值第{layer}层（{\"小\" if layer==1 else \"中\" if layer==2 else \"大\"}）：'\n"
        "          f'{s.mean()*100:+.3f}%/月，NW t={t_nw:.2f}，共{len(s)}期')"
    ))
    c.append(_md(
        "## ✋ 试一试\n\n"
        "1. 把分组数从 10 改成 5，rho 和多空收益会怎么变？\n"
        "2. 把 `TURN` 的方向反过来，rho 的符号怎么变？\n"
        "3. 双重排序里把层数从 3 改成 5，每层的样本变少后结果还稳定吗？\n\n"
        "## ✅ 本节小结\n\n"
        "- 单调性看“组号—收益”的秩相关；多空组合看高组减低组；\n"
        "- 方向由定义决定，符号要和经济学预期对照；\n"
        "- 双重排序控制混淆因子（如市值），看增量解释力。\n\n"
        "> 下一课：七大因子的绩效比较、相关性与分区间稳健性。"
    ))
    nb.cells = c
    return nb


def build_3_3() -> nbf.NotebookNode:
    """03.3 绩效比较、相关性与分区间稳健性。"""
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    c = []
    c.append(_md(
        "# 🎓 第3章 第3课：绩效比较与稳健性\n\n"
        "**本节目标**：把七个因子放在同一张桌子上比较：\n\n"
        "1. 年化收益、波动、Sharpe、NW t、最大回撤；\n"
        "2. 累计净值与相关性；\n"
        "3. 分区间稳健性：前半段有效的因子，后半段还灵吗？\n\n"
        "对应原书 3.2~3.8 节的因子比较与研究建议。"
    ))
    c.append(_code(CH3_SETUP))
    c.append(_code(
        "panel = load_ashare_panel()\n"
        "factors = build_factor_returns(panel, n_groups=10)\n"
        "rows = {}\n"
        "for col in factors.columns:\n"
        "    s = factor_summary(factors[col].dropna())\n"
        "    if s:\n"
        "        rows[col] = s\n"
        "perf = pd.DataFrame(rows).T\n"
        "perf.index = [f'{k}（{FACTOR_CN[k]}）' for k in perf.index]\n"
        "perf.columns = ['年化收益', '年化波动', 'Sharpe', 'NW t', '最大回撤', '胜率']\n"
        "perf.round(4)"
    ))
    c.append(_md(
        "### 怎么读绩效表？\n\n"
        "- **年化收益 / 年化波动**：月度均值/标准差 × 12 / × √12；\n"
        "- **Sharpe**：年化收益 ÷ 年化波动（未减无风险利率，示意）；\n"
        "- **NW t**：Newey-West 调整后的 t 值，|t| > 2 才显著；\n"
        "- **最大回撤**：累计净值从高点到低点的最大跌幅；\n"
        "- **胜率**：因子收益为正的月份占比。\n\n"
        "> 单看收益不够：高收益可能伴随高波动/大回撤。四个指标要一起看。"
    ))
    c.append(_code(
        "nav = (1 + factors).cumprod()\n"
        "fig, ax = plt.subplots(figsize=(12, 5))\n"
        "for col in FACTOR_NAMES:\n"
        "    nav[col].dropna().plot(ax=ax, label=f'{col}（{FACTOR_CN[col]}）')\n"
        "ax.axhline(1, color='gray', lw=.8, ls='--')\n"
        "ax.set_title('七大因子累计净值（1 元起）')\n"
        "ax.set_ylabel('累计净值')\n"
        "ax.legend(ncol=4, fontsize=8)\n"
        "plt.tight_layout(); plt.show()"
    ))
    c.append(_md(
        "## 相关性：因子之间是不是“亲戚”？\n\n"
        "相关性高 → 可能重复；相关性低 → 组合起来更分散。\n"
        "但相关性不是全部：两个因子可能在不同区间轮换表现。"
    ))
    c.append(_code(
        "corr = factors.corr()\n"
        "fig, ax = plt.subplots(figsize=(7, 6))\n"
        "im = ax.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1)\n"
        "ax.set_xticks(range(len(corr))); ax.set_xticklabels(corr.columns)\n"
        "ax.set_yticks(range(len(corr))); ax.set_yticklabels(corr.index)\n"
        "for i in range(len(corr)):\n"
        "    for j in range(len(corr)):\n"
        "        ax.text(j, i, f'{corr.iloc[i, j]:.2f}', ha='center', va='center', fontsize=8)\n"
        "plt.colorbar(im, ax=ax, shrink=.8)\n"
        "ax.set_title('因子相关性矩阵')\n"
        "plt.tight_layout(); plt.show()"
    ))
    c.append(_md(
        "## 分区间稳健性：前半段 vs 后半段\n\n"
        "把样本一分为二，看每个因子的年化收益符号是否一致。\n"
        "**一个因子只有在不同区间都站得住，才更可信。**"
    ))
    c.append(_code(
        "mid = len(factors) // 2\n"
        "first = factors.iloc[:mid].mean() * 12\n"
        "second = factors.iloc[mid:].mean() * 12\n"
        "stab = pd.DataFrame({'前半段': first, '后半段': second}) * 100\n"
        "stab.index = [f'{k}（{FACTOR_CN[k]}）' for k in stab.index]\n"
        "stab['符号一致'] = np.sign(stab['前半段']) == np.sign(stab['后半段'])\n"
        "stab.round(2)"
    ))
    c.append(_md(
        "## 因子冗余：正交化看增量\n\n"
        "以 HML（价值）和 SMB（规模）为例：把 HML 对 SMB 回归，残差就是 HML 中\n"
        "不能被 SMB 解释的“纯增量”。如果残差与 SMB 的相关性接近 0，说明正交化成功。"
    ))
    c.append(_code(
        "x = factors['SMB'].dropna()\n"
        "y = factors['HML'].reindex(x.index).dropna()\n"
        "x = x.reindex(y.index)\n"
        "coef = np.polyfit(x, y, 1)\n"
        "resid = y - (coef[0] * x + coef[1])\n"
        "print(f'HML 与 SMB 原始相关性: {np.corrcoef(x, y)[0, 1]:.3f}')\n"
        "print(f'正交化后残差与 SMB 相关性: {np.corrcoef(x, resid)[0, 1]:.6f}')\n"
        "print('→ 残差就是 HML 的增量信息，可用于构建“纯净”价值因子')"
    ))
    c.append(_md(
        "## ✋ 试一试\n\n"
        "1. 把样本按“2018-2021 / 2022-2024”重新切分，结论变了吗？\n"
        "2. 把 `factor_summary` 的 `periods_per_year` 改成 252（日频），数字怎么变？\n"
        "3. 换一个因子做正交化（例如 WML 对 MKT），残差相关性是多少？\n\n"
        "## ✅ 本节小结\n\n"
        "- 因子比较要同时看收益、波动、Sharpe、t 值、最大回撤、胜率；\n"
        "- 相关性矩阵判断冗余，正交化看增量；\n"
        "- 分区间稳健性是防止“只在一段样本里有效”的关键；\n"
        "- 示例面板为教学数据，结论不代表真实 A 股。\n\n"
        "> 下一章：把因子组合成多因子模型（FF3、Carhart4、FF5……），并比较谁更好。"
    ))
    nb.cells = c
    return nb


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    notebooks = {
        "03.1-data-and-factors": build_3_1(),
        "03.2-factor-sorting": build_3_2(),
        "03.3-performance-and-robustness": build_3_3(),
    }
    for name, nb in notebooks.items():
        path = OUT / f"{name}.ipynb"
        nbf.write(nb, str(path))
        print(f"built {path}")


if __name__ == "__main__":
    main()
