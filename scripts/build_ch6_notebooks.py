"""构建第6章教学 notebooks（用 nbformat 生成 .ipynb，保证可复现）。

用法：python scripts/build_ch6_notebooks.py
生成：
- chapters/06-current-research/notebooks/06.1-p-hacking-and-factor-zoo.ipynb
- chapters/06-current-research/notebooks/06.2-behavioral-finance.ipynb
- chapters/06-current-research/notebooks/06.3-machine-learning-and-overfitting.ipynb
"""
from __future__ import annotations

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "chapters" / "06-current-research" / "notebooks"

CH6_SETUP = (
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
    "from factor_zero.research import (\n"
    "    simulate_random_factors, p_hacking_summary,\n"
    "    publication_decay_experiment, polynomial_train_test_mse, sentiment_signal,\n"
    ")\n"
    "from factor_zero.data import load_ashare_panel\n"
    "from factor_zero.factors import build_factor_returns\n"
    "from factor_zero.sorting import long_short_factor, monotonicity_test\n"
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


def build_6_1() -> nbf.NotebookNode:
    """06.1 p-hacking 与因子动物园。"""
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    c = []
    c.append(_md(
        "# 🎓 第6章 第1课：p-hacking 与因子动物园\n\n"
        "**本节目标**：亲手模拟“数据窥探”如何制造假因子，并理解发表偏差/因子动物园。\n\n"
        "对应原书第6章前半部分。\n\n"
        "1. 生成 1000 个**纯噪声**因子，看 |t|>2 / 3 / 3.4 能挖出多少“显著因子”；\n"
        "2. 模拟“挑最好区间发表”，看样本外衰减；\n"
        "3. 认识因子动物园与因子大战。"
    ))
    c.append(_code(CH6_SETUP))
    c.append(_md(
        "## 1) 纯噪声里能挖出多少“显著因子”？\n\n"
        "如果因子根本没有溢价，t 值应该围绕 0 波动。\n"
        "但研究者会试很多因子、很多口径——只要试得够多，总能找到“显著”的。\n\n"
        "下面生成 **1000 个纯噪声因子**，每个 120 期，计算均值的 t 值。"
    ))
    c.append(_code(
        "factors = simulate_random_factors(n_factors=1000, n_periods=120, seed=2020)\n"
        "summary = p_hacking_summary(factors['t_stat'])\n"
        "print('纯噪声因子的 t 值分布:')\n"
        "print(factors['t_stat'].describe().round(3).to_dict())\n"
        "summary.round(4)"
    ))
    c.append(_code(
        "fig, ax = plt.subplots(figsize=(9, 4))\n"
        "ax.hist(factors['t_stat'], bins=50, alpha=.75, color='#5B8C5A')\n"
        "for thr, color in [(2.0, 'orange'), (3.0, 'red'), (3.4, 'purple')]:\n"
        "    ax.axvline(thr, color=color, ls='--', label=f'|t|={thr}')\n"
        "    ax.axvline(-thr, color=color, ls='--')\n"
        "ax.set_xlabel('t 值'); ax.set_ylabel('因子数量')\n"
        "ax.set_title('1000 个纯噪声因子的 t 值分布')\n"
        "ax.legend(); plt.tight_layout(); plt.show()"
    ))
    c.append(_md(
        "### 三个门槛的含义\n\n"
        "- **|t| > 2.0**：传统 5% 显著；1000 个噪声里约 5% 会“显著”（约 50 个）；\n"
        "- **|t| > 3.0**：Harvey et al. (2016) 建议，应对多重检验；\n"
        "- **|t| > 3.4**：Chordia et al. (2020) 更严格的门槛。\n\n"
        "> 关键不是“t 值大不大”，而是**你试了多少次**。试得越多，假阳性越多。"
    ))
    c.append(_md(
        "## 2) 发表偏差：挑最好区间发表，样本外会怎样？\n\n"
        "模拟：真实月均溢价 0.4%，噪声 3%，共 240 个月。\n"
        "研究者挑“表现最好的 60 个月”发表；我们看全样本（长期真相）相对发表前衰减多少。\n"
        "重复 500 次，看平均衰减。"
    ))
    c.append(_code(
        "decay = publication_decay_experiment(n_simulations=500, true_premium=0.004, noise=0.03, seed=7)\n"
        "print(f'发表前月均（中位数）: {decay[\"in_sample\"].median()*100:.3f}%')\n"
        "print(f'全样本月均（中位数）: {decay[\"full_sample\"].median()*100:.3f}%')\n"
        "print(f'衰减中位数: {decay[\"decay\"].median()*100:.1f}%')\n"
        "print(f'衰减均值:   {decay[\"decay\"].mean()*100:.1f}%')\n"
        "decay[['in_sample','full_sample','decay']].describe().round(4)"
    ))
    c.append(_code(
        "fig, ax = plt.subplots(figsize=(8, 4))\n"
        "ax.hist(decay['decay'].dropna(), bins=40, color='#F28C28', alpha=.8)\n"
        "ax.axvline(0, color='gray', ls='--')\n"
        "ax.set_xlabel('衰减 = 1 − 全样本均值 / 发表前均值')\n"
        "ax.set_ylabel('模拟次数')\n"
        "ax.set_title('挑选最优区间后的样本外衰减')\n"
        "plt.tight_layout(); plt.show()"
    ))
    c.append(_md(
        "## 3) 因子动物园与因子大战\n\n"
        "| 时间/研究 | 结论 |\n"
        "|---|---|\n"
        "| Cochrane (2011) | 学术界的“因子动物园”：已挖出 400+ 因子 |\n"
        "| Harvey et al. (2016) | 多重检验下，t 门槛应从 2.0 提高到 3.0 |\n"
        "| Chordia et al. (2020) | 进一步建议 t > 3.4 |\n"
        "| McLean & Pontiff (2016) | 因子发表后收益平均衰减 50%+ |\n\n"
        "**因子大战**：不同研究互相“打架”——同一因子在不同样本、口径、区间下结论不同。\n"
        "这不是坏事：它逼着研究者做样本外、稳健性和经济逻辑检验。\n\n"
        "> 读论文时先问三件事：**样本外还活着吗？换了口径还成立吗？有经济逻辑吗？**"
    ))
    c.append(_md(
        "## ✋ 试一试\n\n"
        "1. 把因子数量从 1000 改成 5000，|t|>2 的“显著因子”数量怎么变？\n"
        "2. 把噪声从 0.03 改成 0.01，发表后衰减会更严重还是更轻？\n"
        "3. 把 `in_sample` 从 60 改成 12，衰减怎么变？\n\n"
        "## ✅ 本节小结\n\n"
        "- 纯噪声里也能挖出“显著因子”，试得越多假阳性越多；\n"
        "- 挑选最优区间发表，会高估因子收益，样本外衰减；\n"
        "- 因子动物园/因子大战要求更高的 t 门槛、样本外和稳健性；\n"
        "- 不要只看“显著”，要看“试了多少次、是否样本外、是否有逻辑”。\n\n"
        "> 下一课：行为金融——投资者情绪与过度反应。"
    ))
    nb.cells = c
    return nb


def build_6_2() -> nbf.NotebookNode:
    """06.2 行为金融与投资者情绪。"""
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    c = []
    c.append(_md(
        "# 🎓 第6章 第2课：行为金融与投资者情绪\n\n"
        "**本节目标**：用换手率 + 近期收益构造“情绪代理”，检验高情绪股票是否跑输。\n\n"
        "对应原书第6章行为金融部分。\n\n"
        "> ⚠️ 使用真实价格/成交量快照（87 只股票）；结果仅用于演示方法，不代表真实 A 股结论。"
    ))
    c.append(_code(CH6_SETUP))
    c.append(_code(
        "panel = load_ashare_panel()\n"
        "ret = panel['ret']\n"
        "sentiment = sentiment_signal(panel)\n"
        "print('情绪面板:', sentiment.shape)\n"
        "sentiment.stack().describe().round(3).to_dict()"
    ))
    c.append(_md(
        "## 1) 情绪代理：高换手 + 近期上涨\n\n"
        "```\n"
        "sentiment = zscore(换手率) + zscore(上期收益)\n"
        "```\n\n"
        "- 高值：高换手 + 近期涨得多 → 情绪偏热；\n"
        "- 低值：低换手 + 近期跌得多 → 情绪偏冷。\n\n"
        "**行为逻辑**：过度自信、追涨杀跌、注意力效应 → 高情绪股票被高估，未来可能跑输。"
    ))
    c.append(_code(
        "f_sent, port_sent, _ = long_short_factor(sentiment, ret, n_groups=10, high_minus_low=False)\n"
        "s_sent = factor_summary(f_sent)\n"
        "rho_sent = monotonicity_test(port_sent)['rho']\n"
        "print(f'低情绪 − 高情绪: 月均 {f_sent.mean()*100:+.3f}%，年化 {s_sent[\"mean_ann\"]*100:+.2f}%，NW t={s_sent[\"t_stat\"]:.2f}')\n"
        "print(f'分组单调性 rho={rho_sent:.2f}')\n"
        "((1 + f_sent).cumprod()).plot(figsize=(10, 4), color='#5B8C5A', title='低情绪 − 高情绪 累计净值')\n"
        "plt.axhline(1, color='gray', lw=.8, ls='--'); plt.ylabel('累计净值'); plt.tight_layout(); plt.show()"
    ))
    c.append(_md(
        "> 🔍 **本例结果与行为预期相反/不显著**：低情绪 − 高情绪月均约 −0.7%，NW t≈−0.74；\n"
        "> 即高情绪组反而略强。样本小、区间短，不能据此否定行为异象，也不能当成交易信号。\n"
    ))
    c.append(_md(
        "## 2) 过度反应：短期输家 vs 短期赢家\n\n"
        "用上期收益排序，做多输家、做空赢家。\n"
        "**行为逻辑**：短期过度反应 → 输家反弹、赢家回落（短期反转）。"
    ))
    c.append(_code(
        "past1 = ret.shift(1)\n"
        "f_rev, port_rev, _ = long_short_factor(past1, ret, n_groups=10, high_minus_low=False)\n"
        "s_rev = factor_summary(f_rev)\n"
        "rho_rev = monotonicity_test(port_rev)['rho']\n"
        "print(f'短期输家 − 赢家: 月均 {f_rev.mean()*100:+.3f}%，年化 {s_rev[\"mean_ann\"]*100:+.2f}%，NW t={s_rev[\"t_stat\"]:.2f}')\n"
        "print(f'分组单调性 rho={rho_rev:.2f}')\n"
        "((1 + f_rev).cumprod()).plot(figsize=(10, 4), color='#F28C28', title='短期输家 − 赢家 累计净值')\n"
        "plt.axhline(1, color='gray', lw=.8, ls='--'); plt.ylabel('累计净值'); plt.tight_layout(); plt.show()"
    ))
    c.append(_code(
        "pd.DataFrame({'低情绪-高情绪': s_sent, '短期输家-赢家': s_rev}).T[\n"
        "    ['mean_ann', 'vol_ann', 'sharpe', 't_stat', 'max_drawdown', 'win_rate']\n"
        "].round(4)"
    ))
    c.append(_md(
        "## 3) 行为金融的四个来源\n\n"
        "| 来源 | 含义 | 例子 |\n"
        "|---|---|---|\n"
        "| 套利限制 | 错误定价难以被套利纠正 | 做空成本、流动性、噪声交易者风险 |\n"
        "| 预期偏差 | 对未来的判断有系统误差 | 过度自信、代表性、锚定 |\n"
        "| 风险偏好偏差 | 对风险的态度不一致 | 彩票偏好、损失厌恶、处置效应 |\n"
        "| 认知限制 | 注意力/信息处理有限 | 注意力效应、分类思维、框架效应 |\n\n"
        "> 行为异象要成立，通常需要“错误定价 + 套利限制”同时存在；否则套利者会把价格纠回来。"
    ))
    c.append(_md(
        "## ✋ 试一试\n\n"
        "1. 把情绪代理改成“只有换手率”，结果怎么变？\n"
        "2. 把上期收益换成过去 12 个月收益，情绪代理还是反转吗？\n"
        "3. 把多空方向反过来，t 值符号怎么变？\n\n"
        "## ✅ 本节小结\n\n"
        "- 情绪代理 = 换手率 + 近期收益；高情绪可能对应高估；\n"
        "- 短期反转可以看作过度反应的表现；\n"
        "- 行为异象需要“错误定价 + 套利限制”；\n"
        "- 真实样本小，结果不能直接外推。\n\n"
        "> 下一课：机器学习——强大但容易过拟合。"
    ))
    nb.cells = c
    return nb


def build_6_3() -> nbf.NotebookNode:
    """06.3 机器学习与过拟合。"""
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    c = []
    c.append(_md(
        "# 🎓 第6章 第3课：机器学习与过拟合\n\n"
        "**本节目标**：理解机器学习在因子研究中的力量与陷阱。\n\n"
        "1. 多项式阶数越高，训练误差越低，但测试误差可能变高（过拟合）；\n"
        "2. 线性模型 vs 随机森林：训练集表现好，不代表样本外好；\n"
        "3. 金融数据非平稳、小样本、低信噪比——ML 不是万能钥匙。\n\n"
        "对应原书第6章机器学习部分。"
    ))
    c.append(_code(CH6_SETUP))
    c.append(_md(
        "## 1) 过拟合：高阶多项式记住了噪声\n\n"
        "真实关系是“线性 + 正弦 + 噪声”。我们用不同阶数多项式拟合，\n"
        "比较**训练集 MSE** 和**测试集 MSE**。"
    ))
    c.append(_code(
        "mse = polynomial_train_test_mse(degrees=(1, 3, 5, 9, 15), n=200, noise=0.3, seed=42)\n"
        "mse.round(4)"
    ))
    c.append(_code(
        "fig, ax = plt.subplots(figsize=(8, 4))\n"
        "ax.plot(mse['degree'], mse['train_mse'], marker='o', label='训练 MSE')\n"
        "ax.plot(mse['degree'], mse['test_mse'], marker='s', label='测试 MSE')\n"
        "ax.set_xlabel('多项式阶数'); ax.set_ylabel('MSE')\n"
        "ax.set_title('阶数越高，训练误差越低——但测试误差不一定')\n"
        "ax.legend(); plt.tight_layout(); plt.show()"
    ))
    c.append(_md(
        "## 2) 线性回归 vs 随机森林\n\n"
        "同一组非线性数据：线性模型可能欠拟合，随机森林可能过拟合。\n"
        "关键看**测试集**，不是训练集。"
    ))
    c.append(_code(
        "from sklearn.model_selection import train_test_split\n"
        "from sklearn.linear_model import LinearRegression\n"
        "from sklearn.ensemble import RandomForestRegressor\n"
        "from sklearn.metrics import mean_squared_error\n\n"
        "rng = np.random.default_rng(42)\n"
        "n = 150\n"
        "x = np.linspace(-3, 3, n)\n"
        "y = 0.5 * x + 0.8 * np.sin(1.5 * x) + rng.normal(0, 0.3, n)\n"
        "X = x.reshape(-1, 1)\n"
        "Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=42)\n\n"
        "rows = []\n"
        "for name, model in [\n"
        "    ('线性回归', LinearRegression()),\n"
        "    ('随机森林', RandomForestRegressor(n_estimators=300, random_state=42)),\n"
        "]:\n"
        "    model.fit(Xtr, ytr)\n"
        "    rows.append({\n"
        "        '模型': name,\n"
        "        '训练 MSE': mean_squared_error(ytr, model.predict(Xtr)),\n"
        "        '测试 MSE': mean_squared_error(yte, model.predict(Xte)),\n"
        "    })\n"
        "pd.DataFrame(rows).set_index('模型').round(4)"
    ))
    c.append(_md(
        "## 3) 把 ML 用到因子收益预测：小样本 + 非平稳\n\n"
        "用滞后一期的因子收益预测下月 MKT。\n"
        "前 70% 训练、后 30% 测试——这是时间序列，不能随机打乱。\n"
        "看测试 R²：金融数据里常常很差，甚至为负。"
    ))
    c.append(_code(
        "factors = build_factor_returns(load_ashare_panel(), n_groups=10)\n"
        "features = ['SMB', 'HML', 'WML', 'RMW', 'CMA', 'TURN']\n"
        "data = factors[features].shift(1).join(factors['MKT']).dropna()\n"
        "X = data[features].to_numpy(); y = data['MKT'].to_numpy()\n"
        "split = int(len(data) * 0.7)\n"
        "Xtr, Xte, ytr, yte = X[:split], X[split:], y[:split], y[split:]\n\n"
        "rows = []\n"
        "for name, model in [\n"
        "    ('线性回归', LinearRegression()),\n"
        "    ('随机森林', RandomForestRegressor(n_estimators=300, random_state=42)),\n"
        "]:\n"
        "    model.fit(Xtr, ytr)\n"
        "    rows.append({\n"
        "        '模型': name,\n"
        "        '训练 R²': model.score(Xtr, ytr),\n"
        "        '测试 R²': model.score(Xte, yte),\n"
        "    })\n"
        "pd.DataFrame(rows).set_index('模型').round(4)"
    ))
    c.append(_md(
        "> 🔍 **本例测试 R² 为负**：说明模型在样本外连“均值预测”都不如。\n"
        "> 金融时间序列信噪比低、非平稳，ML 很容易在训练集上表现很好、样本外失效。\n"
    ))
    c.append(_md(
        "## 4) ML 在因子研究中的问题\n\n"
        "| 问题 | 说明 | 对策 |\n"
        "|---|---|---|\n"
        "| 过拟合 | 模型记住噪声，样本外失效 | 训练/验证/测试、正则化、简化模型 |\n"
        "| 非平稳 | 市场结构变化，历史关系失效 | 滚动/扩展窗口、样本外检验 |\n"
        "| 低信噪比 | 金融收益噪声大，信号弱 | 经济逻辑、因子筛选、集成 |\n"
        "| 可解释性 | 黑箱难解释 | 线性/树模型、特征重要性、SHAP |\n"
        "| 数据窥探 | 试了很多模型/参数 | 预注册、多重检验校正、样本外 |\n\n"
        "> 机器学习是工具，不是魔法。**先有经济逻辑，再做样本外验证。**"
    ))
    c.append(_md(
        "## ✋ 试一试\n\n"
        "1. 把多项式阶数加到 30，训练 MSE 和测试 MSE 怎么变？\n"
        "2. 把随机森林的 `n_estimators` 改成 10，结果稳定吗？\n"
        "3. 把时间序列切分从 70/30 改成 50/50，测试 R² 怎么变？\n\n"
        "## ✅ 本节小结\n\n"
        "- 高阶模型/复杂模型在训练集上更好，不代表样本外更好；\n"
        "- 金融数据小样本、低信噪比、非平稳，ML 很容易过拟合；\n"
        "- 要用训练/验证/测试、滚动窗口、正则化和经济逻辑；\n"
        "- 不要用随机打乱的时间序列切分。\n\n"
        "> 下一章：因子投资实践——组合优化、Smart Beta、归因。"
    ))
    nb.cells = c
    return nb


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    notebooks = {
        "06.1-p-hacking-and-factor-zoo": build_6_1(),
        "06.2-behavioral-finance": build_6_2(),
        "06.3-machine-learning-and-overfitting": build_6_3(),
    }
    for name, nb in notebooks.items():
        path = OUT / f"{name}.ipynb"
        nbf.write(nb, str(path))
        print(f"built {path}")


if __name__ == "__main__":
    main()
