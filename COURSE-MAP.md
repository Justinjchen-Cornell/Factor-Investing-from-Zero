# 🗺️ 课程总复习与索引

> 《Factor-Investing-from-Zero》7 章 · 22 个 notebook · 一页看完学习路径、核心公式、工具库和检查站。

## 1. 课程地图

| 章节 | 核心问题 | 关键产出 | Notebooks | 练习 |
|---|---|---|---|---|
| [第1章 因子投资基础](chapters/01-factor-basics/README.md) | 用什么公式统一理解因子投资？ | E[R]=βλ+α、因子/模型/异象、协方差降维 | 3 | [练习](chapters/01-factor-basics/exercises/EXERCISES.md) |
| [第2章 因子投资方法论](chapters/02-methodology/README.md) | 怎么检验因子/模型？ | 排序法、时序/截面/FM、NW、GRS、正交化 | 3 | [练习](chapters/02-methodology/exercises/EXERCISES.md) |
| [第3章 主流因子解读](chapters/03-mainstream-factors/README.md) | 七大因子怎么构造、A 股是否有效？ | 市场/规模/价值/动量/盈利/投资/换手率 | 3 | [练习](chapters/03-mainstream-factors/exercises/EXERCISES.md) |
| [第4章 多因子模型](chapters/04-multi-factor-models/README.md) | 怎么把因子组合成模型、怎么比较？ | FF3/Carhart4/NovyMarx4/FF5/HXZ4/SY4/DHS3 | 3 | [练习](chapters/04-multi-factor-models/exercises/EXERCISES.md) |
| [第5章 异象研究](chapters/05-anomalies/README.md) | 哪些“奇怪现象”可能是真的？ | F-Score、52 周高点、长期反转、IVOL | 3 | [练习](chapters/05-anomalies/exercises/EXERCISES.md) |
| [第6章 因子研究现状](chapters/06-current-research/README.md) | 怎么判断一个因子靠不靠谱？ | p-hacking、因子动物园、行为金融、ML | 3 | [练习](chapters/06-current-research/exercises/EXERCISES.md) |
| [第7章 因子投资实践](chapters/07-practice/README.md) | 怎么把因子做成组合/产品？ | 风险模型、优化、Smart Beta、归因、结业项目 | 4 | [练习](chapters/07-practice/exercises/EXERCISES.md) |

## 2. 三条学习路径

| 路径 | 顺序 | 适合谁 |
|---|---|---|
| **零基础系统学** | 1 → 2 → 3 → 4 → 5 → 6 → 7 | 想完整建立因子投资世界观 |
| **实务速查** | 2 → 3 → 4 → 7 | 已懂基本概念，想快速做组合/归因 |
| **研究进阶** | 2 → 4 → 5 → 6 → 7 | 想做因子研究/写论文/做策略 |

## 3. 一页公式表

### 第1章：统一视角

```
E[R_i] = β_i' λ + α_i          # 预期收益 = 暴露 × 溢价 + 定价误差
Σ = B Σ_f B' + D               # 协方差 = 因子风险 + 特质风险
```

### 第2章：方法论

```
价差组合 = R_high − R_low                    # 排序法：因子收益率
r_it = α_i + β_i' f_t + ε_it                 # 时序回归：β/α
mean(R_i) = λ' β_i + α_i                     # 截面回归：λ
λ_t = 每期截面回归；λ = mean(λ_t)             # Fama-MacBeth
NW 协方差 = 异方差 + 自相关的 HAC 修正         # Newey-West
GRS: H0: α_1 = ... = α_N = 0                 # 联合检验
B⊥ = B − β·A                                 # 正交化：残差 = 增量
```

### 第3章：七大因子

```
MKT  = 市值加权市场收益
SMB  = 小市值 − 大市值
HML  = 高 BM − 低 BM
WML  = 高动量 − 低动量（12-1）
RMW  = 高 ROE − 低 ROE
CMA  = 低投资 − 高投资
TURN = 低换手 − 高换手
```

### 第4章：七大模型

```
FF3       = MKT + SMB + HML
Carhart4  = FF3 + WML
NovyMarx4 = MKT + HML + WML + RMW
FF5       = FF3 + RMW + CMA
HXZ4      = MKT + SMB + RMW + CMA
SY4       = MKT + SMB + MGMT + PERF（本仓库用 RMW/WML 近似）
DHS3      = MKT + FIN + PEAD（本仓库用 HML/WML 近似）
```

