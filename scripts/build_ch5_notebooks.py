"""构建第5章教学 notebooks（用 nbformat 生成 .ipynb，保证可复现）。

用法：python scripts/build_ch5_notebooks.py
生成：
- chapters/05-anomalies/notebooks/05.1-f-score.ipynb
- chapters/05-anomalies/notebooks/05.2-anchoring-reversal.ipynb
- chapters/05-anomalies/notebooks/05.3-idiosyncratic-volatility.ipynb
"""
from __future__ import annotations

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "chapters" / "05-anomalies" / "notebooks"

CH5_SETUP = (
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
    "from factor_zero.anomalies import (\n"
    "    make_teaching_fundamentals, piotroski_f_score,\n"
    "    distance_from_52w_high, rolling_ivol,\n"
    ")\n"
    "from factor_zero.factors import build_factor_returns\n"
    "from factor_zero.sorting import long_short_factor, monotonicity_test, quantile_group, sort_portfolios\n"
    "from factor_zero.statistics import factor_summary, nw_t_stat\n\n"
    "plt.rcParams['figure.dpi'] = 110\n"
    "plt.rcParams['axes.unicode_minus'] = False\n"
    "plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Noto Sans CJK SC', 'DejaVu Sans']\n"
    "print('✅ 环境就绪，开始学习！')"
)


