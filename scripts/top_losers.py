"""
Top Losers Report
-----------------
Fetches the day's top losing S&P 500 stocks from Yahoo Finance using yfinance Screener,
runs down-day correlation analysis on the top 3 losers,
then writes a combined Markdown report to docs/README.md.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime
import pytz
import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ── S&P 500 data ────────────────────────────────────────────────────────────

def fetch_sp500_info() -> dict[str, dict]:
    """從 GitHub CSV 取得 S&P 500 成分股，回傳 {symbol: {sector, name}}。"""
    url = "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv"
    df = pd.read_csv(url)
    df["Symbol"] = df["Symbol"].str.replace(".", "-", regex=False)
    info = {
        row["Symbol"]: {"sector": row["GICS Sector"], "name": row["Security"]}
        for _, row in df.iterrows()
    }
    print(f"S&P 500 symbols loaded: {len(info)}")
    return info


# ── Top Losers ───────────────────────────────────────────────────────────────

def fetch_top_losers(sp500: dict[str, dict], count: int = 100) -> list[dict]:
    """從 day_losers 篩選出屬於 S&P 500 的股票。"""
    response = yf.screen("day_losers", count=count)
    quotes = response.get("quotes", [])

    results = []
    for q in quotes:
        symbol = q.get("symbol", "")
        if symbol not in sp500:
            continue
        results.append({
            "symbol":     symbol,
            "name":       q.get("shortName") or q.get("longName", ""),
            "sector":     sp500[symbol]["sector"],
            "price":      q.get("regularMarketPrice"),
            "change_pct": q.get("regularMarketChangePercent"),
            "volume":     q.get("regularMarketVolume"),
            "exchange":   q.get("exchange", ""),
        })
    return results


# ── Notte API ────────────────────────────────────────────────────────────────

_EXCHANGE_MAP = {
    "NMS": "NASDAQ", "NGM": "NASDAQ", "NCM": "NASDAQ",
    "NYQ": "NYSE",   "NYS": "NYSE",
}

NOTTE_FUNCTION_ID = "2d050d7c-8984-4632-8390-3c2bdf194f7c"
NOTTE_URL = f"https://us-prod.notte.cc/functions/{NOTTE_FUNCTION_ID}/runs/start"


def to_tv_symbol(symbol: str, exchange: str) -> str | None:
    prefix = _EXCHANGE_MAP.get(exchange)
    return f"{prefix}:{symbol}" if prefix else None


def fetch_notte_snapshot(tv_symbol: str, api_key: str, news_count: int = 5) -> dict | None:
    import requests
    try:
        resp = requests.post(NOTTE_URL, json={
            "function_id": NOTTE_FUNCTION_ID,
            "variables": {"symbol": tv_symbol, "news_count": news_count},
        }, headers={
            "x-notte-api-key": api_key,
            "Authorization":   f"Bearer {api_key}",
        }, timeout=30)
        data = resp.json()
        if data.get("status") == "failed":
            print(f"  Notte failed for {tv_symbol}: {str(data.get('result', ''))[:80]}")
            return None
        return data.get("result")
    except Exception as e:
        print(f"  Notte error for {tv_symbol}: {e}")
        return None


# ── Correlation Analysis ─────────────────────────────────────────────────────

def analyze_down_day_correlation(
    symbol: str,
    sector: str,
    sp500: dict[str, dict],
    lookback: str = "6mo",
    top_n: int = 8,
) -> list[dict]:
    """
    找出當 symbol 下跌時同步下跌最多的 S&P 500 股票。
    方法：計算 symbol 下跌日（報酬 < -0.5%）時，同業的平均報酬。
    """
    # 同產業股票作為分析宇集
    peers = [s for s, v in sp500.items() if v["sector"] == sector and s != symbol]
    if not peers:
        return []

    # 下載目標股票歷史
    target_raw = yf.download(symbol, period=lookback, auto_adjust=True, progress=False)
    if target_raw.empty:
        return []

    target_close = target_raw["Close"]
    if isinstance(target_close, pd.DataFrame):
        target_close = target_close.iloc[:, 0]
    target_returns = target_close.pct_change().dropna()

    # 找出下跌日（跌幅 > 0.5%）
    down_days = target_returns[target_returns < -0.005].index
    if len(down_days) < 5:
        return []

    # 批次下載同業歷史（限 50 支避免 rate limit）
    peers_batch = peers[:50]
    peers_raw = yf.download(peers_batch, period=lookback, auto_adjust=True, progress=False)
    if peers_raw.empty:
        return []

    peers_close = peers_raw["Close"]
    if isinstance(peers_close, pd.Series):
        peers_close = peers_close.to_frame()

    peers_returns = peers_close.pct_change().dropna()

    # 取交集日期，計算下跌日平均報酬
    common_days = down_days.intersection(peers_returns.index)
    if len(common_days) < 3:
        return []

    avg_on_down = peers_returns.loc[common_days].mean().sort_values()

    # 計算整體 Pearson 相關係數
    results = []
    for peer_symbol in avg_on_down.index[:top_n]:
        peer_series = peers_returns[peer_symbol].dropna()
        common = target_returns.index.intersection(peer_series.index)
        corr = target_returns.loc[common].corr(peer_series.loc[common])
        results.append({
            "symbol":       peer_symbol,
            "name":         sp500.get(peer_symbol, {}).get("name", ""),
            "avg_down_ret": avg_on_down[peer_symbol],
            "correlation":  corr,
        })

    return results


# ── Formatters ───────────────────────────────────────────────────────────────

def fmt_symbol(symbol: str) -> str:
    url = f"https://www.moneydj.com/us/basic/basic0001/{symbol}"
    return f"[**{symbol}**]({url})"


def fmt_price(v) -> str:
    return f"${v:,.2f}" if v is not None else "—"


def fmt_pct(v) -> str:
    if v is None:
        return "—"
    if v < 0:
        return f'<span style="color:#e74c3c;white-space:nowrap">▼ {abs(v):.2f}%</span>'
    return f'<span style="color:#27ae60;white-space:nowrap">▲ {v:.2f}%</span>'


def fmt_ret(v) -> str:
    if v is None:
        return "—"
    pct = v * 100
    if pct < 0:
        return f'<span style="color:#e74c3c;white-space:nowrap">{pct:.2f}%</span>'
    return f'<span style="color:#27ae60;white-space:nowrap">+{pct:.2f}%</span>'


def fmt_corr(v) -> str:
    if v is None or pd.isna(v):
        return "—"
    return f"{v:.3f}"


def fmt_volume(v) -> str:
    if v is None:
        return "—"
    if v >= 1_000_000:
        return f"{v / 1_000_000:.1f}M"
    if v >= 1_000:
        return f"{v / 1_000:.1f}K"
    return str(v)


# ── Report Builder ───────────────────────────────────────────────────────────

def fmt_recommendation(rec: str, score_str: str) -> str:
    rec_lower = rec.lower()
    if "strong buy" in rec_lower or rec_lower == "buy":
        color = "#27ae60"
    elif "strong sell" in rec_lower or rec_lower == "sell":
        color = "#e74c3c"
    else:
        color = "#888888"
    return f'<span style="color:{color};font-weight:bold">{rec}</span> ({score_str})'


def fmt_notte_block(snap: dict, symbol: str = "", company: str = "") -> list[str]:
    tech  = snap.get("technical", {})
    perf  = snap.get("performance", {})
    fund  = snap.get("fundamentals", {})
    quote = snap.get("quote", {})
    news  = snap.get("news", [])

    rec       = tech.get("recommendation", "—")
    score     = tech.get("recommendation_score")
    score_str = f"{score:+.2f}" if score is not None else "—"
    rec_fmt   = fmt_recommendation(rec, score_str)

    ytd    = perf.get("ytd")
    w1     = perf.get("1_week")
    m1     = perf.get("1_month")
    m3     = perf.get("3_months")
    pe     = fund.get("pe_ratio")
    mktcap = quote.get("market_cap")

    pe_str     = f"{pe:.1f}" if pe else "—"
    mktcap_str = (
        f"${mktcap/1e12:.2f}T" if mktcap and mktcap >= 1e12 else
        f"${mktcap/1e9:.1f}B"  if mktcap and mktcap >= 1e9  else "—"
    )

    lines = [
        "| 技術建議 | 本益比(PE) | 市值 | 1W | 1M | 3M | YTD |",
        "|----------|-----------|------|-----|-----|-----|-----|",
        f"| {rec_fmt} | {pe_str} | {mktcap_str} "
        f"| {fmt_ret(w1/100 if w1 else None)} "
        f"| {fmt_ret(m1/100 if m1 else None)} "
        f"| {fmt_ret(m3/100 if m3 else None)} "
        f"| {fmt_ret(ytd/100 if ytd else None)} |",
    ]
    keywords = [k.lower() for k in [symbol, company] if k]
    relevant_news = [
        item for item in news
        if any(kw in item.get("title", "").lower() for kw in keywords)
    ]
    if relevant_news:
        lines += ["", "**最新新聞**", ""]
        for item in relevant_news:
            lines.append(f"- 📰 {item.get('title', '')}")
    return lines


def build_report(losers: list[dict], correlations: dict[str, list[dict]], sp500: dict[str, dict], notte_data: dict[str, dict] | None = None) -> str:
    et = pytz.timezone("America/New_York")
    now_et = datetime.now(et)
    now_utc = datetime.now(pytz.utc)

    lines = [
        "# 美股當日跌幅榜",
        "",
        f"> 更新時間：{now_et.strftime('%Y-%m-%d %H:%M')} ET"
        f"（{now_utc.strftime('%H:%M')} UTC）",
        "",
        "## S&P 500 Top Losers",
        "",
        "| # | 代碼 | 公司名稱 | 產業 | 現價 | 跌幅 | 成交量 |",
        "|---|------|----------|------|------|------|--------|",
    ]

    for i, s in enumerate(losers, 1):
        lines.append(
            f"| {i} | {fmt_symbol(s['symbol'])} | {s['name']} "
            f"| {s['sector']} "
            f"| **{fmt_price(s['price'])}** "
            f"| {fmt_pct(s['change_pct'])} "
            f"| {fmt_volume(s['volume'])} |"
        )

    # 前 3 名相關性分析
    for s in losers[:3]:
        sym = s["symbol"]
        peers = correlations.get(sym, [])

        lines += [
            "",
            f"### {sym} 下跌時的同步股分析",
            "",
        ]

        snap = (notte_data or {}).get(sym)
        if snap:
            lines += fmt_notte_block(snap, symbol=sym, company=s["name"])
            lines.append("")

        lines += [
            f"> 以過去 6 個月中 **{sym}** 單日跌幅逾 0.5% 的交易日為基準，"
            f"統計同產業（{s['sector']}）各股的平均報酬與相關係數。",
            "",
        ]

        if not peers:
            lines.append("*資料不足，無法計算。*")
            continue

        lines += [
            "| 代碼 | 公司名稱 | 產業 | 下跌日平均報酬 | 相關係數 |",
            "|------|----------|------|----------------|----------|",
        ]
        for p in peers:
            sector = sp500.get(p['symbol'], {}).get("sector", "—")
            lines.append(
                f"| {fmt_symbol(p['symbol'])} | {p['name']} "
                f"| {sector} "
                f"| {fmt_ret(p['avg_down_ret'])} "
                f"| {fmt_corr(p['correlation'])} |"
            )

    lines += [
        "",
        "---",
        "",
        f"*資料來源：Yahoo Finance（via yfinance）。"
        f"自動產生於 {now_et.strftime('%Y-%m-%d %H:%M')} ET，僅供參考，不構成投資建議。*",
    ]

    return "\n".join(lines)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("Fetching S&P 500 info...")
    sp500 = fetch_sp500_info()

    print("Fetching top losers...")
    losers = fetch_top_losers(sp500=sp500, count=100)

    if not losers:
        print("No data returned from screener.")
        return

    print(f"Got {len(losers)} S&P 500 losers.")

    # 對前 3 名跑相關性分析
    correlations: dict[str, list[dict]] = {}
    for s in losers[:3]:
        sym = s["symbol"]
        print(f"Analyzing down-day correlation for {sym}...")
        correlations[sym] = analyze_down_day_correlation(
            symbol=sym,
            sector=s["sector"],
            sp500=sp500,
        )

    # Notte 快照（需要 NOTTE_API_KEY）
    notte_data: dict[str, dict] = {}
    notte_key = os.environ.get("NOTTE_API_KEY")
    if notte_key:
        for s in losers[:3]:
            sym = s["symbol"]
            tv_symbol = to_tv_symbol(sym, s["exchange"])
            if not tv_symbol:
                print(f"  Skipping Notte for {sym}: unknown exchange {s['exchange']!r}")
                continue
            print(f"Fetching Notte snapshot for {tv_symbol}...")
            snap = fetch_notte_snapshot(tv_symbol, notte_key)
            if snap:
                notte_data[sym] = snap
    else:
        print("NOTTE_API_KEY not set, skipping Notte snapshots.")

    report = build_report(losers, correlations, sp500, notte_data)

    output_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "docs", "README.md")
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Report written to {output_path}")


if __name__ == "__main__":
    main()
