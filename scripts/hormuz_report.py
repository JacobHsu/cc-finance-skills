"""
Hormuz Strait Monitor Report
-----------------------------
Fetches real-time status from hormuzstraitmonitor.com/api/dashboard
and writes a Markdown briefing to docs/hormuz.md.
"""

import json
import os
import time
import urllib.request
from datetime import datetime, timezone, timedelta

try:
    from deep_translator import GoogleTranslator
    _translator = GoogleTranslator(source="en", target="zh-TW")
    TRANSLATE_ENABLED = True
except ImportError:
    TRANSLATE_ENABLED = False


def t(text: str) -> str:
    """翻譯英文為繁體中文，失敗時原文回傳。"""
    if not TRANSLATE_ENABLED or not text or not text.strip():
        return text
    try:
        # Google 非官方 API 單次上限 5000 字元
        chunk = text[:4900]
        result = _translator.translate(chunk)
        time.sleep(0.3)  # 避免過快被限速
        return result or text
    except Exception:
        return text


API_URL = "https://hormuzstraitmonitor.com/api/dashboard"
TW_TZ = timezone(timedelta(hours=8))

RISK_COLORS = {
    "normal":   "#27ae60",
    "elevated": "#f39c12",
    "high":     "#e67e22",
    "critical": "#e74c3c",
    "extreme":  "#8e44ad",
}

RISK_LABELS = {
    "normal":   "正常 — 航運正常運作",
    "elevated": "偏高 — 需密切關注",
    "high":     "高風險 — 存在明顯干擾",
    "critical": "嚴重 — 嚴重影響全球石油供應",
    "extreme":  "極端 — 海峽實質封閉，危機升溫",
}


