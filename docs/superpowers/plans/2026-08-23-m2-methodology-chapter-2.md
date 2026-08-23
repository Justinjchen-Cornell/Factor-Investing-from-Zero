# M2 第2章 因子投资方法论 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: 使用 superpowers:executing-plans 逐任务执行本计划。步骤用 `- [ ]` 复选框跟踪进度。

**Goal:** 交付第2章"因子投资方法论"完整三件套（讲义 + 3 个可执行 notebook + 练习），并落地 `factor_zero` 四大核心模块（排序法/统计量/回归/因子构造），用"已知真相的合成数据"验证方法正确性。

**Architecture:** 方法实现全部进 `src/factor_zero/`（sorting/statistics/regression/factors/data_sim），每个模块配 pytest 数学性质测试；讲义把第2章 8 节组织成"分班考试→体检报告→修正眼镜→老师改卷"的比喻主线；3 个 notebook 分别演示排序法、三种回归、异象检验+GRS+正交化，全部可在离线示例数据上运行。

**Tech Stack:** Python 3.10+、pandas、numpy、scipy（GRS 的 F 分布）、statsmodels（NW 交叉验证）、matplotlib、nbformat/nbclient、pytest。

## Global Constraints

- 所有内容原创讲解，不复制原书文字；讲义模板标记：🎯📚📖📋✅。
- 每章三件套：README.md + notebooks/ + exercises/solutions/。
- `factor_zero` 模块函数都要有 docstring（教学注释），不追求过度抽象。
- 测试必须包含"已知真相验证"：合成数据上 FM 能恢复预设 λ、GRS 在 α=0 时不拒绝。
- 完成标准：pytest 全绿；3 个 notebook 全部 nbclient 执行通过；每任务独立 commit。
- 第2章 notebook 命名：`2.1-portfolio-sorting` / `2.2-regression-methods` / `2.3-anomaly-and-grs`。

---

### Task 1: factor_zero/sorting.py —— 投资组合排序法

**Files:**
- Create: `src/factor_zero/sorting.py`
- Create: `tests/test_sorting.py`

**Interfaces:**
- Consumes: 无
- Produces: `quantile_group()`、`sort_portfolios()`、`spread_return()`、`monotonicity_test()` —— 供 Task 7 notebook 与第3章复用

- [ ] **Step 1: 写测试（TDD）**

```python
"""排序法模块测试：分位分组、组合收益、价差组合、单调性检验。"""
import numpy as np
import pandas as pd

from factor_zero.sorting import quantile_group, sort_portfolios, spread_return, monotonicity_test


def test_quantile_group_ten_groups():
    s = pd.Series(np.arange(100.0))
    g = quantile_group(s, n_groups=10)
    assert g.min() == 1 and g.max() == 10
    assert g.groupby(g).size().between(9, 11).all(), "每组约10个"


def test_quantile_group_monotonic():
    s = pd.Series(np.arange(100.0))
    g = quantile_group(s, n_groups=10)
    # 变量越大组号越大（默认升序）
    assert (g.diff().dropna() >= 0).all()


def test_sort_portfolios_equal_weight():
    # 4 支股票 × 3 期：组1={A,B} 组2={C,D}，等权组合收益 = 组内均值
    ret = pd.DataFrame({
        "A": [0.01, 0.02, 0.03], "B": [0.03, 0.01, 0.02],
        "C": [0.05, 0.06, 0.04], "D": [0.07, 0.04, 0.06],
    })
    groups = pd.DataFrame({
        "A": [1, 1, 1], "B": [1, 1, 1],
        "C": [2, 2, 2], "D": [2, 2, 2],
    })
    port = sort_portfolios(ret, groups, n_groups=2)
    np.testing.assert_allclose(port[1].values, [0.02, 0.015, 0.025])
    np.testing.assert_allclose(port[2].values, [0.06, 0.05, 0.05])


def test_spread_return():
    port = pd.DataFrame({1: [0.01, 0.02], 10: [0.05, 0.04]})
    spread = spread_return(port, high=10, low=1)
    np.testing.assert_allclose(spread.values, [0.04, 0.02])


def test_monotonicity_perfect_positive():
    # 组均值完美递增 → Spearman 秩相关 = 1
    port = pd.DataFrame({g: [0.01 * g] for g in range(1, 11)})
    res = monotonicity_test(port)
    assert res["rho"] == 1.0
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_sorting.py -v`
Expected: 全部 FAIL（`factor_zero.sorting` 不存在）。

- [ ] **Step 3: 实现 `src/factor_zero/sorting.py`**

```python
"""投资组合排序法（portfolio sort）——第2章 2.1 节的代码实现。

思想：用排序变量（如 BM）的高低代替因子暴露的高低，
按分位分组构建投资组合，多空价差组合的收益率就是因子收益率。
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def quantile_group(sort_values: pd.Series, n_groups: int = 10) -> pd.Series:
    """按变量取值分位分组，返回组号 1(最低) .. n_groups(最高)。

    排序法只假设变量与因子暴露相关，不假设任何数学关系（2.1.2 节）。
    """
    pct = sort_values.rank(pct=True)
    return np.ceil(pct * n_groups).clip(1, n_groups).astype(int)


def sort_portfolios(
    ret: pd.DataFrame,
    groups: pd.DataFrame,
    n_groups: int,
    weights: str = "equal",
    mktcap: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """按分组计算各投资组合的收益率时序。

    参数
    ----
    ret : DataFrame(日期 × 股票) 收益率
    groups : DataFrame(日期 × 股票) 每期每只股票的分组号
    n_groups : 分组数 L
    weights : "equal"（等权）或 "value"（市值加权，需 mktcap）
    mktcap : DataFrame(日期 × 股票) 市值，value 加权时必传

    返回
    ----
    DataFrame(日期 × 组号 1..n_groups)，每列是一个组合的收益率时序。
    """
    out = pd.DataFrame(index=ret.index, columns=list(range(1, n_groups + 1)), dtype=float)
    for g in range(1, n_groups + 1):
        mask = (groups == g)
        if weights == "equal":
            count = mask.sum(axis=1).replace(0, np.nan)
            out[g] = (ret * mask).sum(axis=1) / count
        elif weights == "value":
            cap = mktcap.where(mask)
            total = cap.sum(axis=1)
            w = cap.div(total, axis=0)
            out[g] = (ret * w).sum(axis=1)
        else:
            raise ValueError(f"weights 仅支持 equal/value，收到 {weights}")
    return out


def spread_return(port_ret: pd.DataFrame, high: int, low: int = 1) -> pd.Series:
    """价差组合（spread portfolio）：做多高组、做空低组，收益率 = 因子收益率。"""
    return port_ret[high] - port_ret[low]


def monotonicity_test(port_ret: pd.DataFrame) -> dict:
    """单调性检验（2.1.2 节）：组合均收益与分组的 Spearman 秩相关系数。"""
    group_order = list(port_ret.columns)
    means = port_ret.mean().reindex(group_order)
    rho = means.rank().corr(pd.Series(range(1, len(group_order) + 1), index=group_order))
    return {"rho": rho, "group_means": means}
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest tests/test_sorting.py -v`
Expected: 5 个测试全部 PASS。

- [ ] **Step 5: 提交**

Run: `git add src/factor_zero/sorting.py tests/test_sorting.py && git commit -m "feat(factor_zero): add portfolio sorting module with tests"`
Expected: 提交成功。

---

### Task 2: factor_zero/statistics.py —— Newey-West 与 GRS

**Files:**
- Create: `src/factor_zero/statistics.py`
- Create: `tests/test_statistics.py`

**Interfaces:**
- Consumes: 无（纯 numpy/scipy）
- Produces: `newey_west_vcov()`、`nw_t_stat()`、`ts_regression()`、`grs_test()` —— 供 Task 8/9 notebook 与第4/5章复用

- [ ] **Step 1: 写测试（TDD）**

