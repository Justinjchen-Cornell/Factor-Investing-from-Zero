"""构建第4章教学 notebooks（用 nbformat 生成 .ipynb，保证可复现）。

用法：python scripts/build_ch4_notebooks.py
生成：
- chapters/04-multi-factor-models/notebooks/04.1-seven-models.ipynb
- chapters/04-multi-factor-models/notebooks/04.2-model-comparison.ipynb
- chapters/04-multi-factor-models/notebooks/04.3-priced-factors-and-parsimony.ipynb
"""
from __future__ import annotations

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "chapters" / "04-multi-factor-models" / "notebooks"

CH4_SETUP = (
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
    "from factor_zero.models import (\n"
    "    MODEL_DEFINITIONS, model_factor_frame, build_test_assets,\n"
    "    evaluate_model, compare_models,\n"
    ")\n"
    "from factor_zero.regression import fama_macbeth, time_series_betas\n"
    "from factor_zero.statistics import factor_summary\n\n"
    "plt.rcParams['figure.dpi'] = 110\n"
    "plt.rcParams['axes.unicode_minus'] = False\n"
    "plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Noto Sans CJK SC', 'DejaVu Sans']\n"
    "print('✅ 环境就绪，开始学习！')"
)

FACTOR_CN = {
    "MKT": "市场", "SMB": "规模", "HML": "价值",
    "WML": "动量", "RMW": "盈利", "CMA": "投资", "TURN": "换手率",
}


def _code(s: str) -> nbf.NotebookNode:
    return nbf.v4.new_code_cell(s)


def _md(s: str) -> nbf.NotebookNode:
    return nbf.v4.new_markdown_cell(s)


def build_4_1() -> nbf.NotebookNode:
    """04.1 七大模型：从三因子到 q-factor。"""
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    c = []
    c.append(_md(
        "# 🎓 第4章 第1课：七大模型 —— 从三因子到 q-factor\n\n"
        "**本节目标**：把第3章的七个因子组合成七个主流多因子模型，看清它们之间的关系。\n\n"
        "对应原书第4章。模型不是“因子越多越好”，而是**用尽量少的因子解释尽量多的收益差异**。\n\n"
        "> ⚠️ 数据声明：本仓库的估值/ROE/投资为教学合成面板；模型比较的数值仅演示流程，不代表真实 A 股结论。"
    ))
    c.append(_code(CH4_SETUP))
    c.append(_md(
        "## 1) 七个模型的定义\n\n"
        "| 模型 | 因子 | 一句话 |\n"
        "|---|---|---|\n"
        "| FF3 | MKT + SMB + HML | 市场、规模、价值 |\n"
        "| Carhart4 | FF3 + WML | 加动量 |\n"
        "| NovyMarx4 | MKT + HML + WML + RMW | 市场、价值、动量、盈利 |\n"
        "| FF5 | MKT + SMB + HML + RMW + CMA | 加盈利、投资 |\n"
        "| HXZ4 | MKT + SMB + RMW + CMA | q-factor：市场、规模、盈利、投资 |\n"
        "| SY4 | MKT + SMB + RMW + WML | 近似：RMW/WML 代理 MGMT/PERF |\n"
        "| DHS3 | MKT + HML + WML | 近似：HML/WML 代理 FIN/PEAD |\n\n"
        "> SY4 和 DHS3 的真实因子（MGMT/PERF、FIN/PEAD）本仓库数据无法精确构造，\n"
        "> 这里用现有因子做“近似代理”，只用于演示模型比较流程，**不代表原模型**。"
    ))
    c.append(_code(
        "panel = load_ashare_panel()\n"
        "factors = build_factor_returns(panel, n_groups=10)\n"
        "model_table = pd.DataFrame([\n"
        "    {'模型': name, '因子数': len(spec['factors']),\n"
        "     '因子': ' + '.join(spec['factors']), '说明': spec['note']}\n"
        "    for name, spec in MODEL_DEFINITIONS.items()\n"
        "]).set_index('模型')\n"
        "model_table"
    ))
    c.append(_md(
        "## 2) 模型之间的关系\n\n"
        "- **FF3 ⊂ Carhart4**：Carhart4 = FF3 + 动量；\n"
        "- **FF3 ⊂ FF5**：FF5 = FF3 + 盈利 + 投资；\n"
        "- **HXZ4** 和 FF5 共享 MKT/SMB/RMW/CMA，但 HXZ4 不含 HML；\n"
        "- **NovyMarx4** 不含 SMB，强调价值、动量、盈利；\n"
        "- **SY4/DHS3** 在这里是近似代理，不是原版模型。\n\n"
        "> 嵌套模型可以用 GRS/α 检验比较；非嵌套模型还可以看均值-方差张成。"
    ))
    c.append(_code(
        "rows = []\n"
        "for name in MODEL_DEFINITIONS:\n"
        "    mf = model_factor_frame(factors, name)\n"
        "    rows.append({'模型': name, '因子数': mf.shape[1],\n"
        "                 '有效月份': int(mf.dropna().shape[0]),\n"
        "                 '因子': ' + '.join(mf.columns)})\n"
        "pd.DataFrame(rows).set_index('模型')"
    ))
    c.append(_md(
        "## 3) 先看一眼：不同模型的因子收益\n\n"
        "同一组因子，组合方式不同，模型的“性格”也不同。\n"
        "下一课会用 GRS 正式比较；这里先建立直觉。"
    ))
    c.append(_code(
        "summary = {}\n"
        "for name in ['FF3', 'Carhart4', 'FF5', 'HXZ4']:\n"
        "    mf = model_factor_frame(factors, name)\n"
        "    # 用等权因子组合代表模型（仅作直觉展示）\n"
        "    summary[name] = mf.mean(axis=1)\n"
        "pd.DataFrame({name: factor_summary(pd.Series(vals).dropna())\n"
        "              for name, vals in summary.items()}).T.round(4)"
    ))
    c.append(_md(
        "## ✋ 试一试\n\n"
        "1. 把 FF5 的 CMA 去掉，和 FF3+WML 比，哪个平均 |α| 更低？（下一课验证）\n"
        "2. 把 HXZ4 的 RMW 换成 HML，模型变成什么？\n"
        "3. 如果只能用 3 个因子，你会选哪 3 个？为什么？\n\n"
        "## ✅ 本节小结\n\n"
        "- 七大模型是七个因子集的不同组合；\n"
        "- 嵌套关系：FF3 ⊂ Carhart4、FF3 ⊂ FF5；\n"
        "- 模型选择不是“越多越好”，要看解释力、显著性和简约性；\n"
        "- SY4/DHS3 在本仓库是近似代理，不能当作原模型结论。\n\n"
        "> 下一课：用 GRS 检验正式比较七个模型。"
    ))
    nb.cells = c
    return nb