### 第5章：异象

```
F-Score = 9 个财务信号之和（0~9）
52周高点距离 = P_t / max(P_{t-11}, ..., P_t)
IVOL = 多因子回归残差的标准差（滚动窗口，年化）
```

### 第6章：研究现状

```
|t| > 2.0  → 传统 5% 显著
|t| > 3.0  → Harvey et al. (2016) 多重检验门槛
|t| > 3.4  → Chordia et al. (2020) 更严格门槛
发表后衰减 ≈ 50%+（McLean & Pontiff 2016）
```

### 第7章：实践

```
Σ = B Σ_f B' + D                       # 风险模型
max_w w'μ − λ/2·w'Σw                   # 均值-方差优化
s.t. Σw=1, w≥0, w≤cap
r_p = α + β'f + ε                      # Sharpe 风格回归
总波动 = Σ 因子风险贡献 + 特质风险贡献    # Euler 风险归因
组合收益 = Σ 因子暴露 × 因子收益 + α      # 业绩归因
```

## 4. 22 个 notebook 索引

| # | Notebook | 一句话 |
|---|---|---|
| 01.1 | [一个公式看懂因子投资](chapters/01-factor-basics/notebooks/01.1-unified-formula.ipynb) | βλ+α、因子/模型/异象、协方差降维 |
| 01.2 | [学术起源](chapters/01-factor-basics/notebooks/01.2-academic-origins.ipynb) | CAPM→APT→FF3、三位诺奖、数据窥探模拟 |
| 01.3 | [业界全景](chapters/01-factor-basics/notebooks/01.3-industry-practice.ipynb) | 管理人 5 件事、80% 收益来自 β、ETF 费率 |
| 02.1 | [投资组合排序法](chapters/02-methodology/notebooks/02.1-portfolio-sorting.ipynb) | BM 排序、价差组合、NW t、双重排序 |
| 02.2 | [三种回归](chapters/02-methodology/notebooks/02.2-regression-methods.ipynb) | 时序 β、截面 λ、FM、已知真相验证 |
| 02.3 | [异象检验 + GRS](chapters/02-methodology/notebooks/02.3-anomaly-and-grs.ipynb) | 注入 α、OLS vs NW、GRS、正交化 |
| 03.1 | [数据处理与七大因子](chapters/03-mainstream-factors/notebooks/03.1-data-and-factors.ipynb) | 月度面板、七大因子构造、相关性 |
| 03.2 | [分组单调性](chapters/03-mainstream-factors/notebooks/03.2-factor-sorting.ipynb) | 10 组单调性、多空组合、控市值双重排序 |
| 03.3 | [绩效与稳健性](chapters/03-mainstream-factors/notebooks/03.3-performance-and-robustness.ipynb) | 绩效、净值、相关性、分区间、正交化 |
| 04.1 | [七大模型](chapters/04-multi-factor-models/notebooks/04.1-seven-models.ipynb) | FF3/Carhart4/FF5/HXZ4/SY4/DHS3 定义与嵌套 |
| 04.2 | [模型比较](chapters/04-multi-factor-models/notebooks/04.2-model-comparison.ipynb) | 15 个测试资产、GRS、平均 \|α\|、R² |
| 04.3 | [被定价因子与简约性](chapters/04-multi-factor-models/notebooks/04.3-priced-factors-and-parsimony.ipynb) | 单/多变量 FM、被定价因子、简约性 |
| 05.1 | [F-Score](chapters/05-anomalies/notebooks/05.1-f-score.ipynb) | 九信号财务体检、高/低分组多空 |
| 05.2 | [锚定与反转](chapters/05-anomalies/notebooks/05.2-anchoring-reversal.ipynb) | 52 周高点、长期反转 |
| 05.3 | [特质波动率](chapters/05-anomalies/notebooks/05.3-idiosyncratic-volatility.ipynb) | 滚动 FF3 残差 IVOL、控市值双重排序 |
| 06.1 | [p-hacking 与因子动物园](chapters/06-current-research/notebooks/06.1-p-hacking-and-factor-zoo.ipynb) | 纯噪声因子、t 门槛、发表衰减 |
| 06.2 | [行为金融](chapters/06-current-research/notebooks/06.2-behavioral-finance.ipynb) | 情绪代理、短期反转、行为四来源 |
| 06.3 | [机器学习与过拟合](chapters/06-current-research/notebooks/06.3-machine-learning-and-overfitting.ipynb) | 多项式/随机森林、时间序列 ML 失效 |
| 07.1 | [风险模型与优化](chapters/07-practice/notebooks/07.1-risk-model-and-optimization.ipynb) | 迷你风险模型、最小方差/最大 Sharpe |
| 07.2 | [Smart Beta 与择时](chapters/07-practice/notebooks/07.2-smart-beta-and-timing.ipynb) | 复合分数、等权/分数加权、因子择时 |
| 07.3 | [风格分析与归因](chapters/07-practice/notebooks/07.3-style-analysis-and-attribution.ipynb) | Sharpe 回归、风险归因、业绩归因 |
| 07.4 | [结业项目](chapters/07-practice/notebooks/07.4-capstone.ipynb) | 多因子组合、绩效、换手、归因、报告 |