```python
"""统计量模块测试：NW 方差-协方差矩阵与 statsmodels 交叉验证、GRS 统计量。"""
import numpy as np
import pandas as pd

from factor_zero.statistics import newey_west_vcov, nw_t_stat, ts_regression, grs_test


def test_newey_west_matches_statsmodels():
    rng = np.random.default_rng(7)
    T, K = 300, 2
    X = rng.normal(size=(T, K))
    X[:, 0] = 1.0  # 截距
    # 制造自相关残差
    eps = np.zeros(T)
    for t in range(1, T):
        eps[t] = 0.6 * eps[t - 1] + rng.normal(0, 1)
    vcov = newey_west_vcov(X, eps)
    import statsmodels.api as sm
    m = sm.OLS(eps + X @ np.array([1.0, 2.0]), X).fit(cov_type="HAC", cov_kwds={"maxlags": 4})
    np.testing.assert_allclose(vcov, m.cov_params(), rtol=1e-6)


def test_nw_t_stat_manual():
    rng = np.random.default_rng(11)
    series = pd.Series(rng.normal(0.001, 0.02, size=120))
    t, se = nw_t_stat(series)
    assert np.isclose(se, np.sqrt(newey_west_vcov(np.ones((120, 1)), series - series.mean())[0, 0]))


def test_ts_regression_recovers_betas():
    rng = np.random.default_rng(3)
    T = 500
    f = rng.normal(0.001, 0.02, size=(T, 2))
    true_beta = np.array([1.2, -0.5])
    r = 0.001 + f @ true_beta + rng.normal(0, 0.01, size=T)
    alpha, betas, resid = ts_regression(r, pd.DataFrame(f, columns=["F1", "F2"]))
    assert abs(alpha - 0.001) < 0.001
    np.testing.assert_allclose(betas, true_beta, atol=0.05)


def test_grs_no_alpha_not_rejected():
    rng = np.random.default_rng(5)
    T, N, K = 240, 6, 3
    f = rng.normal(0.001, 0.02, size=(T, K))
    beta = rng.uniform(0.5, 1.5, size=(N, K))
    resid = rng.normal(0, 0.01, size=(T, N))
    r = beta @ f.T + resid.T  # 真实 alpha = 0
    # 用 ts_regression 估计各资产的 alpha 与残差
    alphas, resid_stack = [], np.zeros((T, N))
    for i in range(N):
        a, _, e = ts_regression(r[:, i], pd.DataFrame(f, columns=[f"F{k}" for k in range(K)]))
        alphas.append(a)
        resid_stack[:, i] = e
    F, p = grs_test(np.array(alphas), resid_stack, f)
    assert p > 0.05, f"alpha=0 时 GRS 不应拒绝，p={p:.4f}"
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_statistics.py -v`
Expected: 全部 FAIL（`factor_zero.statistics` 不存在）。

- [ ] **Step 3: 实现 `src/factor_zero/statistics.py`**

```python
"""统计量工具：Newey-West 调整、单序列 t 检验、时序回归、GRS 检验。

对应原书第2章 2.2.1（时序回归/GRS）与 2.4.3（Newey-West）。
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def newey_west_vcov(X: np.ndarray, eps: np.ndarray, max_lag: int | None = None) -> np.ndarray:
    """Newey-West 异方差自相关相合协方差矩阵（式 2.63~2.64）。

    修正了残差存在自相关和异方差时 OLS 标准误被低估的问题。
    """
    T, K = X.shape
    if max_lag is None:
        max_lag = int(np.floor(4 * (T / 100) ** (2 / 9)))  # NW(1994) 自适应规则
    Xe = X * eps[:, None]
    S = Xe.T @ Xe  # White 部分（仅异方差）
    for j in range(1, max_lag + 1):
        w = 1 - j / (max_lag + 1)  # Bartlett 核权重
        S += w * (Xe[j:].T @ Xe[:-j] + Xe[:-j].T @ Xe[j:])
    XtX_inv = np.linalg.inv(X.T @ X)
    return XtX_inv @ S @ XtX_inv


def nw_t_stat(series: pd.Series, max_lag: int | None = None) -> tuple[float, float]:
    """单收益率序列的经 Newey-West 调整的 t 检验（2.4.4 节）。

    返回 (t 值, 标准误)。X = 1 的 NW 回归即对均值序列做 HAC 修正。
    """
    T = len(series)
    resid = (series - series.mean()).to_numpy().reshape(-1, 1)
    X = np.ones((T, 1))
    vcov = newey_west_vcov(X, resid[:, 0], max_lag)
    se = np.sqrt(vcov[0, 0])
    return series.mean() / se, se


def ts_regression(
    asset_ret: np.ndarray, factor_ret: pd.DataFrame
) -> tuple[float, np.ndarray, np.ndarray]:
    """单资产时序回归：r_t = alpha + beta' f_t + eps_t（式 2.13）。

    返回 (alpha, betas, 残差序列)。
    """
    T = len(asset_ret)
    X = np.column_stack([np.ones(T), factor_ret.to_numpy()])
    coef, *_ = np.linalg.lstsq(X, asset_ret, rcond=None)
    alpha, betas = coef[0], coef[1:]
    resid = asset_ret - X @ coef
    return float(alpha), betas, resid


def grs_test(
    alphas: np.ndarray, residuals: np.ndarray, factor_ret: np.ndarray
) -> tuple[float, float]:
    """GRS 检验（Gibbons-Ross-Shanken 1989）：联合检验所有 alpha 是否为零。

    返回 (F 统计量, p 值)。原假设：alpha 全部为 0（模型完美）。
    """
    T, N = residuals.shape
    K = factor_ret.shape[1]
    mu = factor_ret.mean(axis=0)
    Sigma_f = np.cov(factor_ret, rowvar=False)
    Sigma_e = np.cov(residuals, rowvar=False)
    scalar = (T - N - K) / N * (1 + mu @ np.linalg.inv(Sigma_f) @ mu) ** (-1)
    F = scalar * (alphas @ np.linalg.inv(Sigma_e) @ alphas)
    p = 1 - stats.f.cdf(F, N, T - N - K)
    return float(F), float(p)
```

- [ ] **Step 4: 运行测试确认通过**

Run: `python -m pytest tests/test_statistics.py -v`
Expected: 4 个测试全部 PASS（NW 与 statsmodels 一致、GRS 性质成立）。

- [ ] **Step 5: 提交**

Run: `git add src/factor_zero/statistics.py tests/test_statistics.py && git commit -m "feat(factor_zero): add Newey-West and GRS statistics with tests"`
Expected: 提交成功。

---

### Task 3: factor_zero/regression.py —— 时序/截面/Fama-MacBeth 回归

**Files:**
- Create: `src/factor_zero/regression.py`
- Create: `tests/test_regression.py`

**Interfaces:**
- Consumes: `statistics.newey_west_vcov`（Task 2）
- Produces: `time_series_betas()`、`cross_sectional_lambda()`、`fama_macbeth()` —— 供 Task 8 notebook 与第4章复用

- [ ] **Step 1: 写测试（TDD）—— 核心：已知真相恢复验证**

```python
"""回归模块测试：FM 回归必须能在合成数据上恢复预设的因子溢价。"""
import numpy as np
import pandas as pd

from factor_zero.data_sim import simulate_cross_section
from factor_zero.regression import time_series_betas, cross_sectional_lambda, fama_macbeth


def test_fm_recovers_true_lambda_noiseless():
    """无噪声极限：FM 应精确恢复预设 λ（误差 < 1e-8）。"""
    sim = simulate_cross_section(n_assets=100, t_periods=120, n_factors=2,
                                 noise=0.0, seed=42)
    lam_hat, lam_t, se, t = fama_macbeth(sim["ret"], sim["char"])
    np.testing.assert_allclose(lam_hat[1:], sim["lambda"], atol=1e-8)


def test_fm_recovers_true_lambda_with_noise():
    """有噪声：恢复的 λ 应在 3 倍标准误之内（统计一致性）。"""
    sim = simulate_cross_section(n_assets=200, t_periods=240, n_factors=3,
                                 noise=0.01, seed=7)
    lam_hat, lam_t, se, t = fama_macbeth(sim["ret"], sim["char"])
    for k in range(sim["n_factors"]):
        assert abs(lam_hat[1 + k] - sim["lambda"][k]) < 3 * se[1 + k], \
            f"因子{k} 未在3se内恢复 λ"


def test_cross_sectional_lambda_shape():
    sim = simulate_cross_section(n_assets=50, t_periods=60, n_factors=2, seed=1)
    betas = pd.DataFrame(sim["beta"], columns=["F1", "F2"])
    mean_ret = sim["ret"].mean(axis=0)
    lam, alphas = cross_sectional_lambda(betas, pd.Series(mean_ret))
    assert len(lam) == 2 and len(alphas) == 50


def test_time_series_betas_recovers_beta():
    sim = simulate_cross_section(n_assets=20, t_periods=200, n_factors=2,
                                 noise=0.005, seed=3)
    fdf = pd.DataFrame(sim["factor_ret"], columns=["F1", "F2"])
    rdf = pd.DataFrame(sim["ret"], columns=[f"a{i}" for i in range(sim["n_assets"])])
    alphas, betas, resid = time_series_betas(rdf, fdf)
    np.testing.assert_allclose(betas.to_numpy(), sim["beta"], atol=0.05)
```

