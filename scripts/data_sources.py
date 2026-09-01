"""A 股数据源统一入口：按优先级链式尝试，任一成功即返回。

兜底链（本机实测，2026-08）：
    1) akshare stock_zh_a_hist      —— 东方财富（部分网络被代理拦截）
    2) efinance                     —— 东方财富（另一实现，本机可用）
    3) akshare stock_zh_a_daily     —— 新浪（本机可用）
    4) akshare stock_zh_a_hist_tx   —— 腾讯（本机可用，较慢）
    5) 腾讯 K线 API（直连）          —— 本机最快（~0.3s）
全部失败则抛异常，由调用方回退合成数据。

统一输出列：date, open, high, low, close, volume
"""
from __future__ import annotations

import json
import urllib.request

import pandas as pd


def _prefix(code: str) -> str:
    """A 股代码转交易所前缀：6 开头→sh，0/3 开头→sz。"""
    return ("sh" if code.startswith("6") else "sz") + code


def _fetch_akshare_em(code: str, start: str, end: str) -> pd.DataFrame:
    import akshare as ak
    df = ak.stock_zh_a_hist(
        symbol=code, period="daily",
        start_date=start.replace("-", ""), end_date=end.replace("-", ""),
        adjust="qfq",
    )
    return pd.DataFrame({
        "date": pd.to_datetime(df["日期"]), "open": df["开盘"],
        "high": df["最高"], "low": df["最低"],
        "close": df["收盘"], "volume": df["成交量"],
    })


def _fetch_efinance(code: str, start: str, end: str) -> pd.DataFrame:
    import efinance as ef
    df = ef.stock.get_quote_history(
        code, beg=start.replace("-", ""), end=end.replace("-", ""), klt=101
    )
    return pd.DataFrame({
        "date": pd.to_datetime(df["日期"]), "open": df["开盘"],
        "high": df["最高"], "low": df["最低"],
        "close": df["收盘"], "volume": df["成交量"],
    })


def _fetch_akshare_sina(code: str, start: str, end: str) -> pd.DataFrame:
    import akshare as ak
    df = ak.stock_zh_a_daily(symbol=_prefix(code), start_date=start, end_date=end, adjust="qfq")
    return pd.DataFrame({
        "date": pd.to_datetime(df["date"]), "open": df["open"],
        "high": df["high"], "low": df["low"],
        "close": df["close"], "volume": df["volume"],
    })


def _fetch_akshare_tx(code: str, start: str, end: str) -> pd.DataFrame:
    import akshare as ak
    df = ak.stock_zh_a_hist_tx(
        symbol=_prefix(code),
        start_date=start.replace("-", ""), end_date=end.replace("-", ""),
        adjust="qfq",
    )
    return pd.DataFrame({
        "date": pd.to_datetime(df["date"]), "open": df["open"],
        "high": df["high"], "low": df["low"],
        "close": df["close"], "volume": df["amount"],
    })


def _fetch_tencent_direct(code: str, start: str, end: str) -> pd.DataFrame:
    """腾讯 K 线 API 直连（最快，无需任何第三方库）。"""
    symbol = _prefix(code)
    url = (f"https://web.ifzq.gtimg.cn/appstock/app/fqkline/get?"
           f"param={symbol},day,{start},{end},2000,qfq")
    with urllib.request.urlopen(url, timeout=15) as r:
        d = json.loads(r.read().decode("utf-8"))
    key = "qfqday" if "qfqday" in d["data"][symbol] else "day"
    rows = d["data"][symbol][key]  # [date, open, close, high, low, volume, ...]
    return pd.DataFrame(rows, columns=["date", "open", "close", "high", "low", "volume", "_"])
    # 列顺序注意：腾讯返回 open/close/high/low


_CHAIN = [
    ("akshare-eastmoney", _fetch_akshare_em),
    ("efinance", _fetch_efinance),
    ("akshare-sina", _fetch_akshare_sina),
    ("akshare-tencent", _fetch_akshare_tx),
    ("tencent-direct", _fetch_tencent_direct),
]


def fetch_daily(code: str, start: str, end: str, verbose: bool = False) -> pd.DataFrame:
    """按优先级链式获取日线，返回统一列（date/open/high/low/close/volume）。"""
    errors = []
    for name, fn in _CHAIN:
        try:
            df = fn(code, start, end)
            df = df.sort_values("date").reset_index(drop=True)
            if len(df) < 10:
                raise ValueError(f"仅 {len(df)} 行")
            if verbose:
                print(f"  [{name}] {code} ok ({len(df)} 行)")
            return df
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{name}: {type(exc).__name__}")
    raise RuntimeError(f"{code} 全部数据源失败: {'; '.join(errors)}")


def fetch_fundamentals_snapshot(codes: list[str] | None = None, verbose: bool = False) -> pd.DataFrame:
    """估值快照：stock, trade_date, pb, pe, total_mv（真实数据）。

    主源：腾讯实时行情（qt.gtimg.cn，逐只请求，含 市盈率[39]/总市值亿[45]/市净率[46]）。
    备源：efinance 实时快照（动态市盈率 + 总市值，无 PB）。
    说明：这是"今天"的截面快照；教学先演示方法，第3章起再扩展时变基本面。
    """
    import time
    if codes is None:
        return pd.DataFrame(columns=["stock", "trade_date", "pb", "pe", "total_mv"])
    today = pd.Timestamp.today().strftime("%Y-%m-%d")
    rows = []
    for code in codes:
        try:
            symbol = _prefix(code)
            url = f"https://qt.gtimg.cn/q={symbol}"
            with urllib.request.urlopen(url, timeout=8) as r:
                txt = r.read().decode("gbk")
            f = txt.split("~")
            if len(f) < 47:
                raise ValueError("字段不足")
            pb = float(f[46])
            pe = float(f[39]) if f[39].strip() else float("nan")
            mv = float(f[45]) * 1e8  # 亿 → 元
            if pb > 0 and mv > 0:
                rows.append({"stock": code, "trade_date": today, "pb": pb,
                             "pe": pe, "total_mv": mv})
        except Exception:  # noqa: BLE001 —— 单只失败跳过
            continue
        time.sleep(0.05)
    if len(rows) >= 30:
        if verbose:
            print(f"[tencent-realtime] 快照 {len(rows)}/{len(codes)} 行")
        return pd.DataFrame(rows)
    # 备源：efinance 实时（无 PB，pb 置 NaN）
    try:
        import efinance as ef
        df = ef.stock.get_realtime_quotes()
        out = pd.DataFrame({
            "stock": df["股票代码"].astype(str).str.zfill(6),
            "pb": float("nan"),
            "pe": pd.to_numeric(df["动态市盈率"], errors="coerce"),
            "total_mv": pd.to_numeric(df["总市值"], errors="coerce"),
        }).dropna(subset=["pe", "total_mv"])
        out["trade_date"] = today
        if verbose:
            print(f"[efinance-realtime] 备源快照 {len(out)} 行")
        return out[["stock", "trade_date", "pb", "pe", "total_mv"]]
    except Exception as exc:  # noqa: BLE001
        raise RuntimeError(f"基本面快照全部失败: {exc}")


if __name__ == "__main__":
    df = fetch_daily("600519", "2023-01-01", "2023-12-31", verbose=True)
    print(df[["date", "close", "volume"]].tail(3))
