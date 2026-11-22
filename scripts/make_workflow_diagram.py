"""生成《困境资产中的因子思维》工作流图（PNG + SVG）。"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

OUT = Path(__file__).resolve().parents[1] / "articles" / "assets"
OUT.mkdir(parents=True, exist_ok=True)

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "Noto Sans CJK SC", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

CREAM = "#FFF8EC"
INK = "#3E2C23"
MUTED = "#7A6A5F"
ORANGE = "#F28C28"
GREEN = "#5B8C5A"
BLUE = "#5B7FA6"
RED = "#D95D39"
PURPLE = "#7B6AA8"
LINE = "#EADCC8"

boxes = [
    {
        "x": 0.50, "y": 6.35, "n": "1", "color": "#FDE3C4", "accent": ORANGE,
        "title": "定义 Universe 与收益/风险",
        "bullets": ["区域 · 资产类型 · 法律状态 · 进入年份",
                    "IRR / 回收率 / 现金流 / 退出 multiple",
                    "先写：什么证据能证明我错了"],
    },
    {
        "x": 5.90, "y": 6.35, "n": "2", "color": "#DCE9F7", "accent": BLUE,
        "title": "数据与样本",
        "bullets": ["Point-in-time：不用未来信息",
                    "完整样本：成功 / 失败 / 未投 / 仍持有",
                    "记录来源、口径与关键假设"],
    },
    {
        "x": 11.30, "y": 6.35, "n": "3", "color": "#DDEBD8", "accent": GREEN,
        "title": "特征 / 因子",
        "bullets": ["折扣率 · LTV · 资产质量",
                    "法律复杂度 · 区域流动性",
                    "周期位置 · 资金久期 · 重组难度"],
    },
    {
        "x": 11.30, "y": 3.25, "n": "4", "color": "#F8D7CC", "accent": RED,
        "title": "排序 / 分组 / 回归",
        "bullets": ["排序法：先排队，再分组比较",
                    "时序 / 截面 / FM：β、λ、α",
                    "NW · GRS · 正交化：别被显著骗了"],
    },
    {
        "x": 5.90, "y": 3.25, "n": "5", "color": "#F9E7B6", "accent": "#C99A1E",
        "title": "稳健性与多重检验",
        "bullets": ["换样本 · 换区间 · 换口径",
                    "提高 t 门槛，做样本外检验",
                    "扣掉交易 / 法律 / 时间成本"],
    },
    {
        "x": 0.50, "y": 3.25, "n": "6", "color": "#E8E1F5", "accent": PURPLE,
        "title": "组合 / 归因 / 复盘",
        "bullets": ["风险模型：真分散还是假分散？",
                    "约束：集中度 / 久期 / 流动性",
                    "归因：赚的是 β 还是 α？复盘更新假设"],
    },
]

W, H = 4.20, 2.10

fig, ax = plt.subplots(figsize=(16, 10), dpi=200)
fig.patch.set_facecolor(CREAM)
ax.set_facecolor(CREAM)
ax.set_xlim(0, 16)
ax.set_ylim(0, 10)
ax.axis("off")


def rounded_box(b):
    patch = FancyBboxPatch(
        (b["x"], b["y"]), W, H,
        boxstyle="round,pad=0.02,rounding_size=0.18",
        linewidth=2.2, edgecolor=b["accent"], facecolor=b["color"],
        zorder=2,
    )
    ax.add_patch(patch)
    # number circle
    ax.add_patch(Circle((b["x"] + 0.38, b["y"] + H - 0.38), 0.23,
                        facecolor=b["accent"], edgecolor="white", linewidth=2, zorder=3))
    ax.text(b["x"] + 0.38, b["y"] + H - 0.38, b["n"], ha="center", va="center",
            fontsize=15, color="white", fontweight="bold", zorder=4)
    ax.text(b["x"] + 0.78, b["y"] + H - 0.38, b["title"], ha="left", va="center",
            fontsize=16.5, color=INK, fontweight="bold", zorder=4)
    for i, line in enumerate(b["bullets"]):
        ax.text(b["x"] + 0.30, b["y"] + H - 0.92 - i * 0.42, "• " + line,
                ha="left", va="center", fontsize=12.2, color=MUTED, zorder=4)


for b in boxes:
    rounded_box(b)

# arrows
arrow_kw = dict(arrowstyle="-|>", mutation_scale=22, linewidth=2.0,
                color="#8C7A6B", shrinkA=0, shrinkB=0)
ax.add_patch(FancyArrowPatch((4.72, 7.40), (5.88, 7.40), **arrow_kw))
ax.add_patch(FancyArrowPatch((10.12, 7.40), (11.28, 7.40), **arrow_kw))
ax.add_patch(FancyArrowPatch((13.40, 6.33), (13.40, 5.38), **arrow_kw))
ax.add_patch(FancyArrowPatch((11.28, 4.30), (10.12, 4.30), **arrow_kw))
ax.add_patch(FancyArrowPatch((5.88, 4.30), (4.72, 4.30), **arrow_kw))

# feedback loop: box 6 -> box 1
feedback = FancyArrowPatch(
    (2.60, 3.23), (0.18, 2.55), connectionstyle="arc3,rad=0.0",
    arrowstyle="-|>", mutation_scale=20, linewidth=1.8,
    color=ORANGE, linestyle=(0, (6, 4)), zorder=1,
)
# custom path via polyline: use annotate-like path
from matplotlib.path import Path as MPath
from matplotlib.patches import PathPatch

path = MPath(
    [(2.60, 3.23), (2.60, 2.35), (0.18, 2.35), (0.18, 7.40), (0.50, 7.40)],
    [MPath.MOVETO, MPath.LINETO, MPath.LINETO, MPath.LINETO, MPath.LINETO],
)
ax.add_patch(PathPatch(path, fill=False, edgecolor=ORANGE, linewidth=1.8,
                       linestyle=(0, (6, 4)), zorder=1))
ax.add_patch(FancyArrowPatch((0.18, 7.40), (0.48, 7.40), arrowstyle="-|>",
                             mutation_scale=18, linewidth=1.8, color=ORANGE, zorder=1))
ax.text(1.35, 2.12, "复盘：更新假设", fontsize=12, color=ORANGE, fontweight="bold")

# title
ax.text(0.50, 9.35, "困境资产中的因子思维", fontsize=34, color=INK, fontweight="bold")
ax.text(0.50, 8.95, "从“故事”到“可检验的证据”｜一套可复现的研究工作流",
        fontsize=16, color=MUTED)
ax.text(12.55, 9.35, "反叙事纪律", fontsize=14, color=ORANGE, fontweight="bold", ha="right")
ax.text(15.45, 9.35, "可检验 · 可复现 · 可归因", fontsize=13, color=GREEN,
        fontweight="bold", ha="right")

# bottom banner
banner = FancyBboxPatch((0.50, 0.55), 15.00, 0.85,
                        boxstyle="round,pad=0.02,rounding_size=0.15",
                        linewidth=1.5, edgecolor=LINE, facecolor="#FFFFFF", zorder=2)
ax.add_patch(banner)
ax.text(8.00, 0.97,
        "收益 = βλ + α ｜ 先分清共同原因，再谈个体能力 ｜ 先看样本外，再信样本内 ｜ 先做归因，再谈成功",
        ha="center", va="center", fontsize=13.2, color=INK, fontweight="bold")

png = OUT / "distressed-factor-workflow.png"
svg = OUT / "distressed-factor-workflow.svg"
plt.tight_layout()
fig.savefig(png, dpi=200, facecolor=CREAM, bbox_inches="tight", pad_inches=0.2)
fig.savefig(svg, facecolor=CREAM, bbox_inches="tight", pad_inches=0.2)
print("saved", png)
print("saved", svg)
