# 交接摘要：Factor-Investing-from-Zero

> 生成日期：2026-11-22 ｜ 用途：新会话/新协作者快速接手 ｜ 最新提交：`a59d02c`

## 1. 项目当前目标和所处阶段

**目标**：把《因子投资：方法与实践》做成一套可复现的开源课程（7 章：讲义 + 可执行 notebook + 练习/答案），并衍生出亲子版网页、实战文章和分享材料。

**当前阶段**：**主体全部完成，进入“说人话学习指南”逐章补全阶段。**

- 成人版 7 章全部完成：**22 个 notebook、60 个测试全部通过**
- 第 1、2 章「说人话学习指南」已完成
- 亲子版网页 7 章已完成并上线 GitHub Pages
- 《困境资产中的因子思维》文章、工作流图、30 分钟 PPT、逐页解读报告（MD + DOCX）已完成
- 仓库工作区干净，最新提交：`a59d02c docs(ch2): add plain-language study guide...`

## 2. 关键技术决策和已排除的方案

| 决策 | 说明 |
|---|---|
| **离线优先** | notebook 全部基于 `data/sample/` 运行，不依赖联网/akshare |
| **真实价格 + 教学合成基本面** | 87 只 A 股日线（2018–2024）真实；估值只有一期快照，逐期估值/ROE/投资用“价格路径 + 快照”推导教学面板，**所有结论均标注“不代表真实 A 股”** |
| **每章三件套** | `README.md` + `notebooks/` + `exercises/solutions/`；结构测试强制检查 |
| **notebook 由脚本生成** | `scripts/build_notebooks.py` 调用 `build_ch2~ch7_notebooks.py`，用 nbformat 生成；执行后用 nbclient 保存输出 |
| **工具库 `factor_zero`** | 排序、统计、回归、因子、数据、模型、异象、研究模拟、组合/风险/归因，均有测试 |
| **亲子版独立静态站** | `docs/` 下纯 HTML/CSS/JS，无外部依赖；localStorage 存星星，Web Speech API 朗读；GitHub Pages 从 `main /docs` 发布 |
| **文章/PPT 程序化生成** | 工作流图用 matplotlib 导出 PNG/SVG；PPTX 用 python-pptx；DOCX 用 python-docx |

**已排除**：

- 不为 notebook 引入联网下载（保证离线可跑）
- 不把估值快照做成静态单期截面（无法演示逐期排序）
- 不新建 `chapters/00-...` 索引章（会破坏三件套结构测试）；改用根目录 `COURSE-MAP.md`
- 不用 GitHub Actions 发布 Pages（gh token 缺 `workflow` scope）；改用 `/docs` legacy Pages
- 不用 LibreOffice 转 PDF（环境未安装）；目前只出 DOCX
- 不引入深度学习/复杂 ML；第 6 章只用 scikit-learn 做过拟合示例

## 3. 已修改的重要文件路径及改动内容

### 课程主体
- `chapters/01-factor-basics/` ~ `chapters/07-practice/`
  - 7 个 `README.md` 讲义
  - 22 个 notebook（第 1–6 章各 3 个，第 7 章 4 个，含结业项目）
  - 每章 `exercises/EXERCISES.md` + `solutions/SOLUTIONS.md`
- `chapters/01-factor-basics/STUDY-GUIDE.md`、`chapters/02-methodology/STUDY-GUIDE.md`
  - 新增的逐节“说人话”指南：概念解释 + notebook 输出解读 + 记忆钩子 + 自测题
- `COURSE-MAP.md`
  - 7 章地图、三条学习路径、公式表、22 个 notebook 索引、工具库地图、七章复习卡、检查站总表

