"""构建课程教学 notebooks（用 nbformat 生成 .ipynb，保证可复现）。

设计理念：每个 notebook = 手把手教学（讲解 cell + 案例代码 cell + 试一试 cell）。
用法：python scripts/build_notebooks.py   # 构建全部
"""
from __future__ import annotations

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]

CH1_SETUP = (
    "import numpy as np\nimport pandas as pd\nimport matplotlib.pyplot as plt\n\n"
    "from pathlib import Path\n"
    "def _find_sample():\n"
    "    for p in [Path('data/sample'), Path.cwd().parents[2] / 'data' / 'sample']:\n"
    "        if p.exists():\n"
    "            return p\n"
    "    raise FileNotFoundError('找不到 data/sample，请从仓库根目录启动 notebook')\n"
    "SAMPLE = _find_sample()\n"
    "plt.rcParams['figure.dpi'] = 110\n"
    "print('✅ 环境就绪，开始学习！')"
)


def build_01_1() -> nbf.NotebookNode:
    """01.1 一个公式：E[R] = βλ + α（世界观课）"""
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    c = []
    c.append(nbf.v4.new_markdown_cell(
        "# 🎓 第1课：一个公式看懂因子投资\n\n"
        "**本节目标**：学完你能用一个公式（E[R] = βλ + α）说清楚因子投资的全部世界观。\n\n"
        "**怎么用本 notebook（三步法）**：\n"
        "1. 读 🍚 讲解 cell（白话+比喻）；\n"
        "2. 运行 🐍 代码 cell（看真实数字）；\n"
        "3. 完成 ✋ 试一试 cell（改参数，观察变化）。\n\n"
        "> 对应原书：第1章 1.1 节"
    ))
    c.append(nbf.v4.new_code_cell(CH1_SETUP))
    c.append(nbf.v4.new_markdown_cell(
        "## 开场：三个生活问题 🤔\n\n"
        "1. 为什么有些股票长期涨得比别的多？（白酒 vs 银行）\n"
        "2. 为什么大盘一跌，几乎所有股票一起跌？（明明是不同的公司！）\n"
        "3. 凭什么有人坚信「买便宜股」能赚钱？\n\n"
        "**因子投资，就是回答这三个问题的学问。**"
    ))
    c.append(nbf.v4.new_markdown_cell(
        "## ① 因子 = 食物的「营养成分」 🍚\n\n"
        "米饭、肉、菜形态各不相同，但身体真正需要的是背后的**碳水、蛋白质、脂肪**——\n"
        "这些营养成分就是食物的「因子」。\n\n"
        "股票也一样：茅台、宁德、招行公司各不相同，但收益被共同的**系统性风险**驱动\n"
        "（市场行情、市值大小、便宜还是贵）——这些共同的风险来源，就是股票的**因子**。\n\n"
        "**定义（背下来）**：因子 = 众多资产共同暴露的系统性风险，是收益背后的驱动力；\n"
        "因子收益率 = 这种风险的风险溢价（共性收益）。\n\n"
        "**两个必要条件**：\n"
        "- ✅ 驱动大家一起动（与协方差矩阵有关）；\n"
        "- ✅ 长期有正收益（被定价）。\n\n"
        "> 💡 判断口诀：**它是很多股票收益的共同原因吗？长期持有它能赚钱吗？** 两个都「是」才是因子。"
    ))
    c.append(nbf.v4.new_markdown_cell(
        "## ② 案例1：什么是「因子暴露 β」？📏\n\n"
        "β = 你对这种风险的**敞口**。先看代码：模拟市场收益，造两支股票——\n"
        "股票A 对市场很敏感（β=1.2），股票B 不敏感（β=0.3）。"
    ))
    c.append(nbf.v4.new_code_cell(
        "rng = np.random.default_rng(42)\n"
        "T = 120\n"
        "market = rng.normal(0.005, 0.04, T)          # 市场因子收益\n"
        "stockA = 1.2 * market + rng.normal(0, 0.01, T)  # β=1.2\n"
        "stockB = 0.3 * market + rng.normal(0, 0.01, T)  # β=0.3\n\n"
        "# 用回归估计 β（斜率）\n"
        "betaA = np.polyfit(market, stockA, 1)[0]\n"
        "betaB = np.polyfit(market, stockB, 1)[0]\n"
        "print(f'股票A 的 β 估计 = {betaA:.2f}（预设1.2）')\n"
        "print(f'股票B 的 β 估计 = {betaB:.2f}（预设0.3）')\n\n"
        "plt.figure(figsize=(6, 4))\n"
        "plt.scatter(market, stockA, s=8, alpha=0.6, label='股票A (β=1.2)')\n"
        "plt.scatter(market, stockB, s=8, alpha=0.6, label='股票B (β=0.3)')\n"
        "plt.xlabel('市场收益'); plt.ylabel('个股收益')\n"
        "plt.title('β = 斜率：市场涨1%，个股平均跟涨多少')\n"
        "plt.legend(); plt.tight_layout(); plt.show()"
    ))
    c.append(nbf.v4.new_markdown_cell(
        "## ③ 一个公式：E[R] = βλ + α 🧮\n\n"
        "收益不是猜的，是算出来的：\n\n"
        "$$E[R_i] = \\beta_i \\lambda + \\alpha_i$$\n\n"
        "| 成分 | 白话 | 例子 |\n"
        "|---|---|---|\n"
        "| β 因子暴露 | 你对这种风险敞开多少 | 茅台 β=1.2，银行 β=0.6 |\n"
        "| λ 因子溢价 | 这种风险值多少钱（月均） | 市场 λ=0.5%/月，便宜因子 λ=0.8%/月 |\n"
        "| α 定价误差 | 模型算不出的额外收益 | 有的股票 α=0.3%/月 |\n\n"
        "λ 是**因子**（市场付钱的原因），βλ 是**多因子模型**（配餐表），α 是**异象**（付错的钱）。"
    ))
    c.append(nbf.v4.new_code_cell(
        "# 案例2：用教学小样本算预期收益（4 支股票 × 2 个因子）\n"
        "teach = pd.read_csv(SAMPLE / 'teaching_sample.csv')\n"
        "lam = np.array([0.008, 0.004])  # 因子溢价：A=0.8%/月, B=0.4%/月\n"
        "beta = teach[['factor_a_exposure', 'factor_b_exposure']].to_numpy()\n"
        "er_model = beta @ lam  # 矩阵乘法：暴露 × 溢价\n"
        "pd.DataFrame({'资产': teach['asset'], 'β_A': beta[:, 0], 'β_B': beta[:, 1],\n"
        "             'E[R]模型(月)': er_model}).round(4)"
    ))
    nb.cells = c
    return nb


