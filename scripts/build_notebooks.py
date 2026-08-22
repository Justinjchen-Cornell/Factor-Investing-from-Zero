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
    cells.append(nbf.v4.new_code_cell(
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
    nb.cells = cells
    return nb


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
        "# 特质噪声：形状 (T, 4) 生成后转置为 (4, T)，与 alpha/beta@lam_t.T 对齐\n"
        "idio = rng.normal(0, teach['idio_risk'].to_numpy(), size=(T, 4)).T\n"
        "ret = alpha.reshape(-1, 1) + beta @ lam_t.T + idio  # 个股收益时序（式 1.5 的数值版）\n"
        "print('个股收益的样本协方差 Σ:')\n"
        "print(np.cov(ret).round(5))"
    ))
    nb.cells.append(nbf.v4.new_code_cell(
        "# 用因子重建协方差：Σ_hat = βΣλβ' + Σε\n"
        "sigma_eps = np.diag(teach['idio_risk'].to_numpy() ** 2)\n"
        "sigma_hat = beta @ cov_lam @ beta.T + sigma_eps\n"
        "sigma_true = np.cov(ret)\n"
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
    build_01_1_time_cells(nb)
    path = ROOT / "chapters" / "01-factor-basics" / "notebooks" / "01.1-unified-view.ipynb"
    path.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(nb, str(path))
    print(f"built {path}")


if __name__ == "__main__":
    main()