- [ ] **Step 2: 运行测试确认失败**

Run: `python -m pytest tests/test_regression.py -v`
Expected: 全部 FAIL（`factor_zero.data_sim` 不存在）。注意：`simulate_cross_section` 在 Task 4 实现，本任务先写测试（红灯），Task 4 点亮。

- [ ] **Step 3: 实现 `src/factor_zero/regression.py`**

```python
"""多因子模型的三种回归检验（第2章 2.2 节）。

- time_series_betas：时序回归，估计每个资产的因子暴露 beta（式 2.13）
- cross_sectional_lambda：两步截面回归，估计因子溢价 lambda（式 2.18）
- fama_macbeth：Fama-MacBeth 回归，"先回归、再均值"（式 2.36~2.40）
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from factor_zero.statistics import newey_west_vcov


def time_series_betas(
    ret: pd.DataFrame, factor_ret: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """对每个资产独立做时序回归 r_it = alpha_i + beta_i' f_t + eps_it。

    返回 (alphas: 1×N, betas: N×K, residuals: T×N)。
    """
    assets = ret.columns
    alphas, betas, resid = {}, {}, {}
    for a in assets:
        alpha, beta_vec, e = _ts_regression_single(ret[a].to_numpy(), factor_ret.to_numpy())
        alphas[a] = alpha
        betas[a] = beta_vec
        resid[a] = e
    return (
        pd.Series(alphas),
        pd.DataFrame(betas, index=assets).T,  # index=因子, columns=资产
        pd.DataFrame(resid, columns=assets),
    )


def _ts_regression_single(y: np.ndarray, f: np.ndarray) -> tuple[float, np.ndarray, np.ndarray]:
    T = len(y)
    X = np.column_stack([np.ones(T), f])
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    return float(coef[0]), coef[1:], y - X @ coef


def cross_sectional_lambda(
    betas: pd.DataFrame, mean_ret: pd.Series
) -> tuple[np.ndarray, np.ndarray]:
    """截面回归：mean_ret = lambda' beta + alpha（式 2.18，无截距）。

    返回 (lambda: K 维, alphas: N 维)。
    """
    B = betas.T.to_numpy()  # N×K
    lam, *_ = np.linalg.lstsq(B, mean_ret.to_numpy(), rcond=None)
    alphas = mean_ret.to_numpy() - B @ lam
    return lam, alphas


def fama_macbeth(
    ret: pd.DataFrame,
    characteristics: np.ndarray,
    max_lag: int | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Fama-MacBeth 回归（2.2.4 节）。

    参数
    ----
    ret : DataFrame(日期 × 股票) 超额收益率
    characteristics : ndarray(T × N × K) 时变因子暴露（公司特征）
    max_lag : Newey-West 最大滞后阶数

    返回
    ----
    (lambda 均值(K+1 含截距), lambda 时序(T×(K+1)), 标准误, t 值)
    """
    T, N, K = characteristics.shape
    X = np.concatenate([np.ones((T, N, 1)), characteristics], axis=2)  # 加截距
    lam_t = np.empty((T, K + 1))
    for t in range(T):
        coef, *_ = np.linalg.lstsq(X[t], ret.iloc[t].to_numpy(), rcond=None)
        lam_t[t] = coef
    lam_mean = lam_t.mean(axis=0)
    se = np.empty(K + 1)
    for k in range(K + 1):
        resid = lam_t[:, k] - lam_mean[k]
        vcov = newey_west_vcov(np.ones((T, 1)), resid, max_lag)
        se[k] = np.sqrt(vcov[0, 0])
    t_stat = lam_mean / se
    return lam_mean, lam_t, se, t_stat
```

- [ ] **Step 4: 运行测试（此时应因缺 data_sim 而报错，属于预期红灯）**

Run: `python -m pytest tests/test_regression.py -v`
Expected: FAIL（ModuleNotFoundError: factor_zero.data_sim）——Task 4 实现后点亮。

- [ ] **Step 5: 提交（测试与实现一起，红转绿在 Task 4）**

Run: `git add src/factor_zero/regression.py tests/test_regression.py && git commit -m "feat(factor_zero): add time-series/cross-sectional/Fama-MacBeth regression with tests"`
Expected: 提交成功（测试当前红灯，Task 4 修复）。

---

### Task 4: factor_zero/data_sim.py + factors.py —— 合成数据生成器与因子构造

**Files:**
- Create: `src/factor_zero/data_sim.py`
- Create: `src/factor_zero/factors.py`
- Create: `tests/test_factors.py`

**Interfaces:**
- Consumes: 无
- Produces: `simulate_cross_section()`（已知真相数据，Task 3/8/9 的验证基石）；`monthly_returns()`、`momentum()`、`book_to_market()`、`log_market_cap()`（Task 7 在 A 股快照上构造因子）

- [ ] **Step 1: 实现 `src/factor_zero/data_sim.py`**

```python
"""合成横截面数据生成器：已知真相，用于验证方法正确性。

生成过程（对照式 1.3）：
    1) 随机生成每只资产的因子暴露 beta（N×K）与真实因子溢价 lambda（K 维）；
    2) 按 r_it = beta_i' f_t + eps_it 生成收益时序，其中因子收益 f_t ~ N(lambda, Sigma_f)；
    3) 特征 char 直接用 beta（"公司特征=真实暴露"的理想情形，便于方法验证）。
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def simulate_cross_section(
    n_assets: int = 200,
    t_periods: int = 120,
    n_factors: int = 2,
    noise: float = 0.01,
    seed: int = 42,
) -> dict:
    rng = np.random.default_rng(seed)
    beta = rng.uniform(0.5, 1.5, size=(n_assets, n_factors))
    lam = rng.uniform(0.002, 0.010, size=n_factors)  # 月均因子溢价（已知真相）
    sigma_f = np.diag(np.full(n_factors, 0.02 ** 2))
    factor_ret = rng.multivariate_normal(lam, sigma_f, size=t_periods)
    idio = rng.normal(0, noise, size=(t_periods, n_assets))
    ret = factor_ret @ beta.T + idio
    char = np.repeat(beta[None, :, :], t_periods, axis=0)  # T×N×K 特征（恒定时变）
    return {
        "ret": pd.DataFrame(ret, columns=[f"a{i}" for i in range(n_assets)]),
        "beta": beta,
        "lambda": lam,
        "factor_ret": factor_ret,
        "char": char,
        "n_assets": n_assets,
        "n_factors": n_factors,
    }
```

- [ ] **Step 2: 实现 `src/factor_zero/factors.py`**