def build_01_1_tail(nb) -> None:
    c = nb.cells
    c.append(nbf.v4.new_markdown_cell(
        "## ④ 案例3：人造一个「异象」 ⭐\n\n"
        "给 stock_2 注入 1.2%/月的真实 α——它就成了模型解释不了的「异象」。\n"
        "画出来看：**点到模型直线的垂直距离 = α**。"
    ))
    c.append(nbf.v4.new_code_cell(
        "alpha = np.array([0.0, 0.012, 0.0, 0.0])   # 只有 stock_2 有 α\n"
        "er_actual = er_model + alpha\n"
        "fig, ax = plt.subplots(figsize=(7, 5))\n"
        "xs = np.linspace(0.6, 1.3, 10)\n"
        "ax.plot(xs, xs * lam[0], 'k--', label='模型直线 E[R] = β·λ')\n"
        "for i, row in teach.iterrows():\n"
        "    b = beta[i, 0]\n"
        "    is_anom = alpha[i] != 0\n"
        "    ax.scatter(b, er_actual[i], s=120, marker='^' if is_anom else 'o',\n"
        "               label=f\"{row['asset']}\" + ('（异象⭐）' if is_anom else ''))\n"
        "    if is_anom:\n"
        "        ax.vlines(b, er_model[i], er_actual[i], color='red', linewidth=2)\n"
        "        ax.annotate('α = 1.2%/月', xy=(b, er_model[i]),\n"
        "                    xytext=(b + 0.02, er_model[i] + 0.001), color='red')\n"
        "ax.set_xlabel('因子 A 暴露 β_A'); ax.set_ylabel('预期收益 E[R]（月均）')\n"
        "ax.set_title('统一视角：E[R] = βλ + α')\n"
        "ax.legend(fontsize=8); plt.tight_layout(); plt.show()"
    ))
    c.append(nbf.v4.new_markdown_cell(
        "## ⑤ 截面 vs 时序 + 降维魔法 🧙\n\n"
        "- **截面** 🏙️：为什么北京比鹤岗贵？（不同资产的收益差异）\n"
        "- **时序** 📅：北京今年比去年涨了多少？（同一资产随时间的变化）\n\n"
        "时序角度的核心产出——**方差模型**（式1.6）：\n\n"
        "$$\\Sigma = \\beta \\Sigma_\\lambda \\beta' + \\Sigma_\\varepsilon$$\n\n"
        "**这就是降维魔法**：3000 支股票的协方差是 3000×3000 的矩阵（450万个数字！），\n"
        "用 10 个因子就缩成 10×10。下面亲手验证。"
    ))
    c.append(nbf.v4.new_code_cell(
        "# 案例4：模拟 120 个月，验证协方差分解 Σ = βΣλβ' + Σε\n"
        "rng = np.random.default_rng(42)\n"
        "T = 120\n"
        "cov_lam = np.array([[0.0009, 0.0001], [0.0001, 0.0004]])  # 因子协方差\n"
        "lam_t = rng.multivariate_normal(lam, cov_lam, size=T)     # 因子收益时序\n"
        "idio = rng.normal(0, teach['idio_risk'].to_numpy(), size=(T, 4)).T\n"
        "ret = alpha.reshape(-1, 1) + beta @ lam_t.T + idio        # 个股收益（式1.5）\n\n"
        "# 用因子重建协方差 vs 直接算样本协方差\n"
        "sigma_eps = np.diag(teach['idio_risk'].to_numpy() ** 2)\n"
        "sigma_hat = beta @ cov_lam @ beta.T + sigma_eps\n"
        "sigma_true = np.cov(ret)\n"
        "err = np.abs(sigma_hat - sigma_true).max()\n"
        "print(f'重建协方差 vs 真实协方差的最大误差: {err:.5f}')\n"
        "print('=> Σ = βΣλβ′ + Σε 成立，这就是「因子=降维」的数学依据')"
    ))
    c.append(nbf.v4.new_markdown_cell(
        "## ✋ 试一试（动手任务）\n\n"
        "1. 把上面 `alpha` 数组全部改成 0 重跑案例3——红色竖线发生了什么？为什么？\n"
        "2. 在案例2里给 teach 加一行「新股票」（β=[1.0, 0.6]），算它的 E[R]。\n"
        "3. 把 `cov_lam` 的非对角元改成 0.0005 重跑案例4——误差变大还是变小？为什么？\n\n"
        "## ✅ 本节小结\n\n"
        "- 预期收益 = 暴露 × 溢价 + 定价误差（**E[R] = βλ + α**）；\n"
        "- **α ≠ 0** 的资产 = 异象（模型解释不了的部分）；\n"
        "- 协方差分解 Σ = βΣλβ′ + Σε 是**降维**的数学依据（Barra 的应用基础）。\n\n"
        "> 下一课：学术起源——三位诺奖大师和「因子动物园」。"
    ))