## 5. 工具库地图

| 模块 | 关键函数 | 用途 |
|---|---|---|
| `factor_zero.sorting` | `quantile_group`, `sort_portfolios`, `spread_return`, `monotonicity_test`, `long_short_factor` | 排序法/多空组合 |
| `factor_zero.statistics` | `newey_west_vcov`, `nw_t_stat`, `ts_regression`, `grs_test`, `factor_summary` | NW/GRS/绩效 |
| `factor_zero.regression` | `time_series_betas`, `cross_sectional_lambda`, `fama_macbeth` | 三种回归 |
| `factor_zero.factors` | `monthly_returns`, `momentum`, `book_to_market`, `log_market_cap`, `earnings_yield`, `build_factor_returns` | 因子构造 |
| `factor_zero.data` | `load_ashare_panel` | A 股面板加载 |
| `factor_zero.models` | `MODEL_DEFINITIONS`, `build_test_assets`, `compare_models` | 多因子模型比较 |
| `factor_zero.anomalies` | `piotroski_f_score`, `distance_from_52w_high`, `rolling_ivol` | 异象工具 |
| `factor_zero.research` | `simulate_random_factors`, `p_hacking_summary`, `publication_decay_experiment`, `polynomial_train_test_mse`, `sentiment_signal` | 研究模拟 |
| `factor_zero.portfolio` | `build_style_exposures`, `factor_covariance`, `portfolio_risk`, `min_variance_weights`, `max_sharpe_weights`, `style_regression`, `smart_beta_weights` | 风险/组合/归因 |

## 6. 七章复习卡

### 第1章 因子投资基础
- **一句话**：因子是资产收益的“营养成分”，一只股票 = 一组因子暴露 × 因子溢价 + 定价误差。
- **记住**：E[R]=βλ+α；因子两必要条件（共同运动、长期正溢价）；Σ=BΣ_fB'+D 是降维。
- **坑**：把“相关”当“因果”；把“因子”当“选股指标”。

### 第2章 因子投资方法论
- **一句话**：把“感觉”变成“可检验的统计量”。
- **记住**：排序法 → 价差组合；时序 β → 截面 λ；FM 先回归再均值；NW 修自相关/异方差；GRS 联合检验 α；正交化残差=增量。
- **坑**：只看 t 值、不看经济逻辑；FM 忘记 NW；GRS 拒绝后不知道哪个资产有问题。

### 第3章 主流因子解读
- **一句话**：七大因子各有经济逻辑，A 股结论与美股不同。
- **记住**：MKT/SMB/HML/WML/RMW/CMA/TURN；方向要写清楚；数据清洗决定结果。
- **坑**：把“小盘/便宜/动量”当稳赚；忽略交易成本/容量；用未来数据。

### 第4章 多因子模型
- **一句话**：用少数因子解释大量收益差异，模型不是越多越好。
- **记住**：FF3/Carhart4/NovyMarx4/FF5/HXZ4/SY4/DHS3；GRS+平均 |α|+R²；简约性。
- **坑**：因子越多越好；忽略因子相关性；把样本内 R² 当样本外能力。

### 第5章 异象研究
- **一句话**：异象可能是风险补偿、错误定价，也可能是数据窥探。
- **记住**：F-Score 九信号；52 周高点锚定；长期反转；IVOL 之谜。
- **坑**：把单一异象当规律；忽略套利限制；不做样本外/稳健性。

