# stock-correlation

[English](README.md) | [繁體中文](README.zh-TW.md)

分析股票相關性，透過歷史價格資料找出關聯企業、同業競爭者與配對交易候選標的。

## 功能說明

根據使用者意圖自動路由至四個專屬子技能：

- **共移發現（Co-movement Discovery）** — 給定單一代碼，從精選的產業與主題同業中找出相關性最高的股票（例如：「哪些股票和 NVDA 相關？」）
- **報酬相關性（Return Correlation）** — 對兩支股票進行深入的配對分析，包含 Pearson 相關係數、Beta、R²、價差 Z-score 及滾動穩定性（例如：「AMD 和 NVDA 的相關性」）
- **產業分群（Sector Clustering）** — 建立完整的 NxN 相關矩陣並進行階層式分群，識別群組與離群值（例如：「FAANG 的相關矩陣」）
- **已實現相關性（Realized Correlation）** — 時變與情境條件相關性分析：滾動窗口（20/60/120 日）、上漲與下跌日、高波動與低波動、回撤情境（例如：「NVDA 下跌時哪些股票也跟著跌？」）

## 觸發時機

- 「哪些股票和 NVDA 相關」、「找和 AMD 相關的股票」
- 「AAPL 和 MSFT 的相關性」、「LITE 和 COHR 怎麼一起動」
- 「什麼跟著一起動」、「同步漲跌的股票」、「sympathhy plays」
- 「同業」、「配對交易」、「對沖配對」
- 「NVDA 跌的時候什麼也跌」、「滾動相關性」
- 「FAANG 相關矩陣」、「幫我把這些股票分群」
- 知名配對：AMD/NVDA、GOOGL/AVGO、LITE/COHR

## 前置需求

- Python 3.8+
- 技能會在未安裝時自動透過 pip 安裝 `yfinance`、`pandas`、`numpy`
- `scipy` 為選用（用於產業分群子技能的階層式分群；若未安裝則改以排序方式呈現）

## 支援平台

適用於**所有平台**（Claude Code、Claude.ai 含程式碼執行功能等）。

## 安裝

```bash
npx skills add JacobHsu/cc-finance-skills --skill stock-correlation
```

更多安裝方式請參閱 [主 README](../../README.md)。

## 參考文件

- `references/sector_universes.md` — 使用 yfinance Screener API 動態建構同業宇集，含備援策略說明
