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
