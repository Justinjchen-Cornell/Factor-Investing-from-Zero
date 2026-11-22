# Factor-Investing-from-Zero · 从零开始学因子

> 一本把《因子投资：方法与实践》讲成"开源课程"的仓库 —— 每一章都有讲义、可运行的代码和练习。
> 另附**给 4–7 岁孩子的亲子版教学网页**：用水果摊、松果和三个篮子，种下第一颗种子。
> *An open course built from "Factor Investing: Methods and Practice" — lecture + code + exercises for every chapter, plus a parent-child storybook web course for ages 4–7.*

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

## 🧸 亲子版教学网页 / Parent-Child Web Course

给 4–7 岁孩子的第 1–7 章：**不讲公式，只种种子。** 用水果摊、松果、三个篮子、排队、公平比较、七种果子性格、组队游戏、果园怪事和传言侦探，最后用一个 7 天毕业项目，陪孩子体验「观察、等待、分散、比较、多角度看、合作、看怪事、辨传言、复盘」。

👉 **[打开亲子版教学网页](docs/index.html)** ｜ 线上版：https://justinjchen-cornell.github.io/Factor-Investing-from-Zero/

| 页面 | 内容 |
|---|---|
| [第 1 课：果子为什么一起涨价？](docs/chapter-01/lesson-1.html) | 天气一变，三种果子一起动——找“共同的原因” |
| [第 2 课：耐心的小松鼠](docs/chapter-01/lesson-2.html) | 秋天存松果，冬天不挨饿——体验等待与准备 |
| [第 3 课：三个篮子](docs/chapter-01/lesson-3.html) | 不要把果子全放一个篮子；一样的东西比价格 |
| [果子小管家](docs/chapter-01/game.html) | 5 分钟亲子游戏 + 可打印水果卡、三个罐子、7 天价格表 |
| [第 1 章家长指南](docs/chapter-01/parent-guide.html) | 五颗种子、10 分钟课堂模板、4 周计划、话术与书单 |
| **[第 2 章 · 比一比，排一排](docs/chapter-02/index.html)** | **排序、公平比较、多试几次** |
| [第 1 课：给果子排队](docs/chapter-02/lesson-1.html) | 按价格排队，再分成两档——排序法启蒙 |
| [第 2 课：公平地比一比](docs/chapter-02/lesson-2.html) | 只变一个东西——控制变量启蒙 |
| [第 3 课：多试几次才算数](docs/chapter-02/lesson-3.html) | 一次赢可能只是运气——样本量启蒙 |
| [果子排行榜](docs/chapter-02/game.html) | 按价格排 vs 按甜度排 + 可打印排行榜、公平检查表、10 次测试表 |
| [第 2 章家长指南](docs/chapter-02/parent-guide.html) | 三颗种子、10 分钟模板、4 周计划、话术与书单 |
| **[第 3 章 · 七种果子，七种性格](docs/chapter-03/index.html)** | **市场、规模、价值、动量、盈利、投资、换手率** |
| [第 1 课：果园的天气 + 大果子小果子](docs/chapter-03/lesson-1.html) | 市场与规模——一起动，但小果子动得更大 |
| [第 2 课：便宜的果子 + 会下金蛋的树](docs/chapter-03/lesson-2.html) | 价值与质量——便宜不等于好；好树也要看好价格 |
| [第 3 课：跑得快、太热闹、长新枝](docs/chapter-03/lesson-3.html) | 动量、拥挤、投资——“看起来很好”不等于“一定好” |
| [七种性格卡](docs/chapter-03/game.html) | 7 轮配对游戏 + 可打印角色卡、果园观察表 |
| [第 3 章家长指南](docs/chapter-03/parent-guide.html) | 七个角色对照表、4 周计划、话术、书单 |
| **[第 4 章 · 果园小分队](docs/chapter-04/index.html)** | **组队、轮换、够用就好——多因子模型启蒙** |
| [第 1 课：一个人不够，组个队](docs/chapter-04/lesson-1.html) | 单因子 vs 多因子——几个本领一起工作 |
| [第 2 课：轮到谁表现？](docs/chapter-04/lesson-2.html) | 因子轮动——没有谁能天天赢 |
| [第 3 课：三个就够了吗？](docs/chapter-04/lesson-3.html) | 简约原则——因子不是越多越好 |
| [果园小分队](docs/chapter-04/game.html) | 选 3 位队员挑战 6 个任务 + 可打印小队卡、挑战卡 |
| [第 4 章家长指南](docs/chapter-04/parent-guide.html) | 三颗种子、对照表、4 周计划、话术、书单 |
| **[第 5 章 · 果园里的怪事](docs/chapter-05/index.html)** | **综合体检、价格与价值、波动与风险——异象启蒙** |
| [第 1 课：给果树做体检](docs/chapter-05/lesson-1.html) | 5 项健康信号综合打分——F-Score 启蒙 |
| [第 2 课：跑远的小狗](docs/chapter-05/lesson-2.html) | 价格像小狗，价值像主人——基本面锚定反转 |
| [第 3 课：乱蹦的果子](docs/chapter-05/lesson-3.html) | 动得厉害不等于更好——特质波动率 |
| [果园怪事侦探](docs/chapter-05/game.html) | 3 个案件 + 可打印体检表、价格观察表、波动记录表 |
| [第 5 章家长指南](docs/chapter-05/parent-guide.html) | 三个怪事对照表、4 周计划、话术、书单 |
| **[第 6 章 · 果园里的传言](docs/chapter-06/index.html)** | **听说、只看一段、机器背答案——研究现状启蒙** |
| [第 1 课：听说的，不一定真](docs/chapter-06/lesson-1.html) | 传话游戏——数据窥探/因子动物园 |
| [第 2 课：只看好看的那一段](docs/chapter-06/lesson-2.html) | 完整记录 vs 只挑最好——挑选区间/发表偏差 |
| [第 3 课：机器说的，也要检查](docs/chapter-06/lesson-3.html) | 背答案 vs 真会做——过拟合/训练集与测试集 |
| [果园传言侦探](docs/chapter-06/game.html) | 3 个传言案件 + 可打印检测表、完整记录表、机器测试表 |
| [第 6 章家长指南](docs/chapter-06/parent-guide.html) | 三个传言对照表、4 周计划、话术、书单 |
| **[第 7 章 · 果园大管家（毕业项目）](docs/chapter-07/index.html)** | **计划、执行、复盘——把前六章用一遍** |
| [第 1 课：做一份果园计划](docs/chapter-07/lesson-1.html) | 选目标、分果币——投资计划/资产配置启蒙 |
| [第 2 课：管好 7 天](docs/chapter-07/lesson-2.html) | 每天四件小事——执行与记录 |
| [第 3 课：做一次复盘](docs/chapter-07/lesson-3.html) | 看完整 7 天——绩效归因启蒙 |
| [果园大管家毕业项目](docs/chapter-07/game.html) | 7 关综合挑战 + 可打印毕业证书、7 天计划表、复盘表 |
| [第 7 章家长指南](docs/chapter-07/parent-guide.html) | 一周家庭安排、复盘话术、毕业仪式、FAQ |