def build_01_2() -> nbf.NotebookNode:
    """01.2 学术起源：三位诺奖 + 因子动物园（含数据窥探模拟）"""
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    c = []
    c.append(nbf.v4.new_markdown_cell(
        "# 🎓 第2课：学术起源 —— 三位诺奖与「因子动物园」\n\n"
        "**本节目标**：了解因子研究从哪来、现在有多乱（重要！），并亲手模拟「数据窥探」如何造假因子。\n\n"
        "> 对应原书：第1章 1.2 节"
    ))
    c.append(nbf.v4.new_code_cell(CH1_SETUP))
    c.append(nbf.v4.new_markdown_cell(
        "## ① 时间线（故事版）📜\n\n"
        "- **1934** Graham & Dodd《证券分析》——「便宜股」思想的源头；\n"
        "- **1960s** CAPM 问世——第一次用公式刻画风险-收益；\n"
        "- **1976** APT（Ross）——从 1 个因子推广到多个；\n"
        "- **1977/1981** 便宜股效应、小市值效应被发现——CAPM **解释不了**它们（异象！）；\n"
        "- **1993** Fama-French 三因子模型——把两个异象「收编」成 SMB 和 HML 因子。\n\n"
        "**规律**：异象倒逼模型升级 → 模型把异象收编成因子 → 新异象出现 → ……"
    ))
    c.append(nbf.v4.new_markdown_cell(
        "## ② 三位诺奖大师 🏆（2013 年共享诺奖）\n\n"
        "- **Fama（有效市场之父）**：① 联合假说（1970）——**想检验市场有没有效，先得有把对的尺子（定价模型）**；\n"
        "  ② Fama-MacBeth 回归（1973）——检验模型的统计工具；③ FF 三因子模型（1993）。\n"
        "- **Hansen**：发明 GMM（1982）——检验模型的「万能账本」（第2章详讲）。\n"
        "- **Shiller（行为金融）**：噪音交易者模型（1984）——价格涨过头跌过头，因为人非理性。\n\n"
        "> 🧠 注意 Fama 和 Shiller 立场相反：Fama 认为市场有效，Shiller 认为市场常犯错——\n"
        "> **因子投资就诞生在这两种立场的拉扯中**：有效市场需要因子（风险补偿），\n"
        "> 行为金融需要异象（错误定价）。"
    ))
    c.append(nbf.v4.new_markdown_cell(
        "## ③ 案例1：「数据窥探」模拟 —— 随机数里挖假因子 🎲\n\n"
        "数据窥探 = **先看数据、再编故事**（先射箭、再画靶）。\n"
        "模拟一下：生成 **1000 个纯随机噪声序列**（市场里根本不存在任何因子），\n"
        "然后用「|t|>2 就算显著」的标准去挖——能挖出多少个「显著因子」？"
    ))
    c.append(nbf.v4.new_code_cell(
        "rng = np.random.default_rng(2020)\n"
        "n_trials, T = 1000, 120\n"
        "trials = rng.normal(0, 0.02, size=(n_trials, T))   # 纯噪声！\n"
        "ts = trials.mean(axis=1) / (trials.std(axis=1) / np.sqrt(T))\n"
        "sig = np.abs(ts) > 2\n"
        "print(f'纯噪声序列中，|t|>2 的「显著因子」: {sig.sum()} 个 / {n_trials} ({sig.mean()*100:.1f}%)')\n\n"
        "plt.figure(figsize=(6, 4))\n"
        "plt.hist(ts, bins=50, alpha=0.7)\n"
        "plt.axvline(2, color='red', ls='--', label='t=2 阈值')\n"
        "plt.axvline(-2, color='red', ls='--')\n"
        "plt.xlabel('t 值'); plt.ylabel('数量'); plt.title('1000 个噪声序列的 t 值分布')\n"
        "plt.legend(); plt.tight_layout(); plt.show()"
    ))
    c.append(nbf.v4.new_markdown_cell(
        "## ④ 「因子动物园」警告 ⚠️（记住三个数字）\n\n"
        "| 事实 | 出处 |\n"
        "|---|---|\n"
        "| 学术界已挖出 **400+** 个因子，多数是数据窥探的产物 | Cochrane (2011) |\n"
        "| 显著性门槛从 t=2.0 抬到 **3.0** | Harvey et al. (2016) |\n"
        "| 再抬到 **3.4**；因子发表后收益平均**衰减 50%+** | Chordia (2020)、McLean & Pontiff (2016) |\n\n"
        "> 🍜 衰减 = **网红店红了就排队，利润被摊薄**：越多人知道的因子越不赚钱。"
    ))
    c.append(nbf.v4.new_markdown_cell(
        "## ⑤ 案例2：「发表后衰减」模拟 📉\n\n"
        "研究者会挑「表现最好的区间」发表（另一种数据窥探）——模拟这个过程看衰减多少："
    ))
    c.append(nbf.v4.new_code_cell(
        "rng = np.random.default_rng(7)\n"
        "T = 240\n"
        "true_premium = 0.004  # 真实月均溢价 0.4%\n"
        "ret = rng.normal(true_premium, 0.03, size=T)\n\n"
        "# 「发表前」：挑 60 个月里表现最好的区间（数据窥探）\n"
        "best = max(range(0, T - 60), key=lambda s: ret[s:s+60].mean())\n"
        "in_sample = ret[best:best+60].mean()\n"
        "# 「发表后」：全部 240 个月的真相\n"
        "out_sample = ret.mean()\n"
        "print(f'发表前（挑最优区间）月均: {in_sample*100:.2f}%')\n"
        "print(f'发表后（长期真相）月均:   {out_sample*100:.2f}%')\n"
        "print(f'衰减幅度: {100*(1 - out_sample/in_sample):.0f}%（真实世界中 McLean-Pontiff 测得 ~50%+）')"
    ))
    c.append(nbf.v4.new_markdown_cell(
        "## ✋ 试一试\n\n"
        "1. 把案例1的阈值改成 t=3.0 重跑——「显著因子」从 5% 降到多少？这就是 Harvey 抬高门槛的意义。\n"
        "2. 案例2里把 `best` 窗口从 60 个月改成 12 个月——衰减更严重还是更轻？为什么？\n\n"
        "## ✅ 小结\n\n"
        "- 因子研究=异象倒逼模型升级的循环；Fama/Hansen/Shiller 三人奠定了全部工具；\n"
        "- **数据窥探**让 400+ 因子大半不可信——读论文先问：**这个因子在样本外还活着吗？**\n\n"
        "> 下一课：业界全景——管理人怎么用因子、投资者怎么买因子。"
    ))
    nb.cells = c
    return nb