def build_4_2() -> nbf.NotebookNode:
    """04.2 模型比较：GRS 体检。"""
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    c = []
    c.append(_md(
        "# 🎓 第4章 第2课：模型比较 —— GRS 体检\n\n"
        "**本节目标**：用同一组测试资产，比较七个多因子模型。\n\n"
        "- **GRS**：所有测试资产的 α 是否联合为零？p 值大 → 模型通过体检；\n"
        "- **平均 |α|**：模型解释不了的收益差异有多大；\n"
        "- **平均 R²**：模型能解释多少收益波动。\n\n"
        "对应原书 4.1~4.7 节。"
    ))
    c.append(_code(CH4_SETUP))
    c.append(_code(
        "panel = load_ashare_panel()\n"
        "factors = build_factor_returns(panel, n_groups=10)\n"
        "assets = build_test_assets(panel, n_groups=5)\n"
        "print('测试资产:', assets.shape[1], '个组合')\n"
        "print('样本期:', assets.dropna().index.min().date(), '→', assets.dropna().index.max().date())\n"
        "assets.iloc[:3, :5].round(4)"
    ))
    c.append(_md(
        "## 1) 七个模型的 GRS 比较\n\n"
        "对每个模型，把 15 个测试资产（BM/SIZE/MOM 各 5 组）对它做时序回归，\n"
        "再联合检验所有 α 是否为零。"
    ))
    c.append(_code(
        "comp = compare_models(factors, assets)\n"
        "comp_sorted = comp.sort_values('mean_abs_alpha_ann')\n"
        "comp_sorted.round(4)"
    ))
    c.append(_md(
        "### 怎么读？\n\n"
        "- **grs_p 大**：不能拒绝“α 全为零”，模型通过体检；\n"
        "- **平均 |α| 小**：模型留下的定价误差小；\n"
        "- **平均 R² 高**：模型解释的波动多；\n"
        "- **因子数 k**：越多不一定越好——要看解释力提升是否值得复杂度。\n\n"
        "> ⚠️ 本样本 GRS 的 p 值可能都不小（样本短、测试资产少、功效低），\n"
        "> 这时不要只看 p 值，要结合平均 |α|、R² 和经济学逻辑。"
    ))
    c.append(_code(
        "fig, axes = plt.subplots(1, 2, figsize=(14, 4))\n"
        "comp_sorted['mean_abs_alpha_ann'].plot(kind='bar', ax=axes[0], color='#5B8C5A')\n"
        "axes[0].set_title('平均 |α|（年化，越小越好）')\n"
        "axes[0].set_ylabel('年化 |α|')\n"
        "comp_sorted['avg_r2'].plot(kind='bar', ax=axes[1], color='#F28C28')\n"
        "axes[1].set_title('平均 R²（越大越好）')\n"
        "axes[1].set_ylabel('R²')\n"
        "plt.tight_layout(); plt.show()"
    ))
    c.append(_md(
        "## 2) 以 FF3 为例：哪些测试资产的 α 最大？\n\n"
        "GRS 只回答“联合是否为零”，不指出具体资产。逐个看 α 可以定位问题。"
    ))
    c.append(_code(
        "mf = model_factor_frame(factors, 'FF3')\n"
        "data = pd.concat([assets, mf], axis=1).dropna()\n"
        "alphas, betas, resid = time_series_betas(data[assets.columns], data[mf.columns])\n"
        "alphas_ann = (alphas * 12).sort_values(key=np.abs, ascending=False)\n"
        "alphas_ann.head(10).round(4)"
    ))
    c.append(_md(
        "## ✋ 试一试\n\n"
        "1. 把测试资产从 5 组改成 10 组，GRS 的 p 值和平均 |α| 怎么变？\n"
        "2. 把 `SY4`/`DHS3` 从比较中删掉，只看五个“正统”模型，排名变了吗？\n"
        "3. 用 FF3 的 α 排序，哪些组合最容易被 FF3 错误定价？\n\n"
        "## ✅ 本节小结\n\n"
        "- GRS 联合检验 α 是否为零，p 值大 → 模型通过；\n"
        "- p 值不够时，结合平均 |α|、R²、经济学逻辑；\n"
        "- 因子越多不一定越好，要看解释力提升和简约性；\n"
        "- SY4/DHS3 在本仓库是近似代理，结果只用于演示。\n\n"
        "> 下一课：A 股被定价因子 + 简约性。"
    ))
    nb.cells = c
    return nb