> 每次 10 分钟，家长陪同，不涉及真实金钱。星星进度保存在本机浏览器。
> *10 minutes per session, parent-led, no real money. Progress is stored locally in the browser.*

---

## 🗺️ 全课程总复习 / 索引

一页看完 7 章、22 个 notebook、核心公式、工具库和检查站：

👉 **[打开 COURSE-MAP.md](COURSE-MAP.md)**

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

> 进度：🎉 全部 7 章已发布（第1~7章）  
> 📘 第1章配套：[说人话学习指南](chapters/01-factor-basics/STUDY-GUIDE.md) —— 逐节讲解 + notebook 输出 + 记忆钩子 + 自测题  
> 📘 第2章配套：[说人话学习指南](chapters/02-methodology/STUDY-GUIDE.md) —— 排序法/回归/NW/GRS/正交化/GMM 逐节讲解

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

- `data/sample/`：预生成示例数据（教学小样本 + **87 只 A 股真实行情快照** 2018-2024，进 git，离线可用）
  - 日线来自**腾讯/新浪/efinance 多源兜底链**（`scripts/data_sources.py`：东财→efinance→新浪→腾讯→腾讯直连）
  - 基本面（PB/PE/总市值）来自**腾讯实时行情**（2026-09 快照，教学演示用）
- `data/cache/`：可选下载的全市场数据（`python scripts/download_data.py --all-sample`）
- 需要真实数据时：`python scripts/make_sample_data.py` 自动走兜底链刷新

## 延伸阅读 / Further Reading

- 原书《因子投资：方法与实践》及其参考文献（石川、刘洋溢、连祥斌，电子工业出版社 2020）
- 原书配套网站：https://factorwar.com
- [Microsoft qlib](https://github.com/microsoft/qlib) —— AI 量化平台（进阶机器学习因子研究）
- [QuantSkills](https://github.com/quantskills) —— 因子分析 Agent 技能
- [alphalens-reloaded](https://github.com/stefan-jansen/alphalens-reloaded) —— IC/分位分析参考实现
- [PyPortfolioOpt](https://github.com/robertmartin8/PyPortfolioOpt) —— 组合优化参考
- [困境资产中的因子思维](articles/2026-11-22-困境资产中的因子思维.md) —— 把第 2/6/7 章方法用到困境资产投资
  - [30 分钟分享大纲](articles/2026-11-22-困境资产中的因子思维-30分钟分享大纲.md) ｜ [PPTX](articles/assets/困境资产中的因子思维-30分钟分享.pptx) ｜ [工作流图](articles/assets/distressed-factor-workflow.png)
  - [PPT 逐页解读报告（Markdown）](articles/2026-11-22-困境资产中的因子思维-PPT逐页解读报告.md) ｜ [Word](articles/assets/困境资产中的因子思维-PPT逐页解读报告.docx)

## 版权声明 / Copyright

本项目是《因子投资：方法与实践》（石川、刘洋溢、连祥斌著，电子工业出版社，2020）的
**学习笔记、代码复现与原创讲解**，不复制原书正文；原书版权归作者与出版社所有。
示例数据仅含公开行情与财报字段，仅用于教学。
*This project contains original lecture notes, code reproductions and interpretations based on the book
"Factor Investing: Methods and Practice". All rights of the book belong to its authors and publisher.*
