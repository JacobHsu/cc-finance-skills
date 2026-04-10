# Finance Skills

[English](README.md) | [繁體中文](README.zh-TW.md)

> [!WARNING]
> 本專案僅供教育與資訊用途。此處內容不構成任何投資建議。投資前請自行研究並諮詢合格的財務顧問。

一套用於金融分析與交易的 Agent 技能集合。

範例截圖請參閱 [DEMOS.md](DEMOS.md)。

## 安裝

### 本地安裝（快速開始）

以 `banini` 為例，其他技能名稱替換即可。

**macOS / Linux：**

```bash
# 已在專案目錄內
cp -r skills/banini ~/.claude/skills/
```

```bash
# 從外部 clone
git clone https://github.com/JacobHsu/cc-finance-skills.git
cp -r cc-finance-skills/skills/banini ~/.claude/skills/
```

**Windows（PowerShell）：**

```powershell
# 已在專案目錄內
Copy-Item -Recurse skills\banini "$env:USERPROFILE\.claude\skills\"
```

```powershell
# 從外部 clone
git clone https://github.com/JacobHsu/cc-finance-skills.git
Copy-Item -Recurse cc-finance-skills\skills\banini "$env:USERPROFILE\.claude\skills\"
```

> **專案本地安裝：** 若只想在特定專案使用，將目的地改為 `.claude/skills/`（專案根目錄下）。

---

### Claude Code Plugin（推薦）

本專案為 [Claude Code plugin](https://code.claude.com/docs/en/plugins)，可直接安裝：

**方式 A — Plugin 市集**

```bash
# 新增市集來源
/plugin marketplace add JacobHsu/cc-finance-skills

# 安裝 plugin
/plugin install finance-skills@cc-finance-skills
```

**方式 B — 本地開發安裝**

```bash
claude --plugin-dir ./path/to/finance-skills
```

安裝後，技能會以 `finance-skills:` 為命名空間（例如 `/finance-skills:options-payoff`）。

### Claude Code（Agent Skills）

**方式 A — `npx skills add`**

```bash
npx skills add JacobHsu/cc-finance-skills
```

安裝特定技能：

```bash
npx skills add JacobHsu/cc-finance-skills --skill options-payoff
```

全域安裝（所有專案皆可使用）：

```bash
npx skills add JacobHsu/cc-finance-skills --skill options-payoff -g
```

**方式 B — 手動安裝**

Clone 後將技能複製到 Claude Code skills 目錄：

```bash
# 個人全域（所有專案）
cp -r skills/options-payoff ~/.claude/skills/options-payoff

# 專案本地（僅此專案）
cp -r skills/options-payoff .claude/skills/options-payoff
```

### Claude.ai（網頁 / 桌面版）

1. 前往 **Settings > Capabilities**，啟用 **Code execution and file creation**
2. 從 [最新 Release](https://github.com/JacobHsu/cc-finance-skills/releases/latest) 下載所需技能的 zip（例如 `options-payoff.zip`）
3. 在 Claude 中前往 **Customize > Skills**
4. 點擊 **+** 按鈕，選擇 **Upload a skill**
5. 選取 zip 檔案，技能即會出現在清單中

每個技能重複步驟 2–5。

### 其他 Agent

本專案遵循 [Agent Skills](https://agentskills.io) 開放標準，可安裝至任何支援的 Agent（Codex、Gemini CLI、GitHub Copilot 等）：

```bash
npx skills add JacobHsu/cc-finance-skills -a <agent-name>
```

## 可用技能

### 分析與資料

| 技能 | 說明 | 支援平台 |
|---|---|---|
| [stock-correlation](skills/stock-correlation/) | 分析股票相關性，尋找關聯企業、同業競爭者與配對交易候選標的。包含共移發現、報酬相關性、產業分群、已實現相關性等子技能。 | 所有平台 |
| [yfinance-data](skills/yfinance-data/) | 透過 yfinance 取得金融市場資料，包含股價、OHLCV 歷史、財務報表、選擇權鏈、股利、盈餘、分析師評等、篩選器等。 | 所有平台 |

### 地緣政治與總體風險

| 技能 | 說明 | 支援平台 |
|---|---|---|
| [hormuz-strait](skills/hormuz-strait/) | 即時霍爾木茲海峽監控，涵蓋船運通行、油價衝擊、受困船隻、保險風險、外交動態、全球貿易影響與危機時間軸。 | 所有平台 |

## Scripts

| 腳本 | 說明 |
|------|------|
| [scripts/top_losers.py](scripts/top_losers.py) | 抓取當日美股跌幅榜，輸出至 `docs/README.md` |

詳見 [scripts/README.md](scripts/README.md)。

## 參考

[kc_ai_skills](https://github.com/KerberosClaw/kc_ai_skills/tree/main)  banini

## 授權

MIT

基於 [himself65/finance-skills](https://github.com/himself65/finance-skills) by himself65。