### 第6章 因子研究现状
- **一句话**：试得够多，总能“显著”；先怀疑，再验证。
- **记住**：t 门槛 2→3→3.4；发表后衰减 50%+；行为四来源；ML 四陷阱。
- **坑**：p-hacking；只挑好看区间；随机打乱时间序列；黑箱模型。

### 第7章 因子投资实践
- **一句话**：收益模型决定“偏不偏”，风险模型决定“稳不稳”，归因决定“知不知”。
- **记住**：Σ=BΣ_fB'+D；均值-方差=误差最大化器；Smart Beta 加权；Sharpe 回归；风险/业绩归因。
- **坑**：模型错位；忽略交易成本/容量；把 α 当真；不做样本外。

## 7. 检查站与练习总表

| 章节 | 检查站 | 练习 | 答案 |
|---|---|---|---|
| 第1章 | [README](chapters/01-factor-basics/README.md) | [EXERCISES](chapters/01-factor-basics/exercises/EXERCISES.md) | [SOLUTIONS](chapters/01-factor-basics/exercises/solutions/SOLUTIONS.md) |
| 第2章 | [README](chapters/02-methodology/README.md) | [EXERCISES](chapters/02-methodology/exercises/EXERCISES.md) | [SOLUTIONS](chapters/02-methodology/exercises/solutions/SOLUTIONS.md) |
| 第3章 | [README](chapters/03-mainstream-factors/README.md) | [EXERCISES](chapters/03-mainstream-factors/exercises/EXERCISES.md) | [SOLUTIONS](chapters/03-mainstream-factors/exercises/solutions/SOLUTIONS.md) |
| 第4章 | [README](chapters/04-multi-factor-models/README.md) | [EXERCISES](chapters/04-multi-factor-models/exercises/EXERCISES.md) | [SOLUTIONS](chapters/04-multi-factor-models/exercises/solutions/SOLUTIONS.md) |
| 第5章 | [README](chapters/05-anomalies/README.md) | [EXERCISES](chapters/05-anomalies/exercises/EXERCISES.md) | [SOLUTIONS](chapters/05-anomalies/exercises/solutions/SOLUTIONS.md) |
| 第6章 | [README](chapters/06-current-research/README.md) | [EXERCISES](chapters/06-current-research/exercises/EXERCISES.md) | [SOLUTIONS](chapters/06-current-research/exercises/solutions/SOLUTIONS.md) |
| 第7章 | [README](chapters/07-practice/README.md) | [EXERCISES](chapters/07-practice/exercises/EXERCISES.md) | [SOLUTIONS](chapters/07-practice/exercises/solutions/SOLUTIONS.md) |

## 8. 因子研究 checklist（贴在显示器上）

- [ ] **经济逻辑**：为什么会有溢价？风险补偿还是行为偏差？
- [ ] **数据时点**：用的是当时可知的数据吗？有前视/幸存者偏差吗？
- [ ] **样本外**：留出最后一段样本，或滚动/扩展窗口。
- [ ] **多重检验**：试了多少次？t 门槛够高吗？做了 FDR/Bonferroni 吗？
- [ ] **稳健性**：换窗口、换分组、换因子模型、分区间、换数据源。
- [ ] **交易成本**：扣费用、冲击、容量；高换手策略尤其注意。
- [ ] **归因**：收益/风险从哪里来？因子贡献 vs α vs 特质。
- [ ] **局限**：样本、口径、模型错位、数据质量；不把结论外推。

## 9. 数据与限制（务必记住）

- 日线行情：**87 只 A 股，2018-2024**，真实快照；
- 估值：只有**一期快照**（2026-09-01），逐期估值/ROE/投资为**教学合成面板**；
- 没有完整财报、行业分类、Barra 因子数据；
- 因此 notebook 的数值**只用于演示方法**，不代表真实 A 股结论；
- 原书的 A 股结论请以原书样本与口径为准。

## 10. 完成度与重建

| 项目 | 数量/状态 |
|---|---|
| 章节 | 7 |
| Notebooks | 22 |
| 讲义 README | 7 |
| 练习 + 答案 | 7 + 7 |
| 工具库模块 | 9 |
| 测试 | 60 passed（含全部 notebook 执行） |

```bash
# 重建全部 notebook
python scripts/build_notebooks.py

# 跑全量测试
python -m pytest tests/ -q

# 打开课程
jupyter lab chapters/
```

> 🎓 **课程完成**：因子研究是怀疑与验证的手艺，不是寻找圣杯。