```python
"""常用风格因子构造（第2章 2.1 节配套；第3章会扩展为全部七大因子）。

所有函数返回 DataFrame(日期 × 股票)，与 sorting 模块接口衔接。
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def monthly_returns(prices: pd.DataFrame, freq: str = "ME") -> pd.DataFrame:
    """月末价格序列 → 月度收益率（跳过首月）。"""
    month_end = prices.resample(freq).last()
    return month_end.pct_change().dropna(how="all")


def momentum(monthly_ret: pd.DataFrame, lookback: int = 12, skip: int = 1) -> pd.DataFrame:
    """动量因子：过去 lookback 月累计收益（跳过最近 skip 月，Jegadeesh-Titman 惯例）。"""
    return (1 + monthly_ret).rolling(lookback).apply(np.prod, raw=True).shift(skip) - 1


def book_to_market(fundamentals: pd.DataFrame) -> pd.DataFrame:
    """账面市值比 BM = 1 / PB（来自估值指标表）。fundamentals 列：stock, date, pb, total_mv。"""
    f = fundamentals.copy()
    f["bm"] = 1.0 / f["pb"]
    return f.pivot(index="date", columns="stock", values="bm")


def log_market_cap(fundamentals: pd.DataFrame) -> pd.DataFrame:
    """对数市值（削弱右偏，4.2.1 节惯例）。"""
    f = fundamentals.copy()
    f["ln_mv"] = np.log(f["total_mv"])
    return f.pivot(index="date", columns="stock", values="ln_mv")
```

- [ ] **Step 3: 写因子测试 `tests/test_factors.py`**

```python
"""因子构造测试：与手工计算交叉验证。"""
import numpy as np
import pandas as pd

from factor_zero.factors import monthly_returns, momentum, book_to_market, log_market_cap


def test_monthly_returns_manual():
    dates = pd.bdate_range("2020-01-01", "2020-03-31")
    prices = pd.DataFrame({"A": np.linspace(10, 12, len(dates))}, index=dates)
    mr = monthly_returns(prices)
    # 只有 2 个月末：1月末=10.5附近, 2月末=11附近 → 月收益≈1/21（人工核验区间）
    assert len(mr) == 2
    assert (mr["A"] > 0).all()


def test_momentum_skips_recent_month():
    # 构造 15 个月收益，最后一个月暴涨；动量(12,1) 不应包含最后一个月
    idx = pd.period_range("2020-01", periods=15, freq="M").to_timestamp()
    ret = pd.DataFrame({"A": np.zeros(15)}, index=idx)
    ret.iloc[-1, 0] = 0.50  # 最近一月暴涨 50%
    mom = momentum(ret, lookback=12, skip=1)
    last = mom.dropna().iloc[-1, 0]
    assert abs(last) < 1e-9, "动量应跳过最近一个月，暴涨不应进入"


def test_book_to_market_and_log_size():
    fund = pd.DataFrame({
        "stock": ["A", "A", "B", "B"],
        "date": pd.to_datetime(["2020-01-31", "2020-02-29"] * 2),
        "pb": [2.0, 2.5, 10.0, 8.0],
        "total_mv": [1e10, 1.1e10, 1e9, 0.9e9],
    })
    bm = book_to_market(fund)
    assert abs(bm.loc["2020-01-31", "A"] - 0.5) < 1e-12
    ln = log_market_cap(fund)
    assert abs(ln.loc["2020-02-29", "B"] - np.log(0.9e9)) < 1e-9
```

- [ ] **Step 4: 运行回归测试与因子测试**

Run: `python -m pytest tests/test_regression.py tests/test_factors.py -v`
Expected: 全部 PASS（Task 3 的红灯在此点亮：FM 在无噪声时恢复 λ 误差 <1e-8、有噪声时在 3se 内）。

- [ ] **Step 5: 提交**

Run: `git add src/factor_zero/data_sim.py src/factor_zero/factors.py tests/test_factors.py && git commit -m "feat(factor_zero): add data simulator and factor construction with tests"`
Expected: 提交成功。

---

### Task 5: 第2章讲义 chapters/02-methodology/README.md

**Files:**
- Create: `chapters/02-methodology/README.md`
- Create: `chapters/02-methodology/notebooks/.gitkeep`（Task 7 起放真 notebook）
- Create: `chapters/02-methodology/exercises/solutions/.gitkeep`

**Interfaces:**
- Consumes: Task 2 的结构测试（自动检查新章节三件套）
- Produces: 第2章讲义（比喻主线：分班考试 → 体检报告 → 修正眼镜 → 老师改卷）

- [ ] **Step 1: 写入讲义**

```markdown
# 第2章 因子投资方法论

> 对应原书：第2章（2.1~2.8 节）｜ 配套代码：`notebooks/2.1-portfolio-sorting.ipynb`、`2.2-regression-methods.ipynb`、`2.3-anomaly-and-grs.ipynb` ｜ 练习：`exercises/`

## 🎯 本章目标

学完本章，你将能够：

1. 用"分班考试"的比喻完整讲出**投资组合排序法**：单变量排序、双重排序、价差组合、单调性检验；
2. 区分**时序回归、截面回归、Fama-MacBeth 回归**三种方法，并说清"先均值再回归 vs 先回归再均值"；
3. 用**Newey-West 修正眼镜**处理自相关与异方差，读懂论文里的"经 NW 调整后的 t 值"；
4. 用 **GRS 检验**判断一个多因子模型好不好（α 联合是否为零）；
5. 说出**正交化**在删除什么（重复信息/残差=增量），以及 GMM 的"账本核对"思想；
6. 在 notebook 中：用**已知真相的合成数据**亲手验证 FM 回归能恢复预设的因子溢价。

## 📚 先修要求

- 完成第1章（式 1.3 世界观）
- 会看 pandas DataFrame、会跑 notebook
- 线性代数基础：矩阵乘法、转置、逆（会用即可）

## 📖 正文

### 2.1 排序法 —— 📚"按身高分班，比成绩"

**核心问题**：因子收益率的"身价"（λ）怎么算出来？

**三步走**（对应原书 2.1.2 节）：
1. **排队**：用排序变量（如 BM）把股票从高到低排序；
2. **分班**：切成 L 组（惯例 L=10）；
3. **比赛**：高组收益 − 低组收益 = **价差组合收益 = 因子收益率**（资金中性，多空各等额）。

**两个检验**：
- **t-检验**：这个分差是"真实力"还是"运气"？|t| > 2（95% 置信）才算数；
- **单调性**：是不是"越高的班成绩越好"？—— Spearman 秩相关系数，≈1 表示完美单调。

**单变量排序的坑**：高个子班可能恰好全是富人家的孩子（混入市值因素）。解法：
- **独立双重排序（交叉法）**：市值和 BM 各自分 5 组，取交集 25 个组合，组内做差价再平均；
- **条件双重排序（分层法）**：先按市值分 5 层，每层内再按 BM 分 5 组——市值被"控制住"了。
- 学术惯例：FF3 用 2×3（市值 2 档 × BM 3 档）。

### 2.2 三种回归 —— 🏥"体检报告"

排序法算出了因子收益，但**多因子模型整体对不对**？用回归体检：

**① 时序回归（先查每人敏感度）**：r_it = α_i + β_i' f_t + ε_it
- 每个 β = 资产对因子的敏感度；α = 体检查不出的"隐藏问题"（定价误差）；
- 因子收益率时序已知（排序法给的），所以适合风格因子。

**② 截面回归（两步）**：先时序求 β，再拿"平均收益 ~ β"做截面回归
- 斜率 = 因子溢价 λ（线的斜率就是因子身价）；
- 每个点到线的距离 = α；要**Shanken 修正**（β 是估计值，有误差）。

**③ Fama-MacBeth（先回归，再均值）**——⭐必考
- 普通截面：把 T 期数据揉成一坨回归一次；FM：**每一期单独回归一次**，把 T 个 λ_t 平均；
- 妙处：绕开"截面相关性让标准误失真"的统计幻觉；
- 口诀：**截面回归 = 先均值再回归；FM = 先回归再均值。**

### 2.3 因子暴露：📏"用标签"比"猜性格"更准

- 老办法：时序回归"猜"β（通过行为猜性格，误差大）；
- 新办法：直接用**公司特征**（BM 高就是价值股、市值小就是小盘股）当暴露；
- Jegadeesh et al. (2019) 实证：**公司特征完胜**——用特征当暴露的因子被定价，用时序 β 的却没有；
- Fama-French (2020) 结论：**"截面回归多因子模型"（特征当暴露）优于传统"时序回归多因子模型"**。Barra 就是特征派。

### 2.4 异象检验 + Newey-West —— 🕶️"修正眼镜"

**检验异象**：异象组合收益对多因子模型回归，α 显著 ≠ 0 → 异象成立。

**但残差不乖**：时大时小（异方差）+ 今天影响明天（自相关）→ 普通标准误"隔着雾看东西"。
- **White 眼镜**：只修异方差；
- **Newey-West 眼镜**：两个毛病一起修（Bartlett 核权重，滞后越大权重越小）。
- 论文里"经 NW 调整后的 t 值"= 戴了修正眼镜的结果，更可信。

### 2.5 比较多因子模型 —— 📝"两个老师改卷，比谁压分少"

- **GRS 检验**：把所有测试资产的 α 打包联合检验"是否一起为零"——有限样本精确 F 分布，学界首选；
- **均值-方差张成**：模型 A 的因子组合能否"覆盖"模型 B 的机会集；
- **α 检验**：逐个资产单独查（单科复核）；
- **贝叶斯方法**：先验 + 数据结合判断。

### 2.6 正交化 —— 🗣️"只听增量信息"

"我今天吃了火锅"+"我吃了**辣的**火锅"——第二句没增量。正交化：把因子 B 对因子 A 回归，**残差 = B 的纯新增信息**。业界构建因子组合前的常规操作。

### 2.7 GMM —— 🧮"万能账本核对法"

三步：① **记账规则**（矩条件）：价格 = 未来收益折现，账必须平；② **拿数据对账**：找让账最平的参数；③ **查账**：账不平的部分是运气还是模型错？
- 核心只有两件事：**样本均值的方差** + **delta 方法**（泰勒展开）；
- 权重 W=S⁻¹ 给"更靠谱的账"更高权重（有效估计）；
- ⚠️ 别当黑箱：从金融含义选权重，别只追统计最优。

### 2.8 研究方法建议 —— 🧭"套路总结"

| 研究问题 | 标准套路 |
|---|---|
| 检验异象 | 单变量排序 → 与市值双重排序 → 时序回归看 α → FM 加控制变量 |
| 检验因子 | 金融学依据 → 排序法 t 显著 → FM 佐证 |
| 比较模型 | 同一组测试资产：GRS + α检验；互检因子：GRS + 均值方差张成 |

## 📋 本章小结

| 工具 | 一句话 |
|---|---|
| 排序法 | 用变量高低代替暴露高低，价差组合收益 = 因子收益 |
| 时序回归 | r = α + βf + ε，β=敏感度，α=定价误差 |
| 截面回归 | 平均收益 ~ β，斜率 = λ，需 Shanken 修正 |
| FM 回归 | 每期回归再平均，抗截面相关，业界标配 |
| Newey-West | 修自相关+异方差的"眼镜"，t 值更可信 |
| GRS | 联合检验所有 α 是否为零，F 分布 |
| 正交化 | 残差 = 增量信息，剔除重复 |
| GMM | 矩条件=记账规则，万能检验框架 |

## ✅ 检查站（自测题）

1. 排序法为什么能绕过"先有鸡还是先有蛋"（暴露 vs 收益率）的循环？
2. 时序回归和截面回归求出的 λ 为什么可能不同？谁更"客观"？
3. FM 回归为什么能抗截面相关性？它的代价是什么（对什么无能为力）？
4. 为什么说 Newey-West 是"修正眼镜"？它修正哪两个问题？
5. GRS 检验的原假设是什么？p 值大说明什么？
6. 正交化里的"残差"代表什么？为什么要用它？
7. GMM 的三步是什么？为什么"别当黑箱"？

> 答案见 `exercises/solutions/`。三个 notebook 带你亲手实现全部方法。
```

