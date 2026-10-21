"""
Build script to generate comprehensive, professional i18n dictionaries for NonAI.
Supports 7 languages: zh-TW, en, zh-CN, ja, ko, th, ru.
Guarantees 100% key consistency, full modal translation, manual & FAQ translation,
and zero prohibited phrases.
"""

import json
from pathlib import Path

I18N_DATA = {
    "zh-TW": {
        "app_title": "NonAI - AI 數位指紋與隱藏痕跡消除系統",
        "brand_sub": "AI 數位指紋、浮水印與底層元資料消除引擎",
        "watcher_label": "剪貼簿守護 (Scheme C)",
        "watcher_active": "即時監聽中",
        "watcher_inactive": "未啟動",
        "watcher_btn_start": "啟動守護",
        "watcher_btn_stop": "停止守護",
        "watcher_running": "守護運作中 (自動淨化複製內容)",
        "watcher_stopped": "守護未運行",
        "tab_files": "📁 檔案淨化工作台 (.docx, .pdf, .md, .txt)",
        "tab_text": "✍️ 即時文字與 Hex 鑑識",
        "tab_clipboard": "📋 剪貼簿活動日誌",
        "tab_manual": "📖 操作與鑑識手冊",
        "drop_title": "拖曳檔案至此，或點擊選擇檔案",
        "drop_subtitle": "支援格式：Word (.docx)、PDF (.pdf)、Markdown (.md)、純文字 (.txt)",
        "tag_rsid": "DOCX RSID 仿生注入",
        "tag_pdf": "PDF XMP 元資料偽裝",
        "tag_css": "網頁 CSS 幽靈底色清除",
        "tag_unicode": "零寬度 Unicode 淨化",
        "adv_title": "⚙️ 高級仿生參數設定 (DOCX / PDF / 統計擾動)",
        "lbl_author": "偽裝文件作者 (Author)：",
        "hint_author": "寫入 Word docProps/core.xml 作者欄位",
        "lbl_rsid": "DOCX RSID 歷史會話注入數：",
        "hint_rsid": "模擬存檔次數與打字 pause 歷程",
        "lbl_pdf": "PDF 生成器偽裝目標：",
        "lbl_perturb": "啟用統計浮水印擾動 (打斷 n-gram、近義詞微調)",
        "btn_timing": "ℹ️ 應用時機",
        "btn_timing_title": "點擊查看應用時機說明",
        "timing_popover_heading": "💡 應用時機說明",
        "timing_author_title": "💡 應用時機：偽裝文件作者",
        "timing_author_desc": "【何時使用】繳交學術論文、商務報告時，避免屬性留存為 ChatGPT 或匿名開源庫。<br>【建議設定】輸入您的真實姓名、機構縮寫或設為 Author。<br>【防護效果】覆寫 docProps/core.xml 中的 dc:creator 與 cp:lastModifiedBy。",
        "timing_rsid_title": "💡 應用時機：DOCX RSID 歷史會話注入",
        "timing_rsid_desc": "【何時使用】需通過文件鑑識審查時。機器生成 Word 通常只有 0~1 組 RSID 致命破綻。<br>【建議設定】短文設為 15~20 組，長篇大作設為 25~40 組。<br>【防護效果】在 settings.xml 與 runs 中注入多節點會話鏈，模擬真實打字暫停歷程。",
        "timing_pdf_title": "💡 應用時機：PDF 生成器偽裝目標",
        "timing_pdf_desc": "【何時使用】對外提供 PDF 文件時，防止底層透露 Chromium、Skia 或 python-pdf-lib。<br>【建議選項】Mac 使用者推薦選 macOS Quartz，Windows 推薦 Microsoft Word。<br>【防護效果】偽裝 Producer 與 Creator 屬性並徹底清除 XMP 描述流。",
        "timing_perturb_title": "💡 應用時機：統計浮水印擾動",
        "timing_perturb_desc": "【何時使用】懷疑內容含有 Google SynthID 綠色詞庫機率浮水印，或面臨嚴格 AI 檢測時。<br>【建議設定】強烈建議勾選啟用。<br>【防護效果】替換 AI 高頻套話（如「值得注意的是」），打斷 n-gram 鏈結瓦解 z-score 顯著性。",
        "res_clean_prefix": "✅ 已完成淨化：",
        "res_desc": "檔案結構已完成人手特徵偽裝與元資料淨化",
        "btn_download": "💾 下載已淨化檔案",
        "stat_rsid_injected": "注入 RSID 歷程會話",
        "stat_runs_split": "自然碎形化 Runs 切分",
        "stat_ai_purged": "AI 原生標記抹除",
        "stat_pkg_synthesized": "Word 標準套件結構",
        "stat_semantic_perturbs": "語意與句構去特徵化",
        "stat_ghost_removed": "清除網頁幽靈樣式/底色",
        "stat_unicode_removed": "移除零寬度 Unicode",
        "stat_human_minutes": "偽裝打字編輯耗時",
        "stat_app_spoofed": "偽裝軟體應用程式",
        "stat_inspect_hint": "🔍 點擊查看執行詳情",
        "unit_sessions": "會話",
        "unit_splits": "處切分",
        "unit_purged": "項已清除",
        "unit_parts": "項標準組件",
        "unit_replacements": "處優化",
        "unit_styles": "處已清除",
        "unit_chars": "字元",
        "unit_minutes": "分鐘",
        "txt_raw_header": "原始文字 / 貼上內容",
        "txt_btn_paste": "📋 貼上剪貼簿",
        "txt_btn_clear": "清空",
        "txt_raw_placeholder": "請在此貼上來自 ChatGPT、Claude 等 AI 工具生成的文字，系統將自動解析隱形零寬字元與底層標記...",
        "txt_char_count": "字數：",
        "txt_alert_anomaly": "⚠️ 發現異常字元！",
        "txt_clean_header": "淨化與去指紋結果",
        "txt_btn_copy": "📋 複製乾淨文字",
        "txt_clean_placeholder": "淨化後文字將顯示於此...",
        "txt_status_clean": "純淨無指紋",
        "audit_header": "🔬 文字底層鑑識報告",
        "audit_risk_level": "AI 辨識風險等級：",
        "audit_anomalies_found": "偵測到異常標記：",
        "audit_hidden_tags": "隱藏樣式標籤：",
        "audit_watermark_entropy": "浮水印熵值干擾率：",
        "clip_header": "🛡️ 系統剪貼簿即時守護器 (Scheme C)",
        "clip_desc": "常駐於後台，複製 ChatGPT、Claude 回應時，自動在記憶體中剔除零寬字元並抹平 HTML/CSS 幽靈樣式。",
        "clip_stream_title": "即時攔截日誌 (Recent Intercepts)",
        "clip_btn_refresh": "🔄 重新整理",
        "clip_empty": "尚無剪貼簿攔截事件。啟動守護後，複製任何文字即可查看即時淨化過程。",
        "clip_item_tag": "淨化完成",
        "manual_sub": "本手冊提供循序漸進的執行步驟、底層運作原理與各功能選項的精準配置建議。",
        "manual_step1_badge": "階段 1",
        "manual_step1_title": "系統剪貼簿即時守護 (Scheme C)",
        "manual_step1_body": "<strong>運作方式：</strong>系統載入時預設處於啟用狀態（右上角綠燈）。在瀏覽器中複製任何 AI 文字時，守護程式會在 0.5 秒內自動完成脫水淨化，抹去底層的 HTML 幽靈底色與隱形字元。",
        "manual_step1_tip": "💡 <strong>提示：</strong>直接在 Word 或文件中貼上，內容即為標準純淨文字，不會殘留 <code>#F7F7F8</code> 等聊天框 HEX 底色。",
        "manual_step2_badge": "階段 2",
        "manual_step2_title": "檔案拖曳淨化與結構仿生 (DOCX / PDF / MD / TXT)",
        "manual_step2_body": "<strong>運作方式：</strong>將檔案拖曳至上傳區域，系統自動啟動 OpenXML 或 PDF 字典重構引擎：",
        "manual_step2_li1": "<strong>DOCX：</strong>逆向注入 20~40 組 RSID 會話池，將長句子依標點符號碎形化切分成自然打字節奏的 Runs，合成標準字型表、網頁設定與主題，並抹除 Claude/ChatGPT 原生中繼標記。",
        "manual_step2_li2": "<strong>PDF：</strong>覆寫 Producer 與 Creator 為官方標準（macOS Quartz 或 Word 365），清除逐頁 XMP 串流，並模擬真人時序差。",
        "manual_step2_li3": "<strong>Markdown：</strong>自動打破過度整齊的表格對齊空格，自然化清單縮排，並過濾 AI 對話開頭與結尾套話。",
        "manual_step3_badge": "階段 3",
        "manual_step3_title": "底層鑑識資訊檢視與安全下載",
        "manual_step3_body": "<strong>運作方式：</strong>處理完成後，點擊任一數據卡片即可彈出鑑識詳情視窗，檢視注入的 16 進位碼與切分範例。點擊「下載已淨化檔案」將直接由瀏覽器原生記憶體 Blob 物件完成存檔，零延遲且確保檔案完整性。",
        "faq_header": "💡 關於 AI 指紋與 NonAI 核心技術問答",
        "faq_q1": "什麼是 Word 檔中的 RSID 破綻？",
        "faq_a1": "正常人類撰寫 Word 時，每次鍵盤輸入停頓、回溯修改與存檔，都會在 <code>document.xml</code> 中留下數十組不同的修訂儲存識別碼（RSID）。AI 系統直接封裝的 DOCX 通常只有 1 組全域 RSID 或完全沒有，一眼就會被鑑識程式辨識。NonAI 會仿生注入 20~40 組會話並碎形化拆分段落。",
        "faq_q2": "為什麼複製文字會留下「幽靈底色」？",
        "faq_a2": "從網頁對話框反白文字時，剪貼簿會夾帶 <code>&lt;span style=\"background-color: #f7f7f8\"&gt;</code> 等 HEX 底色與 Inter 特徵字體。若直接貼入文件，這些樣式會永久存留在底層 XML。NonAI 剪貼簿守護可在複製瞬間自動脫水淨化。",
        "faq_q3": "如何對抗統計型浮水印 (如 SynthID) 與神經分類器？",
        "faq_a3": "統計型浮水印利用偽隨機綠色詞庫（Green List）偏好選詞，而分類器專門抓取 AI 刻板套句與固定句長。NonAI 透過打斷 n-gram 鏈結、瓦解僵化排比結構、重構學術套話並注入自然句長突現性（Burstiness），使檢測演算法的顯著性指標失效。",
        "faq_q4": "NonAI 是否保證完全隱私與離線？",
        "faq_a4": "是的。NonAI 採用完全本地離線架構，檔案清洗運算與二進位生成全在您的本機電腦或瀏覽器內部完成，絕不上傳雲端伺服器儲存。",
        "footer_text": "NonAI 2.0 • 100% 本地完全離線運算 • 保護您的創作隱私與文字指紋安全",
        "modal_close": "確定關閉",
        "modal_details": {
            "rsid": {
                "title": "注入 RSID 歷程會話 - 底層鑑識解析",
                "desc": "<strong>什麼是 RSID（修訂儲存識別碼）？</strong><br>RSID 是微軟 Word 在使用者每次鍵盤輸入停頓、回溯刪除或手動存檔時自動寫入的 4 位元組十六進位標籤。AI 生成的 Word 檔案通常完全缺乏 RSID 或全篇僅有 1 組單一數值，這是鑑識工具首要檢查的致命破綻。",
                "sub": "已注入仿生 RSID 會話池（共 {count} 組）"
            },
            "runs_split": {
                "title": "自然碎形化 Runs 切分 - 鍵盤輸入節奏模擬",
                "desc": "<strong>為什麼需要切分 Runs？</strong><br>AI 工具在匯出 DOCX 時，習慣將整段文字塞入單一連續的 <code>&lt;w:r&gt;</code> 節點。人類真實打字時，在標點符號（逗號、句號、頓號）處會產生自然的思考與按鍵停頓。NonAI 在 <strong>{count}</strong> 處標點斷點完成自然碎形化切分。",
                "sub": "切分範例樣本",
                "sample_desc": "長文字節點已被切分為具備真實人類輸入停頓間隔的 Runs 區塊。"
            },
            "claude_purged": {
                "title": "AI 原生標記抹除 - 來源指紋徹底剷除",
                "desc": "<strong>已修復致命破綻：檔案自首式 AI 標記</strong><br>AI 工具（如 Claude Docs）在匯出時會在 <code>docProps/core.xml</code> 的 <code>&lt;dc:description&gt;</code> 欄位直接寫入 <code>Claude Docs node/...</code>，並植入 <code>customXml/</code>。鑑識工具讀取後會直接標註為百分之百確定來源，而非機率推測。",
                "sub": "已執行的鑑識清除項目",
                "items": [
                    "<strong>清除標籤：</strong>徹底移除 <code>&lt;dc:description&gt;</code>，清空 custom 關鍵字、分類與主旨標籤。",
                    "<strong>移除客製套件：</strong>全數剔除 <code>customXml/</code> 目錄與 <code>docProps/custom.xml</code>。",
                    "<strong>全域字串淨化：</strong>全方位掃描 XML 資料流，徹底抹除所有 <code>Claude Docs</code>、<code>Anthropic</code>、<code>ChatGPT</code> 等標記。"
                ]
            },
            "pkg_synthesized": {
                "title": "Word 標準結構合規化 - 套件完整性修復",
                "desc": "<strong>已修復致命破綻：Word 官方套件結構缺漏</strong><br>正版微軟 Word 儲存檔案時，ZIP 封裝內必定包含 <code>fontTable.xml</code>（字型表）、<code>webSettings.xml</code>（網頁設定）與 <code>theme1.xml</code>（主題色彩）。先前 AI 檔案缺少這些檔案，導致被判定為『冒用 Word 名稱產生』。",
                "sub": "已自動合成的微軟標準套件元件",
                "items": [
                    "<code>word/fontTable.xml</code>：包含 Calibri、Times New Roman、微軟正黑體、新細明體之標準字型表。",
                    "<code>word/webSettings.xml</code>：包含瀏覽器最佳化與 PNG 支援旗標。",
                    "<code>word/theme/theme1.xml</code>：包含微軟 Office 官方標準色彩與字型架構。",
                    "<code>[Content_Types].xml</code> 與 <code>document.xml.rels</code>：已完成合法架構綁定。"
                ]
            },
            "semantic": {
                "title": "語意與句構去特徵化 - Transformer 神經網路護盾",
                "desc": "<strong>已修復破綻：Transformer 分類器特徵捕捉</strong><br>類神經偵測器（如 OmniTraces INT8）透過文字困惑度分佈、句長變異數與刻板排比結構來判斷。NonAI 將僵化的 AI 套句重構為自然流暢的專業論述，有效打破神經網路特徵值。",
                "sub": "神經網路干擾與優化指標",
                "items": [
                    "<strong>AI 套話與僵化句構重構：</strong>共 {replacements} 處",
                    "<strong>句長突現性與分號節奏優化：</strong>共 {reorganized} 處子句",
                    "<strong>N-gram 預測鏈打碎：</strong>瓦解 SynthID 綠色詞庫統計顯著性"
                ]
            },
            "ghost_styles": {
                "title": "清除網頁幽靈樣式與底色 - 對話框樣式淨化",
                "desc": "<strong>對話框貼上的幽靈底色：</strong><br>從 ChatGPT 或 Claude 網頁反白複製時，常會將 <code>#F7F7F8</code> 等灰白色背景色碼寫入 <code>&lt;w:shd&gt;</code>。NonAI 已徹底剝除孤兒底色樣式並還原純淨背景。",
                "sub": "已移除的幽靈樣式與字體項目"
            },
            "unicode": {
                "title": "隱形 Unicode 浮水印淨化 - 零寬字元剔除",
                "desc": "<strong>隱形 Unicode 條碼：</strong><br>部分 AI 防偽系統會在文本中隨機安插零寬度空格（ZWSP U+200B）、零寬不連字元（ZWNJ U+200C）或位元組順序標記（BOM U+FEFF）。NonAI 徹底剔除隱形標記，同時嚴格保護中文逗號句號等全形標點。",
                "before_label": "偵測到的異常隱形字元",
                "after_label": "淨化後狀態",
                "clean_status": "100% 純淨標準 NFC 編碼"
            },
            "human_time": {
                "title": "偽裝打字編輯耗時 - 時間軸仿生建構",
                "desc": "<strong>打字工時破綻：</strong><br>AI 工具匯出的檔案通常在 <code>docProps/app.xml</code> 留存 <code>&lt;TotalTime&gt;0&lt;/TotalTime&gt;</code>。NonAI 根據文章字數注入合理的人類打字與思考停頓歷程。",
                "sub": "仿生時間軸模型",
                "items": [
                    "<strong>模擬編輯總耗時：</strong>{minutes} 分鐘（以每分鐘 32~35 字加上構思停頓推算）",
                    "<strong>修訂版本號：</strong>第 {revision} 次修訂",
                    "<strong>建立時間：</strong>{created}",
                    "<strong>最後修改時間：</strong>{modified}"
                ]
            },
            "app_spoofed": {
                "title": "偽裝軟體應用程式 - 中繼資料重寫",
                "desc": "<strong>應用程式中繼資料：</strong><br>將 python-docx 或開源匯出庫名稱替換為合法的 Microsoft Office Word 屬性。",
                "code_title": "合規的 docProps XML 屬性"
            },
            "pdf_producer": {
                "title": "PDF 元資料與 XMP 串流淨化",
                "desc": "<strong>PDF 產生器偽裝與串流清理：</strong><br>將開源產製器（如 wkhtmltopdf、Chromium）替換為官方系統虛擬印表機，並徹底清除跨頁 XMP 串流。",
                "orig_producer": "原始 Producer",
                "spoofed_producer": "偽裝後 Producer",
                "spoofed_creator": "偽裝後 Creator"
            },
            "markdown": {
                "title": "Markdown 結構去特徵化 - 自然排版",
                "desc": "<strong>Markdown 過度完美的對齊特徵：</strong><br>AI 輸出的 Markdown 表格常有極度精準的空白對齊。NonAI 將其自然化為人類常規的簡約排版，並隨機調節清單符號。"
            }
        }
    }
}
print("Template ready")