def build_01_3() -> nbf.NotebookNode:
    """01.3 业界发展：管理人 5 件事 + 选 ETF 之难（含两个模拟案例）"""
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    c = []
    c.append(nbf.v4.new_markdown_cell(
        "# 🎓 第3课：业界全景 —— 管理人怎么用因子？投资者怎么买因子？\n\n"
        "**本节目标**：了解因子在真实世界怎么被使用，并亲手模拟「80% 收益来自 β」和「选 ETF 之难」。\n\n"
        "> 对应原书：第1章 1.3 节"
    ))
    c.append(nbf.v4.new_code_cell(CH1_SETUP))
    c.append(nbf.v4.new_markdown_cell(
        "## ① 管理人视角：5 件事 📋\n\n"
        "| # | 关键词 | 白话 |\n"
        "|---|---|---|\n"
        "| 1 | 收益预测 vs 风险管理 | 因子既能选股（截面），也能算协方差控风险（时序） |\n"
        "| 2 | 因子拥挤 | 用的人越多越不赚钱，出事时互相踩踏（2007年8月量化危机） |\n"
        "| 3 | 因子择时 | 因子时灵时不灵，能躲开吗？（RA 按估值 vs AQR 按动量） |\n"
        "| 4 | α vs β 收益 | 管理人赚的钱里 ~80% 来自 β（因子暴露），只有 20% 是真 α |\n"
        "| 5 | 创新 | 另类数据（舆情/专利/新闻）+ 机器学习 = 新收益源 |\n\n"
        "> 🛗 **电梯类比**：管理人收益像在电梯里做俯卧撑——电梯上行（β）贡献 80% 高度，俯卧撑（α）只占 20%。"
    ))
    c.append(nbf.v4.new_markdown_cell(
        "## ② 案例1：「电梯类比」模拟 —— 谁才是顶尖管理人？🛗\n\n"
        "模拟 100 个管理人：收益 = 80% 来自 β×市场 + 20% 来自 α 能力 + 运气。\n"
        "看看「业绩最好的 10 个」是靠电梯（β）还是靠俯卧撑（α）？"
    ))
    c.append(nbf.v4.new_code_cell(
        "rng = np.random.default_rng(5)\n"
        "n = 100\n"
        "beta = rng.uniform(0.8, 1.5, n)          # 电梯速度（因子暴露）\n"
        "alpha = rng.normal(0, 0.001, n)          # 俯卧撑能力（真 α）\n"
        "mkt = rng.normal(0.006, 0.04, 120)       # 市场收益\n"
        "ret = 0.8 * beta[:, None] * mkt[None, :] + 0.2 * alpha[:, None] * 12 + rng.normal(0, 0.01, (n, 120))\n"
        "ann = ret.mean(axis=1) * 12              # 年化收益\n\n"
        "top = np.argsort(-ann)[:10]\n"
        "pd.DataFrame({'年化收益%': (ann[top]*100).round(2),\n"
        "             'β暴露(电梯)': beta[top].round(2),\n"
        "             'α能力(俯卧撑)%': (alpha[top]*100).round(2)}).reset_index(drop=True)"
    ))
    c.append(nbf.v4.new_code_cell(
        "print('看懂了没？顶尖管理人几乎都是「电梯快」（β 高）的，而不是「俯卧撑强」（α 高）的！')\n"
        "print('→ 评价基金先问：它的收益是选对了风格（β），还是真有选股能力（α）？')"
    ))
    c.append(nbf.v4.new_markdown_cell(
        "## ③ 投资者视角：从风格指数到 Smart Beta 🧺\n\n"
        "- **1987** Russell 推出最早风格指数（价值/成长）；\n"
        "- **1992** 先锋推出价值指数基金——主动投资的低成本替代；\n"
        "- 今天 **Smart Beta ETF 规模超 6500 亿美元**（2018年估算）——普通投资者「一键买入因子」。\n\n"
        "⚠️ 但选 ETF 极难！Choi et al. (2009) 实验：连金融专业学生都被历史收益迷惑，忽视费率。\n"
        "下面复刻这个实验。"
    ))
    c.append(nbf.v4.new_markdown_cell(
        "## ④ 案例2：复刻「选 ETF 实验」 🎯\n\n"
        "5 个 ETF 追踪**同一个价值因子**，毛收益完全相同，只有**费率**不同（0.05%~0.50%）。\n"
        "加上随机扰动模拟「历史表现差异」——你会选哪个？"
    ))
    c.append(nbf.v4.new_code_cell(
        "rng = np.random.default_rng(1)\n"
        "fees = [0.05, 0.10, 0.20, 0.35, 0.50]           # 年费率 %\n"
        "factor_ret = rng.normal(0.006, 0.03, size=60)    # 价值因子月收益\n"
        "noise = rng.normal(0, 0.002, size=(60, 5))       # 干扰：历史表现随机波动\n\n"
        "# 「迷惑版」：毛收益 + 随机扰动（像真实市场一样让人看走眼）\n"
        "gross = pd.DataFrame({f'ETF_{i+1}(费率{fee}%)': factor_ret - fee/100/12 + noise[:, i]\n"
        "                      for i, fee in enumerate(fees)})\n"
        "print('近5年累计收益（你会选哪个？）：')\n"
        "print(((1+gross).prod()-1).round(3).sort_values(ascending=False))"
    ))
    c.append(nbf.v4.new_code_cell(
        "# 揭晓：扣掉费率后的真实收益——唯一标准是费率！\n"
        "clean = pd.DataFrame({f'ETF_{i+1}(费率{fee}%)': factor_ret - fee/100/12 for i, fee in enumerate(fees)})\n"
        "net = (1+clean).prod()-1\n"
        "print('扣费后真实累计收益：')\n"
        "print(net.round(3).sort_values(ascending=False))\n"
        "best = net.idxmax()\n"
        "print(f'\\n🏆 赢家是 {best} —— 费率最低的才是对的！')"
    ))
    c.append(nbf.v4.new_markdown_cell(
        "## ✋ 试一试\n\n"
        "1. 案例1中把 `0.8` 和 `0.2` 换成 `0.2` 和 `0.8` 重跑——顶尖管理人还看得到「电梯」吗？\n"
        "2. 案例2把 `fees` 改成 [0.5, 0.5, 0.5, 0.5, 0.5] 重跑——结果变成什么？说明什么？\n\n"
        "## ✅ 小结\n\n"
        "- 管理人：**80% 收益来自 β**（选对风格），因子拥挤是最大风险；\n"
        "- 投资者：Smart Beta 让普通人也能买因子，但**同类 ETF 之间只看费率**；\n"
        "- 第1章完结！你已经有了完整的「因子世界观」。\n\n"
        "> 下一章（第2章）：方法论——排序法、回归、Newey-West……把「感觉」变成「检验」。"
    ))
    nb.cells = c
    return nb


def main() -> None:
    nb1 = build_01_1()
    build_01_1_tail(nb1)
    notebooks = {
        "01.1-unified-formula": nb1,
        "01.2-academic-origins": build_01_2(),
        "01.3-industry-practice": build_01_3(),
    }
    chapter = ROOT / "chapters" / "01-factor-basics" / "notebooks"
    # 清理旧版 notebook（已拆分为三个教学 notebook）
    for old in chapter.glob("01.1-unified-view.ipynb"):
        old.unlink()
    for name, nb in notebooks.items():
        path = chapter / f"{name}.ipynb"
        nbf.write(nb, str(path))
        print(f"built {path}")

    # 第2章 notebook 由独立构建脚本生成（保持章节独立、便于维护）
    from build_ch2_notebooks import main as build_ch2
    build_ch2()


if __name__ == "__main__":
    main()