- [ ] **Step 2: 建目录并跑结构测试**

Run: `mkdir -p chapters/02-methodology/notebooks chapters/02-methodology/exercises/solutions && touch chapters/02-methodology/notebooks/.gitkeep chapters/02-methodology/exercises/solutions/.gitkeep && python -m pytest tests/test_course_structure.py -v`
Expected: 全部 PASS（结构测试自动覆盖新章节）。

- [ ] **Step 3: 提交**

Run: `git add chapters/02-methodology && git commit -m "feat(ch2): add chapter 2 lecture (methodology)"`
Expected: 提交成功。

---

### Task 6: notebook 2.1 —— 排序法实战（A股快照）

**Files:**
- Create: `chapters/02-methodology/notebooks/2.1-portfolio-sorting.ipynb`（由 `scripts/build_notebooks.py` 追加构建函数生成）

**Interfaces:**
- Consumes: `factor_zero.sorting`（T1）、`factor_zero.factors`（T4）、`data/sample/`（M1）
- Produces: 可执行 notebook：BM/动量单变量排序 → 单调性 → 双重排序控市值

- [ ] **Step 1: 在 `scripts/build_notebooks.py` 末尾追加构建函数**

```python
CH2_SETUP = (
    "import numpy as np\nimport pandas as pd\nimport matplotlib.pyplot as plt\n\n"
    "from factor_zero.sorting import quantile_group, sort_portfolios, spread_return, monotonicity_test\n"
    "from factor_zero.factors import monthly_returns, momentum, book_to_market, log_market_cap\n\n"
    "from pathlib import Path\n"
    "def _find_sample():\n"
    "    for p in [Path('data/sample'), Path.cwd().parents[2] / 'data' / 'sample']:\n"
    "        if p.exists():\n"
    "            return p\n"
    "    raise FileNotFoundError('找不到 data/sample，请从仓库根目录启动 notebook')\n"
    "SAMPLE = _find_sample()\n"
    "plt.rcParams['figure.dpi'] = 110"
)


def _load_ashare_snapshot() -> dict:
    """读取 A 股快照：月收益、BM、市值、动量（对齐各股票的时间索引）。"""
    daily_dir = SAMPLE / "a_share_snapshot" / "daily"
    codes = sorted(p.stem for p in daily_dir.glob("*.csv"))
    prices = {}
    for code in codes:
        df = pd.read_csv(daily_dir / f"{code}.csv", parse_dates=["date"])
        prices[code] = df.set_index("date")["close"]
    price_df = pd.DataFrame(prices).sort_index()
    fund = pd.read_csv(SAMPLE / "a_share_snapshot" / "fundamentals.csv", parse_dates=["date"])
    ret_m = monthly_returns(price_df)
    bm = book_to_market(fund)
    mv = log_market_cap(fund)
    mom = momentum(ret_m, lookback=12, skip=1)
    return {"ret": ret_m, "bm": bm, "mv": mv, "mom": mom}


def build_2_1() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    c = []
    c.append(nbf.v4.new_markdown_cell(
        "# 2.1 投资组合排序法 —— 分班考试实战\n\n"
        "对应原书 2.1 节。我们将对 A 股快照（87 只股票，2018-2024）做三件事：\n\n"
        "1. **单变量排序**：按 BM（账面市值比）分 10 组，看组均收益是否单调；\n"
        "2. **价差组合**：高减低 = 价值因子收益率，t 检验显著吗？\n"
        "3. **双重排序**：控制市值后，BM 还有增量解释力吗？"
    ))
    c.append(nbf.v4.new_code_cell(CH2_SETUP))
    c.append(nbf.v4.new_code_cell("data = _load_ashare_snapshot()\ndata['ret'].shape, data['bm'].shape"))
    c.append(nbf.v4.new_markdown_cell(
        "## 1) 单变量排序：按 BM 分 10 组\n\n"
        "**排序法只假设变量（BM）与因子暴露相关**，不假设任何数学关系（2.1.2 节）。\n"
        "我们用 t 期末的 BM 分组，看 t+1 期的组合收益（避免未来函数）。"
    ))
    c.append(nbf.v4.new_code_cell(
        "# 用 t 期 BM 分组，t+1 期收益：对齐后逐期滚动\n"
        "ret, bm = data['ret'], data['bm']\n"
        "common_idx = ret.index.intersection(bm.index)\n"
        "group_dict, port_list = {}, []\n"
        "for t in range(len(common_idx) - 1):\n"
        "    d = common_idx[t]\n"
        "    d_next = common_idx[t + 1]\n"
        "    if d not in bm.index or d_next not in ret.index:\n"
        "        continue\n"
        "    g = quantile_group(bm.loc[d].dropna(), n_groups=10)\n"
        "    group_dict[d_next] = g\n"
        "    port_list.append(d_next)\n"
        "groups = pd.DataFrame(group_dict).T.reindex(index=ret.index)\n"
        "port = sort_portfolios(ret, groups, n_groups=10)\n"
        "port.tail(3).round(4)"
    ))
    c.append(nbf.v4.new_code_cell(
        "means = port.mean()\n"
        "res = monotonicity_test(port)\n"
        "print(f'Spearman 秩相关: {res[\"rho\"]:.3f}')\n"
        "fig, ax = plt.subplots(figsize=(8, 4))\n"
        "means.plot(kind='bar', ax=ax)\n"
        "ax.set_title('按 BM 分 10 组的月均收益（%——应单调上升）')\n"
        "ax.set_xlabel('组别（1=低BM 10=高BM）'); ax.set_ylabel('月均收益')\n"
        "plt.tight_layout(); plt.show()"
    ))
    c.append(nbf.v4.new_code_cell(
        "# 价差组合：High(10) - Low(1) = 价值因子收益率\n"
        "spread = spread_return(port, high=10, low=1)\n"
        "from factor_zero.statistics import nw_t_stat\n"
        "t_val, se = nw_t_stat(spread)\n"
        "print(f'价差组合月均收益: {spread.mean()*100:.3f}%  NW调整 t={t_val:.2f}')\n"
        "print(f'|t| > 2 → 价值因子显著' if abs(t_val) > 2 else '不显著')"
    ))
    c.append(nbf.v4.new_markdown_cell(
        "## 2) 双重排序：控制市值\n\n"
        "高 BM 组会不会恰好全是小盘股？用**条件双重排序**：先按市值分 5 层，"
        "每层内再按 BM 分 5 组，看每一层内 BM 是否仍然区分收益。"
    ))
    c.append(nbf.v4.new_code_cell(
        "mv = data['mv']\n"
        "bm = data['bm']\n"
        "ret = data['ret']\n"
        "common = ret.index.intersection(bm.index).intersection(mv.index)\n"
        "spreads_by_size = {}\n"
        "for t in range(len(common) - 1):\n"
        "    d, dn = common[t], common[t + 1]\n"
        "    size_g = quantile_group(mv.loc[d].dropna(), n_groups=5)   # 市值 5 层\n"
        "    for s in range(1, 6):\n"
        "        inside = size_g[size_g == s].index\n"
        "        if len(inside) < 5:\n"
        "            continue\n"
        "        bm_inside = bm.loc[d, inside].dropna()\n"
        "        g = quantile_group(bm_inside, n_groups=5)             # 层内按 BM 分 5 组\n"
        "        sub_ret = ret.loc[dn, g.index]\n"
        "        port_s = sort_portfolios(sub_ret.to_frame().T, g.to_frame().T, n_groups=5)\n"
        "        spreads_by_size.setdefault(s, []).append(\n"
        "            port_s.iloc[0, 4] - port_s.iloc[0, 0])\n"
        "print('市值层内 BM 价差月均收益（每层=控制市值后的 BM 效果）:')\n"
        "for s in sorted(spreads_by_size):\n"
        "    vals = pd.Series(spreads_by_size[s])\n"
        "    print(f'  市值第{s}层: {vals.mean()*100:+.3f}%/月 (共{len(vals)}期)')"
    ))
    c.append(nbf.v4.new_markdown_cell(
        "## 小结\n\n"
        "- 排序法把"因子暴露未知"的循环绕开了：**变量高低 ≈ 暴露高低**；\n"
        "- 价差组合 = 因子收益率，NW t 检验看显著性；\n"
        "- 双重排序控制其他因子（这里是市值），看**增量解释力**；\n"
        "- ⚠️ 示例数据为合成快照，收益大小仅演示方法，不代表真实 A 股结论。\n\n"
        "> 下一节：三种回归方法（时序/截面/FM），用已知真相的数据验证。"
    ))
    nb.cells = c
    return nb
```

