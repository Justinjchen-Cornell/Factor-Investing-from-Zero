# Factor-Investing-from-Zero · 从零开始学因子

> 一本把《因子投资：方法与实践》讲成"开源课程"的仓库 —— 每一章都有讲义、可运行的代码和练习。
> *An open course built from "Factor Investing: Methods and Practice" — lecture + code + exercises for every chapter.*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Chapters](https://img.shields.io/badge/Chapters-7-green)
![Data](https://img.shields.io/badge/Data-A%E8%82%A1%20sample%20offline--ready-brightgreen)

---

## TL;DR / 一句话

**因子是资产收益率的"营养成分"：一只股票 = 一组因子暴露 × 因子溢价 + 独有的定价误差。**
**A stock is a basket of factor exposures: E[R] = βλ + α.**

本仓库用"比喻式精讲 + 可运行代码 + 检查站练习"三件套，带你从零认识因子、学会方法、读懂 A 股实证、最终上手实践。

---

## 章节导航 / 学习路径 · Learning Path

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
