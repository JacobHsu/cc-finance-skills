# yfinance-data

[English](README.md) | [繁體中文](README.zh-TW.md)

透過 [yfinance](https://github.com/ranaroussi/yfinance) Python 套件取得金融與市場資料。

## 功能說明

從 Yahoo Finance 擷取各類金融資料，包含：

- **即時報價** — 股票現價、市值、本益比
- **歷史 OHLCV** — 可自訂時間區間與頻率的價格歷史資料
- **財務報表** — 資產負債表、損益表、現金流量表（年報與季報）
- **企業行動** — 股利、股票分割
- **選擇權資料** — 完整選擇權鏈含 Greeks 值
- **分析資料** — 盈餘歷史、分析師目標價、評等、升降評
- **持股結構** — 機構持股、內部人交易
- **股票篩選** — 透過 `yf.Screener` 與 `yf.EquityQuery` 篩選股票

> **注意**：yfinance 與 Yahoo, Inc. 無關聯。資料僅供研究與教育用途。

## 觸發時機

- 提及任何股票代碼（AAPL、MSFT、TSLA、2330 等）
- 「現在股價是多少」、「幫我查財務報表」、「顯示盈餘」
- 「選擇權鏈」、「股利歷史」、「資產負債表」、「損益表」
- 「分析師目標價」、「比較股票」、「篩選股票」

## 前置需求

- Python 3.8+
- 技能會在未安裝時自動透過 pip 安裝 `yfinance`

## 支援平台

適用於**所有平台**（Claude Code、Claude.ai 含程式碼執行功能等）。

## 安裝

```bash
npx skills add JacobHsu/cc-finance-skills --skill yfinance-data
```

更多安裝方式請參閱 [主 README](../../README.md)。

## 參考文件

- `references/api_reference.md` — 完整 yfinance API 參考，含每個資料類別的程式碼範例