def build_4_3() -> nbf.NotebookNode:
    """04.3 A 股被定价因子 + 简约性。"""
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    c = []
    c.append(_md(
        "# 🎓 第4章 第3课：A 股被定价因子 + 简约性\n\n"
        "**本节目标**：做两件事：\n\n"
        "1. 用 **Fama-MacBeth** 检验哪些特征（beta/规模/价值/盈利/投资/换手/动量）被定价；\n"
        "2. 用 **GRS + 平均 |α| + R²** 讨论多因子模型的简约性：因子越多越好吗？\n\n"
        "对应原书 4.8~4.9 节。"
    ))
    c.append(_code(CH4_SETUP))
    c.append(_code(
        "panel = load_ashare_panel()\n"
        "ret, market = panel['ret'], panel['market']\n"
        "beta = ret.rolling(24).cov(market).div(market.rolling(24).var(), axis=0)\n"
        "chars = {\n"
        "    'BETA': beta, 'SIZE': panel['size'], 'BM': panel['bm'],\n"
        "    'ROE': panel['roe'], 'INV': panel['investment'],\n"
        "    'TURN': panel['turnover'], 'MOM': panel['momentum'],\n"
        "}\n"
        "def zscore(df):\n"
        "    return df.sub(df.mean(axis=1), axis=0).div(df.std(axis=1), axis=0)\n"
        "print('特征矩阵数量:', len(chars), '| 股票数:', ret.shape[1], '| 月份数:', ret.shape[0])"
    ))
    c.append(_md(
        "## 1) 单变量 FM：每个特征单独看\n\n"
        "每次只放一个特征（加截距），看它的 λ 和 NW t。\n"
        "这回答“单独看，这个特征被定价吗？”"
    ))
    c.append(_code(
        "uni = {}\n"
        "for name, df in chars.items():\n"
        "    X = np.nan_to_num(zscore(df).to_numpy()[:, :, None], nan=0.0)\n"
        "    lam, lam_t, se, t = fama_macbeth(ret, X)\n"
        "    uni[name] = {'lambda': lam[1], 'NW t': t[1]}\n"
        "uni_table = pd.DataFrame(uni).T\n"
        "uni_table.round(4)"
    ))
    c.append(_md(
        "## 2) 多变量 FM：一起看\n\n"
        "把所有特征同时放入截面回归。\n"
        "**注意**：特征之间可能相关，多变量 λ 的符号可能和单变量不同（多重共线性/相互控制）。"
    ))
    c.append(_code(
        "X = np.stack([np.nan_to_num(zscore(v).to_numpy(), nan=0.0)\n"
        "              for v in chars.values()], axis=2)\n"
        "lam, lam_t, se, t = fama_macbeth(ret, X)\n"
        "multi_table = pd.DataFrame({\n"
        "    'lambda': lam[1:], '标准误': se[1:], 'NW t': t[1:],\n"
        "}, index=list(chars.keys()))\n"
        "multi_table.round(4)"
    ))
    c.append(_md(
        "### 怎么读“被定价”？\n\n"
        "- |NW t| > 2：在 95% 置信下显著；\n"
        "- λ 的符号要和经济学逻辑对照：例如价值（BM）通常预期正 λ，换手率通常预期负 λ；\n"
        "- 单变量和多变量符号不一致，说明特征之间存在相关性，需要谨慎解释。\n\n"
        "> ⚠️ 本仓库的估值/ROE/投资是教学合成面板。你在这里看到的符号和显著性\n"
        "> **不能直接当作真实 A 股结论**；原书的 A 股结论请以原书样本与口径为准。"
    ))
    c.append(_md(
        "## 3) 简约性：因子越多越好吗？\n\n"
        "把七个模型的因子数、平均 |α|、平均 R² 放在一起看。\n"
        "好的模型不是“因子最多”，而是**用较少因子解释较多差异**。"
    ))
    c.append(_code(
        "factors = build_factor_returns(panel, n_groups=10)\n"
        "assets = build_test_assets(panel, n_groups=5)\n"
        "comp = compare_models(factors, assets)\n"
        "comp[['k', 'mean_abs_alpha_ann', 'avg_r2', 'grs_p']].sort_values('k').round(4)"
    ))
    c.append(_code(
        "fig, axes = plt.subplots(1, 2, figsize=(14, 4))\n"
        "for ax, col, title in [\n"
        "    (axes[0], 'mean_abs_alpha_ann', '因子数 vs 平均 |α|（越低越好）'),\n"
        "    (axes[1], 'avg_r2', '因子数 vs 平均 R²（越高越好）'),\n"
        "]:\n"
        "    for name, row in comp.iterrows():\n"
        "        ax.scatter(row['k'], row[col], s=70)\n"
        "        ax.annotate(name, (row['k'], row[col]), fontsize=8,\n"
        "                    xytext=(4, 4), textcoords='offset points')\n"
        "    ax.set_title(title); ax.set_xlabel('因子数 k')\n"
        "plt.tight_layout(); plt.show()"
    ))
    c.append(_md(
        "## ✋ 试一试\n\n"
        "1. 把 `chars` 里的 `BETA` 去掉，多变量 FM 的符号怎么变？\n"
        "2. 把 `TURN` 换成“高换手 − 低换手”，单变量 λ 的符号怎么变？\n"
        "3. 在 `compare_models` 里加一个“只有 MKT”的模型，看它的平均 |α| 和 R²。\n\n"
        "## ✅ 本节小结\n\n"
        "- FM 可以检验哪些特征被定价；单变量和多变量要分开看；\n"
        "- 特征相关时，多变量 λ 的符号可能变化；\n"
        "- 模型选择要平衡解释力与简约性：因子越多，过拟合和噪声越大；\n"
        "- 示例面板为教学数据，结论不能直接外推到真实 A 股。\n\n"
        "> 下一章：异象研究——F-Score、基本面锚定反转、特质波动率。"
    ))
    nb.cells = c
    return nb


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    notebooks = {
        "04.1-seven-models": build_4_1(),
        "04.2-model-comparison": build_4_2(),
        "04.3-priced-factors-and-parsimony": build_4_3(),
    }
    for name, nb in notebooks.items():
        path = OUT / f"{name}.ipynb"
        nbf.write(nb, str(path))
        print(f"built {path}")


if __name__ == "__main__":
    main()