def _code(s: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(s)


def _md(s: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(s)


def build_5_1() -> nbf.NotebookNode:
    """05.1 F-Score：九信号财务健康评分。"""
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    c = []
    c.append(_md(
        "# 🎓 第5章 第1课：F-Score —— 九信号财务体检\n\n"
        "**本节目标**：用 Piotroski (2000) 的 F-Score，把“财务健康”变成一个 0~9 分的分数，再看高分股是否跑赢低分股。\n\n"
        "对应原书 5.1 节。\n\n"
        "> ⚠️ 数据说明：本仓库没有完整财报，F-Score 的九项信号由**教学合成财务面板**生成。\n"
        "> 本 notebook 演示 F-Score 的计算与排序流程，数值不代表真实公司财务或真实 A 股结论。"
    ))
    c.append(_code(CH5_SETUP))
    c.append(_md(
        "## 1) 九个信号：每一项 1 分\n\n"
        "| # | 信号 | 含义 |\n"
        "|---|---|---|\n"
        "| 1 | ROA > 0 | 盈利能力为正 |\n"
        "| 2 | CFO > 0 | 经营现金流为正 |\n"
        "| 3 | ΔROA > 0 | 盈利能力改善 |\n"
        "| 4 | CFO > ROA | 利润有现金流支撑（应计质量） |\n"
        "| 5 | ΔLeverage < 0 | 杠杆下降 |\n"
        "| 6 | ΔCurrent ratio > 0 | 流动性改善 |\n"
        "| 7 | 没有增发 | 没有通过增发稀释股东 |\n"
        "| 8 | ΔGross margin > 0 | 毛利率改善 |\n"
        "| 9 | ΔAsset turnover > 0 | 资产周转率改善 |\n\n"
        "**F-Score = 9 项之和（0~9 分）**。Piotroski 的经典用法：在“高 BM（便宜）”股票里，\n"
        "买高 F-Score、卖低 F-Score，检验财务健康是否能区分“便宜的好公司”和“价值陷阱”。"
    ))
    c.append(_code(
        "panel = load_ashare_panel()\n"
        "fund = make_teaching_fundamentals(panel)\n"
        "fscore = piotroski_f_score(fund)\n"
        "print('F-Score 面板:', fscore.shape)\n"
        "print('有效分数范围:', np.nanmin(fscore.values), '~', np.nanmax(fscore.values))\n"
        "fscore.stack().value_counts().sort_index().plot(kind='bar', figsize=(8, 3), color='#5B8C5A')\n"
        "plt.title('F-Score 分布（教学合成面板）'); plt.xlabel('F-Score'); plt.ylabel('观测数')\n"
        "plt.tight_layout(); plt.show()"
    ))
    c.append(_md(
        "## 2) 高 F-Score vs 低 F-Score\n\n"
        "每月用 t 期 F-Score 分组，持有 t+1 期：\n\n"
        "- 高分组：F-Score ≥ 7；\n"
        "- 低分组：F-Score ≤ 4；\n"
        "- 多空组合 = 高分组等权收益 − 低分组等权收益。\n\n"
        "> 阈值 7/4 是按本示例面板的分布选的；真实研究常用 8~9 分 vs 0~1 分。"
    ))
    c.append(_code(
        "ret = panel['ret']\n"
        "common = fscore.index.intersection(ret.index)\n"
        "high_rets, low_rets, dates = [], [], []\n"
        "for t in range(len(common) - 1):\n"
        "    d, dn = common[t], common[t + 1]\n"
        "    s = fscore.loc[d].dropna()\n"
        "    high = s[s >= 7].index\n"
        "    low = s[s <= 4].index\n"
        "    if len(high) < 5 or len(low) < 5:\n"
        "        continue\n"
        "    high_rets.append(ret.loc[dn, high].mean())\n"
        "    low_rets.append(ret.loc[dn, low].mean())\n"
        "    dates.append(dn)\n"
        "spread = pd.Series(high_rets, index=dates) - pd.Series(low_rets, index=dates)\n"
        "s = factor_summary(spread)\n"
        "print(f'高F-Score 月均: {np.mean(high_rets)*100:.3f}%')\n"
        "print(f'低F-Score 月均: {np.mean(low_rets)*100:.3f}%')\n"
        "print(f'多空月均: {spread.mean()*100:.3f}%  NW t={s[\"t_stat\"]:.2f}')\n"
        "print(f'年化: {s[\"mean_ann\"]*100:.2f}%  最大回撤: {s[\"max_drawdown\"]*100:.1f}%')"
    ))
    c.append(_md(
        "> 🔍 **本例不显著**：多空月均约 +0.1%，NW t≈0.23。合成面板没有植入 F-Score 溢价，\n"
        "> 这个结果是正常的——notebook 演示的是方法，不是保证异象存在。\n"
    ))
    c.append(_code(
        "nav = (1 + spread).cumprod()\n"
        "fig, ax = plt.subplots(figsize=(10, 4))\n"
        "nav.plot(ax=ax, color='#5B8C5A')\n"
        "ax.axhline(1, color='gray', lw=.8, ls='--')\n"
        "ax.set_title('F-Score 多空组合累计净值（高分组 − 低分组）')\n"
        "ax.set_ylabel('累计净值')\n"
        "plt.tight_layout(); plt.show()"
    ))
    c.append(_md(
        "## ✋ 试一试\n\n"
        "1. 把高/低阈值改成 8/2，样本数和多空收益怎么变？\n"
        "2. 只在高 BM（便宜）股票里做 F-Score 多空，结果会不同吗？\n"
        "3. 把 F-Score 换成“ROA 最高 − ROA 最低”，和 F-Score 的结果比较。\n\n"
        "## ✅ 本节小结\n\n"
        "- F-Score 用 9 个财务信号，把“财务健康”变成一个可排序的分数；\n"
        "- 经典用法：在便宜股里区分“好公司”和“价值陷阱”；\n"
        "- 分数是工具，不是保证；要结合行业、会计口径、样本外检验；\n"
        "- 本 notebook 的财务面板是教学合成数据，结果不代表真实公司。\n\n"
        "> 下一课：基本面锚定反转——价格离 52 周高点有多远？"
    ))
    nb.cells = c
    return nb


def build_5_2() -> nbf.NotebookNode:
    """05.2 基本面锚定反转：52 周高点 + 长期反转。"""
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    c = []
    c.append(_md(
        "# 🎓 第5章 第2课：基本面锚定反转\n\n"
        "**本节目标**：用两个“锚”解释价格反转：\n\n"
        "1. **52 周高点锚定**：价格离过去 12 个月最高点有多远？\n"
        "2. **长期反转**：过去 36 个月的赢家，未来会跑输吗？\n\n"
        "对应原书 5.2 节。\n\n"
        "> ⚠️ 本节使用真实价格快照（87 只股票，2018-2024）；样本小、区间短，\n"
        "> 结果只用于演示方法，不代表真实 A 股结论。"
    ))
    c.append(_code(CH5_SETUP))
    c.append(_md(
        "## 1) 52 周高点锚定：价格 / 过去 12 个月最高价\n\n"
        "`proximity = P_t / max(P_{t-11} ... P_t)`\n\n"
        "- 接近 1：价格贴近 52 周高点；\n"
        "- 接近 0：价格离高点很远。\n\n"
        "**行为解释**：投资者把 52 周高点当“锚”，靠近高点时容易过度乐观，远离高点时过度悲观；\n"
        "锚定误差会导致价格反转。"
    ))
    c.append(_code(
        "panel = load_ashare_panel()\n"
        "ret = panel['ret']\n"
        "month_end = panel['price'].resample('ME').last().ffill().reindex(\n"
        "    index=ret.index, columns=ret.columns\n"
        ")\n"
        "proximity = distance_from_52w_high(month_end, window=12)\n"
        "print('52 周高点距离面板:', proximity.shape)\n"
        "proximity.stack().describe().round(3).to_dict()"
    ))
    c.append(_code(
        "f52, port52, _ = long_short_factor(proximity, ret, n_groups=10, high_minus_low=True)\n"
        "s52 = factor_summary(f52)\n"
        "rho52 = monotonicity_test(port52)['rho']\n"
        "print(f'靠近高点 − 远离高点: 月均 {f52.mean()*100:+.3f}%，年化 {s52[\"mean_ann\"]*100:+.2f}%，NW t={s52[\"t_stat\"]:.2f}')\n"
        "print(f'分组单调性 rho={rho52:.2f}')\n"
        "((1 + f52).cumprod()).plot(figsize=(10, 4), color='#5B7FA6', title='52 周高点多空组合累计净值')\n"
        "plt.axhline(1, color='gray', lw=.8, ls='--'); plt.ylabel('累计净值'); plt.tight_layout(); plt.show()"
    ))
    c.append(_md(
        "## 2) 长期反转：过去 36 个月的输家 vs 赢家\n\n"
        "构造过去 36 个月累计收益（滞后 1 个月，避免同期信息），做多输家、做空赢家。\n"
        "**行为解释**：过度反应 → 长期赢家被高估、输家被低估 → 未来反转。"
    ))
    c.append(_code(
        "past36 = ret.rolling(36).sum().shift(1)\n"
        "f_rev, port_rev, _ = long_short_factor(past36, ret, n_groups=10, high_minus_low=False)\n"
        "s_rev = factor_summary(f_rev)\n"
        "rho_rev = monotonicity_test(port_rev)['rho']\n"
        "print(f'输家 − 赢家: 月均 {f_rev.mean()*100:+.3f}%，年化 {s_rev[\"mean_ann\"]*100:+.2f}%，NW t={s_rev[\"t_stat\"]:.2f}')\n"
        "print(f'分组单调性 rho={rho_rev:.2f}')\n"
        "((1 + f_rev).cumprod()).plot(figsize=(10, 4), color='#F28C28', title='长期反转多空组合累计净值')\n"
        "plt.axhline(1, color='gray', lw=.8, ls='--'); plt.ylabel('累计净值'); plt.tight_layout(); plt.show()"
    ))
    c.append(_md(
        "> 🔍 **本例结果**：52 周高点多空 NW t≈−0.28，长期反转 NW t≈1.12，都不显著；\n"
        "> 方向与“反转”一致，但样本小、区间短，不能据此下结论。\n"
    ))
    c.append(_md(
        "## 3) 两个异象的对比\n\n"
        "| 信号 | 方向 | 经济逻辑 |\n"
        "|---|---|---|\n"
        "| 52 周高点距离 | 靠近高点 − 远离高点 | 锚定/过度反应 |\n"
        "| 长期反转 | 输家 − 赢家 | 过度反应/均值回归 |\n\n"
        "> 两者都可能是“反转”家族，但时间尺度和行为机制不同；相关性要看实际数据。"
    ))
    c.append(_code(
        "pd.DataFrame({\n"
        "    '52周高点': s52,\n"
        "    '长期反转': s_rev,\n"
        "}).T[['mean_ann', 'vol_ann', 'sharpe', 't_stat', 'max_drawdown', 'win_rate']].round(4)"
    ))
    c.append(_md(
        "## ✋ 试一试\n\n"
        "1. 把 52 周窗口从 12 个月改成 6 个月，结果怎么变？\n"
        "2. 把长期反转的回看期从 36 个月改成 24 个月，显著性怎么变？\n"
        "3. 把多空方向反过来，t 值符号怎么变？\n\n"
        "## ✅ 本节小结\n\n"
        "- 52 周高点锚定：价格离高点越远，未来可能反转；\n"
        "- 长期反转：过去 36 个月的输家可能跑赢赢家；\n"
        "- 两者都属于“反转/锚定”家族，但机制和时间尺度不同；\n"
        "- 真实价格样本小，结果不能直接外推。\n\n"
        "> 下一课：特质波动率——动得厉害，收益更高还是更低？"
    ))
    nb.cells = c
    return nb


def build_5_3() -> nbf.NotebookNode:
    """05.3 特质波动率：低 IVOL − 高 IVOL。"""
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    c = []
    c.append(_md(
        "# 🎓 第5章 第3课：特质波动率（IVOL）\n\n"
        "**本节目标**：检验“特质波动率之谜”：\n\n"
        "- 用 FF3 回归的残差波动率衡量“特质风险”；\n"
        "- 按 IVOL 分组，做多低 IVOL、做空高 IVOL；\n"
        "- 看低波动组是否反而收益更高（负相关）。\n\n"
        "对应原书 5.3 节。\n\n"
        "> ⚠️ IVOL 使用真实价格 + 第3章因子（部分因子为教学面板），样本仅 87 只股票；\n"
        "> 结果仅用于演示方法，不代表真实 A 股结论。"
    ))
    c.append(_code(CH5_SETUP))
    c.append(_code(
        "panel = load_ashare_panel()\n"
        "ret = panel['ret']\n"
        "factors = build_factor_returns(panel, n_groups=10)\n"
        "ff3 = factors[['MKT', 'SMB', 'HML']]\n"
        "ivol = rolling_ivol(ret, ff3, window=24)\n"
        "print('IVOL 面板:', ivol.shape)\n"
        "print('有效观测:', int(ivol.notna().sum().sum()))\n"
        "ivol.stack().describe().round(4)"
    ))
    c.append(_md(
        "## 1) IVOL 的直觉\n\n"
        "- **特质风险**：不能被市场/规模/价值解释的个股波动；\n"
        "- 传统金融：高风险应该高收益；\n"
        "- 实证谜题：高 IVOL 股票的未来收益反而更低（IVOL 负相关）；\n"
        "- 解释：套利限制 + 投资者偏好彩票型股票 → 高 IVOL 被高估。\n\n"
        "下面用分组检验看这个关系。"
    ))
    c.append(_code(
        "f_ivol, port_ivol, _ = long_short_factor(ivol, ret, n_groups=10, high_minus_low=False)\n"
        "s_ivol = factor_summary(f_ivol)\n"
        "rho_ivol = monotonicity_test(port_ivol)['rho']\n"
        "print(f'低IVOL − 高IVOL: 月均 {f_ivol.mean()*100:+.3f}%，年化 {s_ivol[\"mean_ann\"]*100:+.2f}%，NW t={s_ivol[\"t_stat\"]:.2f}')\n"
        "print(f'分组单调性 rho={rho_ivol:.2f}（组1=低IVOL，组10=高IVOL）')\n"
        "((1 + f_ivol).cumprod()).plot(figsize=(10, 4), color='#5B8C5A', title='低IVOL − 高IVOL 累计净值')\n"
        "plt.axhline(1, color='gray', lw=.8, ls='--'); plt.ylabel('累计净值'); plt.tight_layout(); plt.show()"
    ))
    c.append(_code(
        "means = port_ivol.mean() * 100\n"
        "means.plot(kind='bar', figsize=(9, 3), color='#5B7FA6')\n"
        "plt.title('IVOL 十分组的月均收益（1=低IVOL，10=高IVOL）')\n"
        "plt.xlabel('组别'); plt.ylabel('月均收益（%）'); plt.tight_layout(); plt.show()\n"
        "means.round(3)"
    ))
    c.append(_md(
        "> 🔍 **本例结果与经典 IVOL 之谜相反**：低 IVOL − 高 IVOL 为负、rho≈+0.68，\n"
        "> 即高 IVOL 组反而收益更高。这说明异象对样本、窗口、因子模型很敏感；\n"
        "> 不要把单一结果当规律，也不要因此否定原书/文献的结论。\n"
    ))
    c.append(_md(
        "## 2) 控制市值：IVOL 会不会只是小盘股的“马甲”？\n\n"
        "先按市值分 3 层，每层内按 IVOL 分 5 组，算“低 IVOL − 高 IVOL”。\n"
        "如果每层内价差仍然存在，说明 IVOL 不是规模因子的替身。"
    ))
    c.append(_code(
        "common = ret.index.intersection(ivol.index).intersection(panel['size'].index)\n"
        "spreads = {1: [], 2: [], 3: []}\n"
        "for t in range(len(common) - 1):\n"
        "    d, dn = common[t], common[t + 1]\n"
        "    sg = quantile_group(panel['size'].loc[d].dropna(), n_groups=3)\n"
        "    for layer in [1, 2, 3]:\n"
        "        inside = sg[sg == layer].index\n"
        "        iv = ivol.loc[d, inside].dropna()\n"
        "        if len(iv) < 5:\n"
        "            continue\n"
        "        g = quantile_group(iv, n_groups=5)\n"
        "        sub_ret = ret.loc[[dn], g.index]\n"
        "        sub_g = g.to_frame().T.copy(); sub_g.index = [dn]\n"
        "        port_s = sort_portfolios(sub_ret, sub_g, n_groups=5)\n"
        "        spreads[layer].append(port_s.iloc[0, 0] - port_s.iloc[0, 4])\n\n"
        "for layer in [1, 2, 3]:\n"
        "    s = pd.Series(spreads[layer])\n"
        "    t_nw, _ = nw_t_stat(s)\n"
        "    print(f'市值第{layer}层（{\"小\" if layer==1 else \"中\" if layer==2 else \"大\"}）：'\n"
        "          f'低-高 IVOL {s.mean()*100:+.3f}%/月，NW t={t_nw:.2f}，共{len(s)}期')"
    ))
    c.append(_md(
        "## ✋ 试一试\n\n"
        "1. 把 IVOL 窗口从 24 个月改成 12 个月，结果怎么变？\n"
        "2. 用 FF5 而不是 FF3 算残差，IVOL 的显著性怎么变？\n"
        "3. 把方向换成“高 IVOL − 低 IVOL”，t 值符号怎么变？\n\n"
        "## ✅ 本节小结\n\n"
        "- IVOL = 多因子回归残差的波动率，衡量特质风险；\n"
        "- 实证上高 IVOL 往往伴随更低未来收益（IVOL 之谜）；\n"
        "- 控制市值后仍可能存在，但结果依赖样本、窗口和因子模型；\n"
        "- 本 notebook 的样本和因子面板有限，结论不能直接外推。\n\n"
        "> 下一章：因子研究现状——p-hacking、因子动物园、机器学习。"
    ))
    nb.cells = c
    return nb


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    notebooks = {
        "05.1-f-score": build_5_1(),
        "05.2-anchoring-reversal": build_5_2(),
        "05.3-idiosyncratic-volatility": build_5_3(),
    }
    for name, nb in notebooks.items():
        path = OUT / f"{name}.ipynb"
        nbf.write(nb, str(path))
        print(f"built {path}")


if __name__ == "__main__":
    main()
