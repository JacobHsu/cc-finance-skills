# Scripts

## top_losers.py

從 Yahoo Finance 抓取當日跌幅最大的美股，輸出 Markdown 報告至 `docs/README.md`。

### 安裝依賴

```bash
pip install yfinance pytz pandas lxml
```

### 本地執行

在專案根目錄下執行：

```bash
python scripts/top_losers.py
```

執行完成後開啟 `docs/README.md` 查看報告。

### 自動排程

GitHub Actions 每個交易日 15:00 UTC（美東 10:00 AM EST）自動執行，
結果 commit 回 `docs/README.md`，並透過 `index.html`（Docsify）顯示。

---

## hormuz_report.py

從 [Hormuz Strait Monitor](https://hormuzstraitmonitor.com) API 抓取荷姆茲海峽即時狀態，輸出 Markdown 報告至 `docs/hormuz.md`。

### 安裝依賴

```bash
pip install deep-translator
```

> `deep-translator` 使用 Google 非官方免費介面，**不需要 API key**。
> 翻譯失敗時自動退回英文原文，不影響報告產生。

### 翻譯欄位

| 欄位 | 說明 |
|------|------|
| 海峽狀態說明 | `straitStatus.description` |
| 外交頭條 / 摘要 | `diplomacy.headline` / `summary` |
| LNG 說明 | `lngImpact.description` |
| 危機時間軸 | `crisisTimeline.events[].title` / `description` |
| 新聞標題 | `news[].title` |
| 替代航線名稱 / 使用狀況 | `alternativeRoutes[].name` / `currentUsageStatus` |
| 主要供應鏈事件 | `supplyChainImpact.keyDisruptions[]` |

數字、狀態碼（OPEN / RESTRICTED）、地名保留英文原文。

### 本地執行

在專案根目錄下執行：

```bash
python scripts/hormuz_report.py
```

執行完成後開啟 `docs/hormuz.md` 查看報告。

### 本地預覽（Docsify）

需先安裝 [docsify-cli](https://docsify.js.org/#/quickstart)：

```bash
npm i docsify-cli -g
```

在專案根目錄啟動本地伺服器：

```bash
docsify serve .
```

瀏覽器開啟 http://localhost:3000 即可看到完整報告網站。

### 自動排程

GitHub Actions 每天 06:00 / 12:00 / 18:00 UTC 自動執行，
結果 commit 回 `docs/hormuz.md`，並透過 `index.html`（Docsify）顯示。

---

## banini_report.py

抓取 Threads @banini31 的近期貼文，輸出原始貼文紀錄至 `docs/banini.md`。

### 安裝依賴

```bash
pip install playwright parsel nested-lookup jmespath
playwright install chromium
```

> 使用本地無頭 Chromium 攔截 Threads GraphQL 回應，**不需要任何 API key**。

### 本地執行

在專案根目錄下執行：

```bash
python scripts/banini_report.py
```

可指定帳號與捲動次數（捲動越多抓越多篇）：

```bash
python scripts/banini_report.py banini31 5
```

執行完成後開啟 `docs/banini.md` 查看報告。

### 輸出格式

每篇貼文包含：時間（台北時間）、原文、讚數、回覆數、原文連結。
0 篇時程式以 exit code 1 結束，GitHub Actions 會標記 fail 並停止 commit。

### 自動排程

GitHub Actions 週一～五 13:00 台北時間（05:00 UTC）自動執行，
結果 commit 回 `docs/banini.md`，並透過 `index.html`（Docsify）顯示。

> **注意：** Threads 使用無頭 Chromium 爬取，在 GitHub Actions 的資料中心 IP 上
> 可能遭 Meta 反爬機制封鎖。請先用 `workflow_dispatch` 手動觸發一次確認可行性。