### 工具库
- `src/factor_zero/sorting.py`：`quantile_group`、`sort_portfolios`、`spread_return`、`monotonicity_test`、`long_short_factor`
- `src/factor_zero/statistics.py`：NW、`nw_t_stat`、`ts_regression`、`grs_test`、`factor_summary`
- `src/factor_zero/regression.py`：`time_series_betas`、`cross_sectional_lambda`、`fama_macbeth`
- `src/factor_zero/factors.py`：`monthly_returns`、`momentum`、`book_to_market`、`log_market_cap`、`earnings_yield`、`build_factor_returns`
- `src/factor_zero/data.py`：`load_ashare_panel`
- `src/factor_zero/models.py`：七大模型定义、`build_test_assets`、`compare_models`
- `src/factor_zero/anomalies.py`：F-Score、52 周高点、`rolling_ivol`
- `src/factor_zero/research.py`：p-hacking、发表衰减、多项式过拟合、情绪信号
- `src/factor_zero/portfolio.py`：风险模型、最小方差/最大 Sharpe、风格回归、Smart Beta 权重

### 脚本与测试
- `scripts/build_notebooks.py` + `scripts/build_ch2~ch7_notebooks.py`
- `scripts/make_workflow_diagram.py`、`make_share_ppt.py`、`make_report_docx.py`
- `tests/`：11 个测试文件，60 个测试（含全部 notebook 执行）
- `requirements.txt`：新增 `scikit-learn==1.9.1`

### 亲子版与文章
- `docs/`：亲子版第 1–7 章网页、`assets/style.css`、`assets/app.js`
- `articles/2026-11-22-困境资产中的因子思维.md`
- `articles/2026-11-22-困境资产中的因子思维-30分钟分享大纲.md`
- `articles/2026-11-22-困境资产中的因子思维-PPT逐页解读报告.md`
- `articles/assets/`：工作流 PNG/SVG、分享 PPTX、解读报告 DOCX
- `README.md`：课程导航、亲子版入口、文章/报告链接、进度更新

## 4. 未决问题和风险点

1. **数据限制（最大风险）**：估值/ROE/投资为教学合成面板，仅 87 只股票、未完整过滤 ST/涨跌停/次新股；notebook 数值不能当真实 A 股结论。
2. **学习指南只完成 1–2 章**：第 3–7 章尚未做“说人话”版。
3. **重建 notebook 会丢输出**：运行 `python scripts/build_notebooks.py` 会重写 notebook 且不带输出；需再用 nbclient 执行并保存。
4. **PDF 未生成**：环境无 LibreOffice；目前只有 DOCX，需用 Word/WPS 手动另存 PDF。
5. **Office 临时锁文件**：PPTX 可能被 PowerPoint/WPS 打开，产生 `~$...pptx`；不要提交，关闭 Office 后自动消失。
6. **安全**：8 月历史对话里曾出现 GitHub PAT 明文，仍存在 `~/.claude/history.jsonl`；建议尽快到 GitHub 吊销并检查仓库操作。
7. **对外发布前需复核**：文章/PPT 中部分数字是教学面板结果，公开发布前要确认口径和免责声明。

## 5. 下一步任务建议

**优先级 1：继续学习指南**
- 做第 3 章「主流因子解读」说人话指南（按 3.1 数据处理 + 3.2~3.8 七大因子 + notebook 03.1–03.3 输出）。
- 之后依次第 4–7 章；保持同一结构：概念解释 + notebook 输出 + 记忆钩子 + 自测题 + 常见混淆 + 三遍复习法。

**优先级 2：整理成册**
- 把第 1、2 章指南导出为 Word/PDF 学习手册；后续章节完成后合并成《因子投资从零学 · 学习手册》。

**优先级 3：真实数据验证**
- 用 `scripts/download_data.py`/akshare 拉全市场数据，替换教学面板，重跑第 3–7 章，标注哪些结论在真实数据下成立/不成立。

**优先级 4：外部分享**
- 复核文章/PPT/解读报告的事实与口径；可再出 15 分钟精简版或 5 分钟闪电版。
- 安全事项：吊销历史 PAT，避免继续留在 `history.jsonl`。

**交接一句话**：

> 课程主体和工具链已稳定，当前只需按章节继续写“说人话学习指南”；所有 notebook 改动后务必执行并保存输出，所有对外结论必须保留“教学面板，不代表真实 A 股”的声明。