- [ ] **Step 2: 把 build_2_1 加入 main() 并构建**

Run: 修改 `main()` 为：

```python
def main() -> None:
    notebooks = {"01.1-unified-view": build_01_1(), "2.1-portfolio-sorting": build_2_1()}
    for name, nb in notebooks.items():
        chapter = name.split(".")[0]
        folder = "01-factor-basics" if chapter == "01" else "02-methodology"
        path = ROOT / "chapters" / folder / "notebooks" / f"{name}.ipynb"
        path.parent.mkdir(parents=True, exist_ok=True)
        nbf.write(nb, str(path))
        print(f"built {path}")
```

然后运行 `python scripts/build_notebooks.py`
Expected: 两个 notebook 均生成。

- [ ] **Step 3: 执行护栏验证（自动覆盖新 notebook）**

Run: `python -m pytest tests/test_notebooks.py -v`
Expected: 2 个测试 PASS（两个 notebook 从头执行成功）。

- [ ] **Step 4: 提交**

Run: `git add scripts/build_notebooks.py chapters/02-methodology/notebooks && git commit -m "feat(ch2): add portfolio sorting notebook"`
Expected: 提交成功。

---

### Task 7: notebook 2.2 —— 三种回归方法（已知真相验证）

**Files:**
- Create: `chapters/02-methodology/notebooks/2.2-regression-methods.ipynb`

**Interfaces:**
- Consumes: `factor_zero.data_sim`（T4）、`factor_zero.regression`（T3）、`factor_zero.statistics`（T2）
- Produces: 可执行 notebook：已知真相数据上 TS 恢复 β、FM 恢复 λ；A 股快照上跑 FM

- [ ] **Step 1: 在 `scripts/build_notebooks.py` 末尾追加构建函数**

