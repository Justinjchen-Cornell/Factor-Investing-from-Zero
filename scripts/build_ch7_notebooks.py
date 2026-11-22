"""构建第7章教学 notebooks（用 nbformat 生成 .ipynb，保证可复现）。

用法：python scripts/build_ch7_notebooks.py
生成：
- chapters/07-practice/notebooks/07.1-risk-model-and-optimization.ipynb
- chapters/07-practice/notebooks/07.2-smart-beta-and-timing.ipynb
- chapters/07-practice/notebooks/07.3-style-analysis-and-attribution.ipynb
- chapters/07-practice/notebooks/07.4-capstone.ipynb
"""
from __future__ import annotations

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "chapters" / "07-practice" / "notebooks"

CH7_SETUP = (
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
    "from factor_zero.anomalies import rolling_ivol\n"
    "from factor_zero.portfolio import (\n"
    "    FACTOR_ORDER, build_style_exposures, factor_covariance,\n"
    "    specific_variance, portfolio_risk, min_variance_weights,\n"
    "    max_sharpe_weights, style_regression, smart_beta_weights,\n"
    ")\n"
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


def build_7_1() -> nbf.NotebookNode:
    """07.1 风险模型与组合优化。"""
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    c = []
    c.append(_md(
        "# 🎓 第7章 第1课：风险模型与组合优化\n\n"
        "**本节目标**：用简化的风格风险模型估计协方差，再做最小方差/最大 Sharpe 组合。\n\n"
        "对应原书第7章收益率模型、Barra 风险模型、组合优化部分。\n\n"
        "> ⚠️ 本仓库没有行业分类/Barra 因子数据；这里用 7 个风格因子做一个**迷你风险模型**，\n"
        "> 演示“因子暴露 → 协方差 → 组合优化”的流程。数值不代表真实 A 股结论。"
    ))
    c.append(_code(CH7_SETUP))
    c.append(_md(
        "## 1) 迷你风险模型：暴露 × 因子协方差 + 特质风险\n\n"
        "```\n"
        "Σ = B Σ_f B' + D\n"
        "```\n\n"
        "- **B**：股票的风格暴露（截面 z-score）；\n"
        "- **Σ_f**：因子协方差（滚动 36 个月，年化）；\n"
        "- **D**：特质方差（滚动回归残差波动率的平方）。\n\n"
        "这就是 Barra 风险模型的“降维”思想：不直接估计 N×N 协方差，而是用 K 个因子 + 特质风险。"
    ))
    c.append(_code(
        "panel = load_ashare_panel()\n"
        "ret = panel['ret']\n"
        "factors = build_factor_returns(panel, n_groups=10)\n"
        "beta = ret.rolling(24).cov(panel['market']).div(panel['market'].rolling(24).var(), axis=0)\n"
        "ivol = rolling_ivol(ret, factors[FACTOR_ORDER], window=36)\n"
        "date = ret.index[-1]\n"
        "B = build_style_exposures(panel, date, beta)\n"
        "fcov = factor_covariance(factors, date, window=36)\n"
        "sv = specific_variance(ivol, date, B.index)\n"
        "print('暴露矩阵:', B.shape, '| 因子协方差:', fcov.shape, '| 特质方差:', sv.shape)\n"
        "B.head(3).round(3)"
    ))
    c.append(_code(
        "fmean = factors[FACTOR_ORDER].loc[:date].tail(36).mean() * 12  # 年化因子溢价\n"
        "mu = B @ fmean  # 用因子模型给股票预期收益\n"
        "Sigma = B @ fcov @ B.T + pd.DataFrame(np.diag(sv), index=B.index, columns=B.index)\n"
        "print('预期收益（年化）:', mu.describe().round(3).to_dict())\n"
        "print('协方差矩阵:', Sigma.shape)\n"
        "pd.Series(np.diag(Sigma), index=B.index).describe().round(3)"
    ))
    c.append(_md(
        "## 2) 三种组合：等权 / 最小方差 / 最大 Sharpe\n\n"
        "用 `scipy.optimize` 做长仓、权重上限 10% 的约束优化。"
    ))
    c.append(_code(
        "w_eq = pd.Series(1.0 / len(B), index=B.index)\n"
        "w_mv = min_variance_weights(Sigma, max_weight=0.10)\n"
        "w_ms = max_sharpe_weights(mu, Sigma, max_weight=0.10)\n"
        "rows = {}\n"
        "for name, w in [('等权', w_eq), ('最小方差', w_mv), ('最大Sharpe', w_ms)]:\n"
        "    r = portfolio_risk(w, B, fcov, sv)\n"
        "    rows[name] = {\n"
        "        '预期收益': float(w @ mu),\n"
        "        '总波动': r['total_vol'],\n"
        "        '因子波动': r['factor_vol'],\n"
        "        '特质波动': r['specific_vol'],\n"
        "        'Sharpe': float((w @ mu) / r['total_vol']) if r['total_vol'] > 0 else np.nan,\n"
        "    }\n"
        "pd.DataFrame(rows).T.round(4)"
    ))
    c.append(_code(
        "for name, w in [('等权', w_eq), ('最小方差', w_mv), ('最大Sharpe', w_ms)]:\n"
        "    print(name, w.sort_values(ascending=False).head(5).round(3).to_dict())"
    ))
    c.append(_md(
        "## 3) 风险分解：风险从哪里来？\n\n"
        "对最小方差组合做风险归因：每个因子贡献多少波动，特质风险贡献多少。\n"
        "贡献之和 = 总波动（Euler 分解）。"
    ))
    c.append(_code(
        "r = portfolio_risk(w_mv, B, fcov, sv)\n"
        "contrib = r['factor_contrib'].copy()\n"
        "contrib['特质'] = r['specific_contrib']\n"
        "print(f'总波动: {r[\"total_vol\"]*100:.2f}%  因子: {r[\"factor_vol\"]*100:.2f}%  特质: {r[\"specific_vol\"]*100:.2f}%')\n"
        "(contrib * 100).round(2)"
    ))
    c.append(_md(
        "## ✋ 试一试\n\n"
        "1. 把权重上限从 10% 改成 5%，最小方差组合的波动怎么变？\n"
        "2. 把因子协方差窗口从 36 个月改成 24 个月，结果稳定吗？\n"
        "3. 如果把 `mu` 换成历史均值，最大 Sharpe 组合会怎么变？（提示：模型错位）\n\n"
        "## ✅ 本节小结\n\n"
        "- 风险模型用 **B Σ_f B' + D** 降维估计协方差；\n"
        "- 最小方差组合只依赖协方差；最大 Sharpe 还依赖预期收益；\n"
        "- 预期收益估计误差会放大组合权重（模型错位）；\n"
        "- 风险归因把总波动拆成因子贡献 + 特质贡献。\n\n"
        "> 下一课：Smart Beta 与因子择时。"
    ))
    nb.cells = c
    return nb


def build_7_2() -> nbf.NotebookNode:
    """07.2 Smart Beta 与因子择时。"""
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    c = []
    c.append(_md(
        "# 🎓 第7章 第2课：Smart Beta 与因子择时\n\n"
        "**本节目标**：\n\n"
        "1. 用多因子复合分数构建 Smart Beta 组合，比较等权/分数加权/基准；\n"
        "2. 用“趋势信号”做因子择时，看看择时是否真的有用。\n\n"
        "对应原书第7章 Smart Beta 与因子择时部分。\n\n"
        "> ⚠️ 示例面板为教学数据；结果仅演示方法，不代表真实 A 股结论。"
    ))
    c.append(_code(CH7_SETUP))
    c.append(_md(
        "## 1) 多因子复合分数\n\n"
        "```\n"
        "score = z(BM) + z(ROE) + z(动量) − z(换手率) − z(投资)\n"
        "```\n\n"
        "方向：价值、质量、动量越高越好；换手率、投资越低越好。\n"
        "每月选分数最高的 20% 股票，分别用等权和分数加权，持有下个月。"
    ))
    c.append(_code(
        "panel = load_ashare_panel()\n"
        "ret = panel['ret']\n"
        "factors = build_factor_returns(panel, n_groups=10)\n"
        "def z(df):\n"
        "    return df.sub(df.mean(axis=1), axis=0).div(df.std(axis=1), axis=0)\n"
        "score = z(panel['bm']) + z(panel['roe']) + z(panel['momentum']) - z(panel['turnover']) - z(panel['investment'])\n"
        "print('复合分数面板:', score.shape, '| 有效观测:', int(score.notna().sum().sum()))"
    ))
    c.append(_code(
        "dates = ret.index\n"
        "p_eq, p_score, p_bench = [], [], []\n"
        "for t in range(len(dates) - 1):\n"
        "    d, dn = dates[t], dates[t + 1]\n"
        "    s = score.loc[d].dropna()\n"
        "    if len(s) < 20:\n"
        "        continue\n"
        "    top = s.sort_values(ascending=False).head(max(10, int(len(s) * 0.2))).index\n"
        "    w_eq = smart_beta_weights(s.loc[top], method='equal')\n"
        "    w_score = smart_beta_weights(s.loc[top], method='score')\n"
        "    p_eq.append(float((ret.loc[dn, top] * w_eq).sum()))\n"
        "    p_score.append(float((ret.loc[dn, top] * w_score).sum()))\n"
        "    p_bench.append(float(ret.loc[dn].mean()))\n"
        "idx = dates[1:1 + len(p_eq)]\n"
        "port = pd.DataFrame({'等权SmartBeta': p_eq, '分数加权SmartBeta': p_score, '等权基准': p_bench}, index=idx)\n"
        "pd.DataFrame({c: factor_summary(port[c]) for c in port.columns}).T.round(4)"
    ))
    c.append(_code(
        "((1 + port).cumprod()).plot(figsize=(11, 4), title='Smart Beta vs 等权基准：累计净值')\n"
        "plt.axhline(1, color='gray', lw=.8, ls='--'); plt.ylabel('累计净值')\n"
        "plt.legend(); plt.tight_layout(); plt.show()"
    ))
    c.append(_md(
        "## 2) 因子择时：趋势信号有用吗？\n\n"
        "规则：如果某因子过去 12 个月均值为正，下个月持有该因子；否则空仓（收益 0）。\n"
        "对比“一直持有”的买入持有。"
    ))
    c.append(_code(
        "signals = (factors.rolling(12).mean().shift(1) > 0).astype(float)\n"
        "timing = factors * signals\n"
        "rows = {}\n"
        "for col in factors.columns:\n"
        "    bh = factor_summary(factors[col].dropna())\n"
        "    tm = factor_summary(timing[col].dropna())\n"
        "    rows[col] = {\n"
        "        '买入持有年化': bh.get('mean_ann', np.nan),\n"
        "        '择时年化': tm.get('mean_ann', np.nan),\n"
        "        '买入持有t': bh.get('t_stat', np.nan),\n"
        "        '择时t': tm.get('t_stat', np.nan),\n"
        "    }\n"
        "pd.DataFrame(rows).T.round(4)"
    ))
    c.append(_code(
        "compare = pd.DataFrame({\n"
        "    '买入持有': [factor_summary(factors[c].dropna()).get('mean_ann', np.nan) for c in factors.columns],\n"
        "    '趋势择时': [factor_summary(timing[c].dropna()).get('mean_ann', np.nan) for c in factors.columns],\n"
        "}, index=factors.columns)\n"
        "compare.plot(kind='bar', figsize=(11, 4), title='因子择时 vs 买入持有：年化收益')\n"
        "plt.ylabel('年化收益'); plt.xticks(rotation=0); plt.tight_layout(); plt.show()"
    ))
    c.append(_md(
        "## ✋ 试一试\n\n"
        "1. 把选股比例从 20% 改成 10%/30%，组合表现怎么变？\n"
        "2. 把复合分数里的动量去掉，Smart Beta 的结果变了吗？\n"
        "3. 把择时信号从 12 个月改成 6 个月，择时表现更好还是更差？\n\n"
        "## ✅ 本节小结\n\n"
        "- Smart Beta = 用因子分数选股/加权，把因子暴露产品化；\n"
        "- 加权方式（等权/分数/风险）会影响组合的集中度和换手；\n"
        "- 因子择时很难：趋势信号可能有用，也可能增加换手和噪声；\n"
        "- 示例数据下结果不代表真实市场。\n\n"
        "> 下一课：风格分析与归因。"
    ))
    nb.cells = c
    return nb


def build_7_3() -> nbf.NotebookNode:
    """07.3 风格分析与归因。"""
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    c = []
    c.append(_md(
        "# 🎓 第7章 第3课：风格分析与归因\n\n"
        "**本节目标**：\n\n"
        "1. 用 **Sharpe 风格回归** 反推一个组合/基金暴露在哪些因子上；\n"
        "2. 做 **风险归因**：组合波动里，多少来自因子、多少来自特质；\n"
        "3. 做 **业绩归因**：组合收益里，多少来自因子暴露、多少是 α。\n\n"
        "对应原书第7章风格分析与风险归因部分。"
    ))
    c.append(_code(CH7_SETUP))
    c.append(_md(
        "## 1) Sharpe 风格回归：反推组合的因子暴露\n\n"
        "构造一个“假装是基金”的组合：\n\n"
        "```\n"
        "fund = 0.6·MKT + 0.2·HML + 0.1·RMW + 0.1·WML + α + 噪声\n"
        "```\n\n"
        "然后只用基金收益和因子收益做回归，看能不能把 0.6/0.2/0.1/0.1 反推出来。"
    ))
    c.append(_code(
        "panel = load_ashare_panel()\n"
        "factors = build_factor_returns(panel, n_groups=10)\n"
        "rng = np.random.default_rng(7)\n"
        "true_beta = pd.Series({'MKT': 0.6, 'SMB': 0.0, 'HML': 0.2, 'WML': 0.1,\n"
        "                       'RMW': 0.1, 'CMA': 0.0, 'TURN': 0.0})\n"
        "alpha_true = 0.002\n"
        "fund = factors[FACTOR_ORDER] @ true_beta + alpha_true + rng.normal(0, 0.005, len(factors))\n"
        "alpha, betas, r2, resid = style_regression(fund.dropna(), factors[FACTOR_ORDER])\n"
        "print(f'回归 α（月）: {alpha*100:.3f}%   R²: {r2:.3f}')\n"
        "pd.DataFrame({'真实暴露': true_beta, '回归估计': betas}).round(3)"
    ))
    c.append(_md(
        "## 2) 风险归因：价值倾斜组合的风险从哪里来？\n\n"
        "用第 1 课的迷你风险模型，对“高 BM 前 20% 等权组合”做 Euler 分解。"
    ))
    c.append(_code(
        "ret = panel['ret']\n"
        "beta = ret.rolling(24).cov(panel['market']).div(panel['market'].rolling(24).var(), axis=0)\n"
        "ivol = rolling_ivol(ret, factors[FACTOR_ORDER], window=36)\n"
        "date = ret.index[-1]\n"
        "B = build_style_exposures(panel, date, beta)\n"
        "fcov = factor_covariance(factors, date, window=36)\n"
        "sv = specific_variance(ivol, date, B.index)\n"
        "top = B['HML'].sort_values(ascending=False).head(max(10, int(len(B) * 0.2))).index\n"
        "w_tilt = pd.Series(1.0 / len(top), index=top)\n"
        "risk = portfolio_risk(w_tilt, B, fcov, sv)\n"
        "contrib = risk['factor_contrib'].copy(); contrib['特质'] = risk['specific_contrib']\n"
        "print(f'总波动: {risk[\"total_vol\"]*100:.2f}%  因子: {risk[\"factor_vol\"]*100:.2f}%  特质: {risk[\"specific_vol\"]*100:.2f}%')\n"
        "(contrib * 100).round(2)"
    ))
    c.append(_md(
        "## 3) 业绩归因：收益里多少来自因子？\n\n"
        "对**价值倾斜组合**（高 BM 前 20%，等权）做归因：\n"
        "用“组合暴露 × 因子收益”作为因子贡献，剩余部分作为 α。\n"
        "看最近 36 个月的年化贡献。"
    ))
    c.append(_code(
        "window = factors.index[-36:]\n"
        "port_ret = (ret.loc[window, top] * w_tilt).sum(axis=1)\n"
        "Bp = w_tilt.reindex(B.index).fillna(0.0) @ B\n"
        "factor_contrib = factors.loc[window, FACTOR_ORDER].mul(Bp, axis=1)\n"
        "alpha_series = port_ret - factor_contrib.sum(axis=1)\n"
        "summary = pd.DataFrame({\n"
        "    '年化贡献': pd.concat([\n"
        "        factor_contrib.mean() * 12,\n"
        "        pd.Series({'α': alpha_series.mean() * 12}),\n"
        "    ]),\n"
        "})\n"
        "summary.round(4)"
    ))
    c.append(_md(
        "> 🔍 **本例 α 很大（年化约 32%）**：这更可能是模型错位/数据面板问题，而不是真实选股能力。\n"
        "> 归因结果高度依赖风险模型、因子定义和样本；不要看到一个漂亮 α 就当真。\n"
    ))
    c.append(_md(
        "## ✋ 试一试\n\n"
        "1. 把 `true_beta` 的 HML 改成 0.4、RMW 改成 −0.1，回归能反推出来吗？\n"
        "2. 把噪声从 0.005 改成 0.02，R² 和系数估计怎么变？\n"
        "3. 把价值倾斜组合换成等权/最小方差组合，风险/业绩归因怎么变？\n\n"
        "## ✅ 本节小结\n\n"
        "- 风格回归用因子收益反推组合暴露；\n"
        "- 风险归因把波动拆成因子贡献 + 特质贡献；\n"
        "- 业绩归因把收益拆成因子贡献 + α；\n"
        "- 归因是“解释”，不是“预测”；模型不同，归因结果也会不同。\n\n"
        "> 下一课：结业项目——把前面所有工具串起来。"
    ))
    nb.cells = c
    return nb


def build_7_4() -> nbf.NotebookNode:
    """07.4 结业项目：多因子 Smart Beta 组合。"""
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    c = []
    c.append(_md(
        "# 🎓 第7章 第4课：结业项目 —— 多因子 Smart Beta 组合\n\n"
        "**本节目标**：把前六章 + 本章工具串起来，完成一个可复现的结业项目：\n\n"
        "1. 用多因子复合分数选股；\n"
        "2. 分数加权，构建 Smart Beta 组合；\n"
        "3. 对比等权基准，做绩效、换手、风格回归、风险归因；\n"
        "4. 写一份“结业报告”摘要。\n\n"
        "> 这是教学项目，不是投资建议；示例面板为教学数据，结果不代表真实 A 股。"
    ))
    c.append(_code(CH7_SETUP))
    c.append(_md("## 1) 策略定义\n\n- 复合分数：价值 + 质量 + 动量 − 换手 − 投资；\n- 每月选分数最高的 20%；\n- 分数加权（负分数截断为 0）；\n- 持有下个月，月度调仓。"))
    c.append(_code(
        "panel = load_ashare_panel()\n"
        "ret = panel['ret']\n"
        "factors = build_factor_returns(panel, n_groups=10)\n"
        "def z(df):\n"
        "    return df.sub(df.mean(axis=1), axis=0).div(df.std(axis=1), axis=0)\n"
        "score = z(panel['bm']) + z(panel['roe']) + z(panel['momentum']) - z(panel['turnover']) - z(panel['investment'])\n"
        "dates = ret.index\n"
        "port, bench, weight_hist = [], [], {}\n"
        "for t in range(len(dates) - 1):\n"
        "    d, dn = dates[t], dates[t + 1]\n"
        "    s = score.loc[d].dropna()\n"
        "    if len(s) < 20:\n"
        "        continue\n"
        "    top = s.sort_values(ascending=False).head(max(10, int(len(s) * 0.2))).index\n"
        "    w = smart_beta_weights(s.loc[top], method='score')\n"
        "    weight_hist[dn] = w\n"
        "    port.append(float((ret.loc[dn, top] * w).sum()))\n"
        "    bench.append(float(ret.loc[dn].mean()))\n"
        "idx = dates[1:1 + len(port)]\n"
        "port = pd.Series(port, index=idx, name='多因子组合')\n"
        "bench = pd.Series(bench, index=idx, name='等权基准')\n"
        "weights = pd.DataFrame(weight_hist).T.fillna(0.0)\n"
        "print('回测月份:', len(port), '| 持仓股票数（平均）:', int((weights > 0).sum(axis=1).mean()))"
    ))
    c.append(_md("## 2) 绩效对比"))
    c.append(_code(
        "perf = pd.DataFrame({\n"
        "    '多因子组合': factor_summary(port),\n"
        "    '等权基准': factor_summary(bench),\n"
        "}).T\n"
        "perf.columns = ['年化收益', '年化波动', 'Sharpe', 'NW t', '最大回撤', '胜率']\n"
        "perf.round(4)"
    ))
    c.append(_code(
        "((1 + pd.DataFrame({'多因子组合': port, '等权基准': bench})).cumprod()).plot(\n"
        "    figsize=(11, 4), title='结业项目：累计净值'\n"
        ")\n"
        "plt.axhline(1, color='gray', lw=.8, ls='--'); plt.ylabel('累计净值')\n"
        "plt.tight_layout(); plt.show()"
    ))
    c.append(_md("## 3) 换手率与风格暴露"))
    c.append(_code(
        "turnover = 0.5 * weights.diff().abs().sum(axis=1)\n"
        "print(f'平均月度换手率: {turnover.mean()*100:.1f}%')\n"
        "print(f'年化换手率（近似）: {turnover.mean()*12*100:.0f}%')\n"
        "alpha, betas, r2, resid = style_regression(port, factors[FACTOR_ORDER])\n"
        "print(f'风格回归 R²: {r2:.3f}   α（月）: {alpha*100:.3f}%')\n"
        "betas.round(3)"
    ))
    c.append(_md("## 4) 风险归因（最后一期）"))
    c.append(_code(
        "beta = ret.rolling(24).cov(panel['market']).div(panel['market'].rolling(24).var(), axis=0)\n"
        "ivol = rolling_ivol(ret, factors[FACTOR_ORDER], window=36)\n"
        "date = ret.index[-1]\n"
        "B = build_style_exposures(panel, date, beta)\n"
        "fcov = factor_covariance(factors, date, window=36)\n"
        "sv = specific_variance(ivol, date, B.index)\n"
        "w_last = weights.iloc[-1].reindex(B.index).fillna(0.0)\n"
        "risk = portfolio_risk(w_last, B, fcov, sv)\n"
        "contrib = risk['factor_contrib'].copy(); contrib['特质'] = risk['specific_contrib']\n"
        "print(f'总波动: {risk[\"total_vol\"]*100:.2f}%  因子: {risk[\"factor_vol\"]*100:.2f}%  特质: {risk[\"specific_vol\"]*100:.2f}%')\n"
        "(contrib * 100).round(2)"
    ))
    c.append(_md(
        "> ⚠️ **注意模型错位**：这里风险模型给出的总波动（约 70%）远高于回测波动（约 20%）。\n"
        "> 这是“迷你风险模型”的局限：z-score 暴露 × 多空因子收益会高估集中组合的因子风险。\n"
        "> 真实 Barra 模型需要纯因子组合、去相关、特征值调整等。风险模型误差本身也是实践中的大问题。\n"
    ))
    c.append(_md(
        "## 5) 结业报告清单\n\n"
        "- [ ] 策略定义：因子、选股比例、加权方式、调仓频率；\n"
        "- [ ] 数据说明：来源、区间、清洗规则、已知偏差；\n"
        "- [ ] 绩效：年化收益、波动、Sharpe、NW t、最大回撤、胜率；\n"
        "- [ ] 基准：等权/市值加权/因子基准；\n"
        "- [ ] 换手率与交易成本：扣费前后、容量；\n"
        "- [ ] 风格暴露：Sharpe 回归的 β、R²、α；\n"
        "- [ ] 风险归因：因子贡献 + 特质贡献；\n"
        "- [ ] 稳健性：分区间、换窗口、换参数、样本外；\n"
        "- [ ] 结论与局限：哪些是数据窥探/过拟合/样本特定。"
    ))
    c.append(_md(
        "## ✋ 试一试\n\n"
        "1. 把选股比例从 20% 改成 10%，换手率和绩效怎么变？\n"
        "2. 把分数加权改成等权，集中度/换手/绩效怎么变？\n"
        "3. 把复合分数里的动量去掉，结果还稳吗？\n\n"
        "## ✅ 本节小结\n\n"
        "- 结业项目 = 数据 → 因子 → 组合 → 绩效 → 归因 → 报告；\n"
        "- 绩效好不代表可复制：要看换手、成本、容量、稳健性；\n"
        "- 风格回归和风险归因帮助解释“收益/风险从哪里来”；\n"
        "- 示例数据为教学面板，结论不能直接外推。\n\n"
        "> 🎓 恭喜你完成《Factor-Investing-from-Zero》七章课程！"
    ))
    nb.cells = c
    return nb


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    notebooks = {
        "07.1-risk-model-and-optimization": build_7_1(),
        "07.2-smart-beta-and-timing": build_7_2(),
        "07.3-style-analysis-and-attribution": build_7_3(),
        "07.4-capstone": build_7_4(),
    }
    for name, nb in notebooks.items():
        path = OUT / f"{name}.ipynb"
        nbf.write(nb, str(path))
        print(f"built {path}")


if __name__ == "__main__":
    main()