def fetch_dashboard() -> dict:
    req = urllib.request.Request(API_URL, headers={"User-Agent": "hormuz-report/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = json.loads(resp.read().decode())
    if not raw.get("success"):
        raise RuntimeError("API returned success=false")
    return raw["data"]


def fmt_change(v, unit: str = "") -> str:
    if v is None:
        return "—"
    sign = "+" if v > 0 else ""
    color = "#e74c3c" if v < 0 else "#27ae60"
    return f'<span style="color:{color}">{sign}{v:.2f}{unit}</span>'


def fmt_pct_of_normal(v) -> str:
    if v is None:
        return "—"
    color = "#e74c3c" if v < 80 else ("#f39c12" if v < 95 else "#27ae60")
    flag = " ⚠️" if v < 80 else (" ▲" if v > 120 else "")
    return f'<span style="color:{color}">{v:.1f}%{flag}</span>'


def fmt_risk_level(level: str) -> str:
    key = level.lower()
    color = RISK_COLORS.get(key, "#888888")
    label = RISK_LABELS.get(key, level)
    return f'<span style="color:{color};font-weight:bold">{level.upper()}</span> — {label}'


def fmt_usd(v) -> str:
    if v is None:
        return "—"
    if v >= 1_000_000:
        return f"${v / 1_000_000:.1f}M"
    if v >= 1_000:
        return f"${v / 1_000:,.0f}K"
    return f"${v:,.0f}"


def build_report(data: dict) -> str:
    now_tw = datetime.now(TW_TZ)

    strait    = data.get("straitStatus", {})
    ships     = data.get("shipCount", {})
    oil       = data.get("oilPrice", {})
    stranded  = data.get("strandedVessels", {})
    ins       = data.get("insurance", {})
    thru      = data.get("throughput", {})
    diplo     = data.get("diplomacy", {})
    trade     = data.get("globalTradeImpact", {})
    timeline  = data.get("crisisTimeline", {}).get("events", [])
    news_list = data.get("news", [])
    last_upd_raw = data.get("lastUpdated", "")
    try:
        last_upd_dt = datetime.fromisoformat(last_upd_raw.replace("Z", "+00:00"))
        last_upd = last_upd_dt.astimezone(TW_TZ).strftime("%Y-%m-%d %H:%M")
    except Exception:
        last_upd = last_upd_raw or "—"

    status_val   = strait.get("status", "UNKNOWN")
    status_color = "#27ae60" if status_val == "OPEN" else "#e74c3c"
    status_fmt   = f'<span style="color:{status_color};font-weight:bold">{status_val}</span>'

    ins_level = ins.get("level", "normal")

    brent   = oil.get("brentPrice")
    chg24h  = oil.get("change24h")
    chg_pct = oil.get("changePercent24h")

    sparkline = oil.get("sparkline", [])
    if len(sparkline) >= 2:
        trend = "上升" if sparkline[-1] > sparkline[0] else ("下跌" if sparkline[-1] < sparkline[0] else "持平")
    else:
        trend = "—"

    thru_7d = thru.get("last7Days", [])
    if len(thru_7d) >= 2:
        thru_trend = "上升" if thru_7d[-1] > thru_7d[0] else ("下跌" if thru_7d[-1] < thru_7d[0] else "持平")
    else:
        thru_trend = "—"

    lines = [
        "# 荷姆茲海峽即時監控報告",
        "",
        f"> 更新時間：{now_tw.strftime('%Y-%m-%d %H:%M')} 台灣時間　｜　資料更新：{last_upd} 台灣時間",
        "",
        "---",
        "",
        "## 海峽狀態",
        "",
        "| 狀態 | 持續自 | 說明 |",
        "|------|--------|------|",
        f"| {status_fmt} | {strait.get('since', '—')} | {t(strait.get('description', '—'))} |",
        "",
        "## 船舶流量",
        "",
        "| 當前過境 | 過去 24h | 正常日均 | 佔正常比 |",
        "|----------|----------|----------|----------|",
        f"| {ships.get('currentTransits', '—')} | {ships.get('last24h', '—')} "
        f"| {ships.get('normalDaily', '—')} | {fmt_pct_of_normal(ships.get('percentOfNormal'))} |",
        "",
        "## 油價",
        "",
        "| 布蘭特原油 | 24h 變動 | 24h 漲跌幅 | 近期趨勢 |",
        "|-----------|---------|-----------|---------|",
        f"| **${brent:.2f}** | {fmt_change(chg24h)} | {fmt_change(chg_pct, '%')} | {trend} |",
        "",
        "## 被困船隻",
        "",
        "| 總計 | 油輪 | 散裝 | 其他 | 今日變化 |",
        "|------|------|------|------|----------|",
        f"| **{stranded.get('total', '—')}** | {stranded.get('tankers', '—')} "
        f"| {stranded.get('bulk', '—')} | {stranded.get('other', '—')} "
        f"| {fmt_change(stranded.get('changeToday'))} |",
        "",
        "## 保險風險",
        "",
        f"風險等級：{fmt_risk_level(ins_level)}",
        "",
        "| 戰爭風險溢價 | 正常溢價 | 倍數 |",
        "|-------------|---------|------|",
        f"| {ins.get('warRiskPercent', '—')}% | {ins.get('normalPercent', '—')}% "
        f"| {ins.get('multiplier', '—')}x |",
        "",
        "## 貨物吞吐量",
        "",
        "| 今日 DWT | 平均 DWT | 佔正常比 | 7日趨勢 |",
        "|---------|---------|---------|---------|",
        f"| {thru.get('todayDWT', '—'):,} | {thru.get('averageDWT', '—'):,} "
        f"| {fmt_pct_of_normal(thru.get('percentOfNormal'))} | {thru_trend} |",
        "",
        "## 外交情勢",
        "",
        f"**狀態：** {diplo.get('status', '—')}",
        "",
        f"**頭條：** {t(diplo.get('headline', '—'))}",
        "",
        f"**各方：** {', '.join(diplo.get('parties', []))}",
        "",
        f"> {t(diplo.get('summary', '—'))}",
        "",
        "## 全球貿易影響",
        "",
        f"| 全球石油佔比 | 每日潛在損失 |",
        f"|-------------|-------------|",
        f"| {trade.get('percentOfWorldOilAtRisk', '—')}% "
        f"| ${trade.get('estimatedDailyCostBillions', '—')}B |",
        "",
    ]

    # LNG 影響
    lng = trade.get("lngImpact")
    if isinstance(lng, dict):
        importers = ", ".join(lng.get("topAffectedImporters", []))
        lines += [
            "**LNG 影響**",
            "",
            "| 全球 LNG 佔比 | 每日潛在損失 | 主要受影響進口國 |",
            "|--------------|-------------|----------------|",
            f"| {lng.get('percentOfWorldLngAtRisk', '—')}% "
            f"| ${lng.get('estimatedLngDailyCostBillions', '—')}B "
            f"| {importers} |",
            "",
        ]
        desc = lng.get("description", "")
        if desc:
            lines += [f"> {t(desc)}", ""]

    # 受影響地區
    regions = trade.get("affectedRegions", [])
    if regions:
        lines += [
            "**受影響地區**",
            "",
            "| 地區 | 嚴重程度 | 石油依賴度 |",
            "|------|---------|-----------|",
        ]
        for r in regions:
            name = r.get("name", "—")
            severity = r.get("severity", "—")
            dep = r.get("oilDependencyPercent")
            dep_str = f"{dep}%" if dep is not None else "—"
            lines.append(f"| {name} | {severity} | {dep_str} |")
        lines.append("")

    # 替代航線
    alt_routes = trade.get("alternativeRoutes", [])
    if alt_routes:
        lines += [
            "**替代航線**",
            "",
            "| 航線 | 額外天數 | 每船額外成本 | 使用狀況 |",
            "|------|---------|------------|---------|",
        ]
        for r in alt_routes:
            cost = r.get("additionalCostPerVessel")
            lines.append(
                f"| {t(r.get('name', '—'))} | +{r.get('additionalDays', '—')} 天 "
                f"| {fmt_usd(cost) if cost else '—'} "
                f"| {t(r.get('currentUsageStatus', '—'))} |"
            )
        lines.append("")

    # 供應鏈影響
    sc = trade.get("supplyChainImpact")
    if isinstance(sc, dict):
        lines += [
            "**供應鏈影響**",
            "",
            "| 運費漲幅 | 消費者物價衝擊 | 戰略儲備可用天數 |",
            "|---------|-------------|----------------|",
            f"| +{sc.get('shippingRateIncreasePercent', '—')}% "
            f"| +{sc.get('consumerPriceImpactPercent', '—')}% "
            f"| {sc.get('sprStatusDays', '—')} 天 |",
            "",
        ]
        disruptions = sc.get("keyDisruptions", [])
        if disruptions:
            lines += ["**主要供應鏈事件**", ""]
            for d in disruptions:
                lines.append(f"- {t(d)}")
            lines.append("")

    # 危機時間軸
    if timeline:
        lines += ["## 危機時間軸", ""]
        for ev in timeline[-10:]:
            etype = ev.get("type", "").upper()
            lines.append(f"**{ev.get('date', '—')}** `{etype}` — **{t(ev.get('title', ''))}**")
            lines.append(f"> {t(ev.get('description', ''))}")
            lines.append("")

    # 最新新聞
    if news_list:
        lines += ["## 最新新聞", ""]
        for item in news_list[:5]:
            url   = item.get("url", "#")
            title = item.get("title", "—")
            src   = item.get("source", "")
            pub   = item.get("publishedAt", "")[:10]
            lines.append(f"- [{t(title)}]({url})　*{src}・{pub}*")
        lines.append("")

    lines += [
        "---",
        "",
        "*資料來源：[Hormuz Strait Monitor](https://hormuzstraitmonitor.com)。"
        f"自動產生於 {now_tw.strftime('%Y-%m-%d %H:%M')} 台灣時間，僅供參考，不構成投資建議。*",
    ]

    return "\n".join(lines)


def main() -> None:
    print("Fetching Hormuz Strait dashboard...")
    data = fetch_dashboard()

    report = build_report(data)

    output_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), "..", "docs", "hormuz.md")
    )
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"Report written to {output_path}")


if __name__ == "__main__":
    main()