```python
def build_2_2() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    c = []
    c.append(nbf.v4.new_markdown_cell(
        "# 2.2 三种回归：时序 / 截面 / Fama-MacBeth\n\n"
        "对应原书 2.2 节。**先造一个已知真相的世界**：我们预设每只股票的 β 和因子溢价 λ，"
        "生成收益数据，然后看三种方法能不能把真相"挖"回来。\n\n"
        "- 时序回归 → 恢复 β（敏感度）；\n"
        "- 截面回归 → 恢复 λ（因子身价）；\n"
        "- FM 回归 → 恢复 λ + 正确标准误。"
    ))
    c.append(nbf.v4.new_code_cell(CH2_SETUP))
    c.append(nbf.v4.new_code_cell(
        "from factor_zero.data_sim import simulate_cross_section\n"
        "from factor_zero.regression import time_series_betas, cross_sectional_lambda, fama_macbeth\n"
        "from factor_zero.statistics import nw_t_stat\n"
        "sim = simulate_cross_section(n_assets=200, t_periods=240, n_factors=3, noise=0.01, seed=7)\n"
        "print('预设的真相 λ =', sim['lambda'].round(5))\n"
        "print('收益矩阵:', sim['ret'].shape, '特征矩阵:', sim['char'].shape)"
    ))
    c.append(nbf.v4.new_markdown_cell(
        "## 1) 时序回归：恢复 β\n\n"
        "对每个资产：r_it = α_i + β_i' f_t + ε_it。估计出的 β 应该接近预设值。"
    ))
    c.append(nbf.v4.new_code_cell(
        "fdf = pd.DataFrame(sim['factor_ret'], columns=['F1', 'F2', 'F3'])\n"
        "alphas, betas, resid = time_series_betas(sim['ret'], fdf)\n"
        "err = np.abs(betas.to_numpy().T - sim['beta']).max()\n"
        "print(f'β 恢复最大误差: {err:.5f}（越小越准）')\n"
        "betas.iloc[:5, :3].round(3)"
    ))
    c.append(nbf.v4.new_markdown_cell(
        "## 2) 截面回归：恢复 λ\n\n"
        "第二步：平均收益 ~ β，斜率就是 λ。注意这里的 β 是**估计值**（生成回归变量），"
        "严格说需要 Shanken 修正（本书 2.2.2 节），我们先用朴素 OLS 感受数量级。"
    ))
    c.append(nbf.v4.new_code_cell(
        "mean_ret = sim['ret'].mean(axis=0)\n"
        "lam_cs, alphas_cs = cross_sectional_lambda(betas.T, mean_ret)\n"
        "print('截面回归 λ =', lam_cs.round(5))\n"
        "print('预设真相 λ =', sim['lambda'].round(5))"
    ))
    c.append(nbf.v4.new_markdown_cell(
        "## 3) Fama-MacBeth：恢复 λ + 标准误\n\n"
        "每一期单独做截面回归，得到 T 个 λ_t，再平均——这就是"先回归、再均值"。"
        "标准误用 Newey-West 修正。"
    ))
    c.append(nbf.v4.new_code_cell(
        "lam_fm, lam_t, se, t_stat = fama_macbeth(sim['ret'], sim['char'])\n"
        "res = pd.DataFrame({'FM λ': lam_fm[1:], '真相 λ': sim['lambda'],\n"
        "                    '标准误': se[1:], 't 值': t_stat[1:]})\n"
        "res.round(4)"
    ))
    c.append(nbf.v4.new_code_cell(
        "print('每个因子 |t| > 2 → 在 95% 置信下显著')\n"
        "print((np.abs(t_stat[1:]) > 2).all() and '全部显著 ✓' or '有不显著的因子 ✗')"
    ))
    c.append(nbf.v4.new_markdown_cell(
        "## 4) 上 A 股快照：FM 检验价值/动量/规模\n\n"
        "用第 2.1 节构造的因子（BM、动量、对数市值）当特征，跑 FM。"
        "合成数据不代表真实 A 股结论，重点是**看懂流程**。"
    ))
    c.append(nbf.v4.new_code_cell(
        "data = _load_ashare_snapshot()\n"
        "ret, bm, mom, mv = data['ret'], data['bm'], data['mom'], data['mv']\n"
        "idx = ret.index.intersection(bm.index).intersection(mv.index)\n"
        "ret = ret.loc[idx]; bm = bm.loc[idx]; mv = mv.loc[idx]\n"
        "mom = mom.reindex(idx).shift(1)  # 动量用过去信息，t 期特征对应 t 期收益\n"
        "# 特征标准化（截面 z-score），便于比较系数\n"
        "def zscore(df):\n"
        "    return df.sub(df.mean(axis=1), axis=0).div(df.std(axis=1), axis=0)\n"
        "X = np.stack([zscore(bm), zscore(mv), zscore(mom)], axis=2)\n"
        "X = np.nan_to_num(X, nan=0.0)\n"
        "lam_fm, lam_t, se, t_stat = fama_macbeth(ret, X)\n"
        "res = pd.DataFrame({'λ': lam_fm[1:], '标准误': se[1:], 't 值': t_stat[1:]},\n"
        "                   index=['价值(BM)', '规模(ln市值)', '动量'])\n"
        "res.round(4)"
    ))
    c.append(nbf.v4.new_markdown_cell(
        "## 小结\n\n"
        "- 三种回归的关系：**时序求 β → 截面求 λ**；FM = 截面回归的逐期版；\n"
        "- FM 在已知真相数据上**精确恢复预设 λ**（含标准误），方法可信；\n"
        "- 真实数据上因子显著性会随样本、区间、数据处理变化——这就是第3章要做的事。"
    ))
    nb.cells = c
    return nb
```

- [ ] **Step 2: 更新 main() 并构建**

Run: `main()` 中 notebooks 字典加 `"2.2-regression-methods": build_2_2()`，运行 `python scripts/build_notebooks.py`
Expected: 三个 notebook 生成。

- [ ] **Step 3: 执行护栏**

Run: `python -m pytest tests/test_notebooks.py -v`
Expected: PASS（三个 notebook 执行通过）。

- [ ] **Step 4: 提交**

Run: `git add scripts/build_notebooks.py chapters/02-methodology/notebooks && git commit -m "feat(ch2): add regression methods notebook"`
Expected: 提交成功。

---

### Task 9: 第2章练习与答案

**Files:**
- Create: `chapters/02-methodology/exercises/EXERCISES.md`
- Create: `chapters/02-methodology/exercises/solutions/SOLUTIONS.md`
- Delete: `chapters/02-methodology/notebooks/.gitkeep`、`chapters/02-methodology/exercises/solutions/.gitkeep`

**Interfaces:**
- Consumes: 讲义（Task 5）与三个 notebook（Task 6~8）
- Produces: 读者自测材料

- [ ] **Step 1: 写入 `EXERCISES.md`**

```markdown
# 第2章 练习

> 建议先独立完成，再看 `solutions/SOLUTIONS.md`。

## 练习 1：排序法（手算题）

某截面有 8 支股票，按 BM 从低到高排序后分组（L=4）：

| 组 | 股票 | 月均收益 |
|---|---|---|
| 1（最低） | A, B | 0.5% |
| 2 | C, D | 0.8% |
| 3 | E, F | 1.1% |
| 4（最高） | G, H | 1.6% |

1. 价差组合（组4 − 组1）的月均收益是多少？
2. 计算这 4 组收益与组号的 Spearman 秩相关，说明单调性。
3. 如果高 BM 组恰好全是小盘股，这个价差组合混入了什么因子？

## 练习 2：三种回归（概念题）

1. 时序回归、截面回归、FM 回归各解决什么问题？
2. 为什么截面回归需要 Shanken 修正？
3. FM 回归"先回归、再均值"绕开了什么问题？对什么问题无能为力？

## 练习 3：Newey-West（判断题）

判断正误并说明理由：
1. "数据有自相关时，普通 OLS 标准误会高估 t 值，让假因子看起来显著。"
2. "Newey-West 是解决异方差的唯一方法。"
3. "NW 调整后的 t 值比未调整的更可信（当残差确实存在自相关时）。"

## 练习 4：GRS（分析题）

GRS 检验的 p 值 = 0.9，说明什么？p 值 = 0.001 呢？GRS 拒绝模型后，能不能确定是"哪个"资产的 α 导致拒绝？为什么还需要 α 检验？

## 练习 5：动手（代码题）

打开 `notebooks/2.2-regression-methods.ipynb`，把 `simulate_cross_section` 的 `n_factors` 改成 5 重新运行：

1. FM 还能恢复全部 5 个 λ 吗？
2. 如果某个因子预设 λ = 0（没被定价），FM 的 t 值应该怎样？
3. 用一句话解释结果说明什么。
```

- [ ] **Step 2: 写入 `SOLUTIONS.md`**

```markdown
# 第2章 练习参考答案

## 练习 1

1. 1.6% − 0.5% = **1.1%/月**。
2. 组收益 [0.5, 0.8, 1.1, 1.6] 与组号 [1,2,3,4] 完美同序 → Spearman 秩相关 = **1.0**，完美单调。
3. 混入了**规模因子**：高 BM 组若全是小盘股，价差组合同时做多小盘、做空大盘。解法：与市值做双重排序（2.1.3 节）。

## 练习 2

1. 时序回归 → 求每个资产的因子暴露 β（r = α + βf + ε）；截面回归 → 用 β 解释平均收益的截面差异，斜率 = λ；FM → 每期单独截面回归再平均，得到 λ 的时序与标准误。
2. 因为第一步的 β 是**估计值**而非真实值（生成回归变量），用它做解释变量会带来误差（EIV 问题），Shanken 修正调整标准误（2.2.2 节）。
3. 绕开了 α 的**截面相关**对标准误的影响；对 α 的**时序相关**无能为力（需 NW 或 GMM 处理）。

## 练习 3

1. **对**（常见情形）：自相关让有效样本量下降，OLS 低估标准误 → t 值虚高 → 假因子"看起来"显著。
2. **错**：White 估计量解决异方差；NW 同时处理异方差+自相关；GMM 是更一般的框架。
3. **对**：当残差确实存在自相关/异方差时，NW 是相合估计，t 值更可信。

## 练习 4

- p = 0.9：无法拒绝"所有 α 都为零"→ 模型解释力够，通过体检。
- p = 0.001：拒绝原假设 → 存在模型解释不了的定价误差（异象），模型不够好。
- GRS 只回答"联合是否为零"，不指出**哪个**资产有问题——所以还需要逐个的 α 检验（2.5.4 节）定位问题资产。

## 练习 5

1. 应该能恢复（方法不变，样本量足够时 5 个 λ 都显著）。
2. λ=0 的因子 t 值应**接近 0、不显著**——方法能区分"被定价"与"没被定价"的因子。
3. FM 回归 + NW 是检验"因子是否被定价"的可靠工具——这正是第4章"哪些因子在 A 股被定价"的方法基础。
```

