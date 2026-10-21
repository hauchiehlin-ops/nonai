# NonAI - AI 數位指紋與隱藏痕跡消除系統

> 針對 TXT、Markdown、DOCX、PDF 等多種檔案格式與剪貼簿，全面消除 AI 統計型浮水印、隱形 Unicode 字元、DOCX 缺乏 RSID 編輯軌跡、網頁 CSS 幽靈樣式與軟體元資料。

---

## 🌟 核心解決的 6 大 AI 殘留問題

| # | 殘留特徵 | 影響格式 | NonAI 解決技術 |
|---|---|---|---|
| 1 | **隱形 Unicode 字元** | TXT / MD / DOCX / PDF | 智慧檢測並剔除零寬度字元（ZWSP `\u200B`、ZWNJ `\u200C`、BOM `\uFEFF` 等），並執行標準化 NFC 校驗。 |
| 2 | **網頁 CSS / HTML 殘留** | DOCX / 剪貼簿 | 清除複製自 ChatGPT/Claude 對話框時夾帶的特徵底色（`<w:shd w:fill="F7F7F8"/>`）與網頁字體（Inter/Söhne）。 |
| 3 | **缺乏 RSID 編輯軌跡** | DOCX | **獨創 RSID 仿生注入演算法**：逆向注入 20~40 組 Microsoft Word 會話池、碎形化切割文字 Runs（模擬打字與停頓歷程），並同步於 `settings.xml` 與 `app.xml` 偽裝合理編輯耗時。 |
| 4 | **軟體元資料暴露** | PDF / DOCX | 抹除 `python-docx` / `pdf-lib` / `Chromium` 標籤，偽裝為 `Microsoft Office Word 16.0000` 或 `macOS Quartz PDFContext`，徹底清空 XMP 隱藏資料流。 |
| 5 | **Markdown 結構過度完美** | MD | 打破 LLM 機械式空格對齊表格、自然化多層級清單標記與段落空行。 |
| 6 | **統計型浮水印 (SynthID)** | 跨格式文字 | 提供 **n-gram 擾動與轉折詞微調**，打破 AI 高頻套話（如「值得注意的是」、「總結來說」），瓦解偵測演算法的 z-score 顯著性。 |

---

## 🚀 快速啟動

### 1. 方案 A：Web 視覺化工作台 (瀏覽器介面)

一鍵啟動現代化 Web 工作台，支援檔案拖曳清洗、即時文字框鑑識與下載：

```bash
# 啟動 Web 服務
./.venv/bin/python run_web.py
```
👉 開啟瀏覽器訪問：**http://127.0.0.1:8765**

---

### 2. 方案 C：系統剪貼簿即時守護程式 (Clipboard Watcher)

常駐於 macOS 後台，當您在 ChatGPT、Claude 按下「複製」時，**自動在記憶體中淨化文字**，剔除所有零寬字元並抹平 HTML 幽靈樣式：

```bash
# 啟動剪貼簿守護
./.venv/bin/python run_clipboard.py

# 亦可附帶開啟統計浮水印輕量擾動：
./.venv/bin/python run_clipboard.py --perturb
```

> 💡 **提示**：您也可以直接在 Web 工作台右上角點擊「**啟動守護**」，無需開多個終端視窗即可在後台進行監聽與活動日誌追蹤！

---

### 3. CLI 命令列工具

```bash
# 清洗 Word 檔 (自動注入 RSID、偽裝微軟作者與編輯時間)
./.venv/bin/python nonai/cli.py clean my_document.docx

# 清洗 PDF 檔 (偽裝為 macOS Quartz Context，清空 XMP)
./.venv/bin/python nonai/cli.py clean report.pdf --spoof macOS

# 鑑識分析檔案中隱藏的 AI 痕跡
./.venv/bin/python nonai/cli.py inspect draft.txt
```

---

## 🧪 測試驗證

本專案附帶完整單元測試套件：

```bash
PYTHONPATH=. .venv/bin/python tests/test_unicode.py
PYTHONPATH=. .venv/bin/python tests/test_docx.py
PYTHONPATH=. .venv/bin/python tests/test_pdf.py
PYTHONPATH=. .venv/bin/python tests/test_markdown.py
PYTHONPATH=. .venv/bin/python tests/test_clipboard.py
```

---

## 🔒 隱私與安全性
本系統為 **100% 本地完全離線運算**，無需上傳至任何雲端伺服器，您的任何檔案、剪貼簿與文字記錄皆只保留在您的本機電腦。