- [ ] **Step 3: 删除占位、全量验证**

Run: `rm chapters/02-methodology/notebooks/.gitkeep chapters/02-methodology/exercises/solutions/.gitkeep && python -m pytest tests/ -v`
Expected: 全部 PASS（结构/数据/方法/notebook 执行）。

- [ ] **Step 4: 提交**

Run: `git add -A chapters/02-methodology && git commit -m "feat(ch2): add exercises and solutions"`
Expected: 提交成功。

---

### Task 10: 全量验证 + M2 发布

**Files:** 无新增

- [ ] **Step 1: 全量测试**

Run: `python -m pytest tests/ -v`
Expected: 全部 PASS（约 25 个测试）。

- [ ] **Step 2: 更新 README 进度行**

Run: 将 README.md 中 `> 进度：📗 第1章已发布 ｜ 📙 第2~7章建设中` 改为 `> 进度：📗 第1~2章已发布 ｜ 📙 第3~7章建设中`，并提交。

- [ ] **Step 3: 推送**

Run: `git push`
Expected: 全部提交推送成功。

- [ ] **Step 4: 验收打卡（对照设计文档 DoD）**

- [ ] 讲义无 TODO，公式用代码块，标注原书小节 ✅
- [ ] 3 个 notebook 执行通过 ✅（护栏测试）
- [ ] 练习与检查站有答案 ✅
- [ ] pytest 全绿 ✅
- [ ] factor_zero 四大模块 + data_sim 落地，FM/GRS/NW 均有"已知真相"验证 ✅
- [ ] README 进度更新 ✅

**M2 完成。下一计划：M3（第3章 主流因子解读——七大因子 A 股实证）。**

### Task 8: notebook 2.3 —— 异象检验 + GRS + 正交化

**Files:**
- Create: `chapters/02-methodology/notebooks/2.3-anomaly-and-grs.ipynb`

**Interfaces:**
- Consumes: `factor_zero.data_sim`（T4）、`factor_zero.regression`（T3）、`factor_zero.statistics`（T2）
- Produces: 可执行 notebook：注入 α 造异象 → 检验 → GRS 模型比较 → 正交化

- [ ] **Step 1: 在 `scripts/build_notebooks.py` 末尾追加完整构建函数**

```python
def build_2_3() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    nb.metadata = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}}
    c = []
    c.append(nbf.v4.new_markdown_cell(
        "# 2.3 异象检验 + GRS + 正交化\n\n"
        "对应原书 2.4~2.6 节。今天当医生：\n\n"
        "1. **造一个异象**：给某资产注入真实 α，看时序回归能不能把它揪出来（含 NW 修正）；\n"
        "2. **GRS 体检**：三个因子够不够？\n"
        "3. **正交化**：去掉重复信息后，因子还剩多少增量。"
    ))
    c.append(nbf.v4.new_code_cell(CH2_SETUP))
    c.append(nbf.v4.new_code_cell(
        "from factor_zero.statistics import newey_west_vcov, grs_test\n"
        "from factor_zero.regression import time_series_betas\n"
        "rng = np.random.default_rng(99)\n"
        "T, N, K = 240, 8, 3\n"
        "beta = rng.uniform(0.5, 1.5, size=(N, K))\n"
        "lam = np.array([0.006, 0.004, 0.002])\n"
        "f = rng.multivariate_normal(lam, np.diag([0.02**2]*K), size=T)\n"
        "alpha_true = np.zeros(N); alpha_true[0] = 0.008\n"
        "r = alpha_true + f @ beta.T + rng.normal(0, 0.01, size=(T, N))\n"
        "print('注入真相：资产0 α=0.8%/月，其余为0')"
    ))
    c.append(nbf.v4.new_markdown_cell(
        "## 1) 时序回归检验异象（2.4.1 节）\n\n"
        "对每个资产回归 r = α + βf + ε。对比 **OLS 标准误 vs Newey-West 标准误**。"
    ))
    c.append(nbf.v4.new_code_cell(
        "fdf = pd.DataFrame(f, columns=['F1','F2','F3'])\n"
        "alphas, betas, resid = time_series_betas(pd.DataFrame(r, columns=[f'a{i}' for i in range(N)]), fdf)\n"
        "rows = []\n"
        "for i in range(N):\n"
        "    X = np.column_stack([np.ones(T), f])\n"
        "    e = resid.iloc[:, i].to_numpy()\n"
        "    vcov_ols = np.linalg.inv(X.T @ X) * (e @ e / (T - K - 1))\n"
        "    vcov_nw = newey_west_vcov(X, e)\n"
        "    rows.append({'资产': i, 'α估计(%/月)': alphas.iloc[i]*100,\n"
        "                 'OLS t': alphas.iloc[i]/np.sqrt(vcov_ols[0,0]),\n"
        "                 'NW t': alphas.iloc[i]/np.sqrt(vcov_nw[0,0]),\n"
        "                 '真相α': alpha_true[i]*100})\n"
        "pd.DataFrame(rows).round(3)"
    ))
    c.append(nbf.v4.new_markdown_cell(
        "## 2) GRS 体检：3 因子模型够吗？（2.5.1 节）\n\n"
        "GRS 联合检验所有 α 是否为零。异象存在 → 模型被拒绝（p 值小）。"
    ))
    c.append(nbf.v4.new_code_cell(
        "F, p = grs_test(alphas.to_numpy(), resid.to_numpy(), f)\n"
        "print(f'GRS F = {F:.3f}, p 值 = {p:.6f}')\n"
        "print('p < 0.05 → 模型被拒绝：存在模型解释不了的异象' if p < 0.05 else 'p ≥ 0.05 → 模型通过体检')"
    ))
    c.append(nbf.v4.new_markdown_cell(
        "## 3) 正交化：只听增量信息（2.6 节）\n\n"
        "假设 F2 ≈ F3（高度相关）——把 F3 对 F2 回归，**残差 = F3 的纯新增信息**。"
    ))
    c.append(nbf.v4.new_code_cell(
        "f2 = f[:, 1]; f3 = f[:, 2]\n"
        "beta_f3 = np.polyfit(f2, f3, 1)\n"
        "f3_orth = f3 - (beta_f3[0] * f2 + beta_f3[1])  # 残差\n"
        "print(f'F2 与 F3 相关系数: {np.corrcoef(f2, f3)[0,1]:.3f}')\n"
        "print(f'F2 与 F3正交化后的相关系数: {np.corrcoef(f2, f3_orth)[0,1]:.10f}')\n"
        "print('→ 正交化后相关性归零，残差就是 F3 独有的信息')"
    ))
    c.append(nbf.v4.new_markdown_cell(
        "## 小结\n\n"
        "- **异象检验** = 回归 α 显著 ≠ 0（别忘了 NW 眼镜）；\n"
        "- **GRS** = 把一群资产的 α 打包查，模型好不好看 p 值；\n"
        "- **正交化** = 残差即增量，业界构建因子前的标准动作。\n\n"
        "> 下一章：把这些方法用到 A 股七大因子上（第3章）。"
    ))
    nb.cells = c
    return nb
```

- [ ] **Step 2: 更新 main() 并构建**

Run: `main()` 中 notebooks 字典加 `"2.3-anomaly-and-grs": build_2_3()`，运行 `python scripts/build_notebooks.py`
Expected: 四个 notebook 生成。

- [ ] **Step 3: 执行护栏**

Run: `python -m pytest tests/test_notebooks.py -v`
Expected: PASS（四个 notebook 执行通过）。

- [ ] **Step 4: 提交**

Run: `git add scripts/build_notebooks.py chapters/02-methodology/notebooks && git commit -m "feat(ch2): add anomaly/GRS/orthogonalization notebook"`
Expected: 提交成功。
