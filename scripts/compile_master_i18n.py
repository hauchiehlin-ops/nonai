# -*- coding: utf-8 -*-
"""
Compile Master i18n Dictionary for NonAI (7 Languages)
Guarantees 100% key and modal symmetry across:
zh-TW, en, zh-CN, ja, ko, th, ru
Zero prohibited phrases ("零基礎", "手把手").
"""

import json
from pathlib import Path

# 1. Load zh-TW
with open("scripts/generate_i18n.py", "r", encoding="utf-8") as f:
    gen_code = f.read()
env1 = {}
exec(gen_code, env1)
DATA = env1["I18N_DATA"]

# 2. Load zh-CN
with open("scripts/build_full_i18n.py", "r", encoding="utf-8") as f:
    build_code = f.read()
env2 = {"DATA": DATA}
exec("import json\nfrom pathlib import Path\n" + build_code.replace("from scripts.build_full_i18n import DATA", ""), env2)

# 3. Load ja
with open("scripts/append_ja.py", "r", encoding="utf-8") as f:
    ja_code = f.read()
env3 = {"DATA": DATA}
exec("import json\n" + ja_code.replace("from scripts.build_full_i18n import DATA", ""), env3)

# 4. Load ko, th, ru
with open("scripts/compile_all_i18n.py", "r", encoding="utf-8") as f:
    rest_code = f.read()
env4 = {"DATA": DATA}
cleaned_rest = rest_code.replace("from scripts.build_full_i18n import DATA", "").replace("import scripts.append_ja", "")
if "# Verify symmetry" in cleaned_rest:
    cleaned_rest = cleaned_rest.split("# Verify symmetry")[0]
exec("import json\nimport re\n" + cleaned_rest, env4)

# 5. Define en (English) with full 105 base keys + 11 modal items
DATA["en"] = {
    "app_title": "NonAI - AI Digital Fingerprint & Watermark Stripper",
    "brand_sub": "AI Digital Fingerprint, Watermark & Deep Metadata Removal Engine",
    "watcher_label": "Clipboard Shield (Scheme C)",
    "watcher_active": "Active Monitoring",
    "watcher_inactive": "Inactive",
    "watcher_btn_start": "Enable Shield",
    "watcher_btn_stop": "Disable Shield",
    "watcher_running": "Shield Active (Auto-sanitizing clipboard contents)",
    "watcher_stopped": "Shield Inactive",
    "tab_files": "📁 File Purifier (.docx, .pdf, .md, .txt)",
    "tab_text": "✍️ Live Text & Hex Forensics",
    "tab_clipboard": "📋 Clipboard Activity Log",
    "tab_manual": "📖 User & Forensic Manual",
    "drop_title": "Drag & drop files here, or click to browse",
    "drop_subtitle": "Supported formats: Word (.docx), PDF (.pdf), Markdown (.md), Plain Text (.txt)",
    "tag_rsid": "DOCX RSID Biomimetic Injection",
    "tag_pdf": "PDF XMP Metadata Spoofing",
    "tag_css": "Ghost Web CSS Background Purge",
    "tag_unicode": "Zero-Width Unicode Sanitization",
    "adv_title": "⚙️ Advanced Biomimetic Parameters (DOCX / PDF / Perturbation)",
    "lbl_author": "Document Author Spoof (Author):",
    "hint_author": "Written to Word docProps/core.xml author fields",
    "lbl_rsid": "DOCX RSID History Session Injections:",
    "hint_rsid": "Simulates human save sessions and typing pause history",
    "lbl_pdf": "PDF Producer Spoof Target:",
    "lbl_perturb": "Enable Statistical Watermark Perturbation (Break n-grams, synonym tuning)",
    "btn_timing": "ℹ️ Timing & Usage",
    "btn_timing_title": "Click to view application context and timing guidance",
    "timing_popover_heading": "💡 Application Context & Timing Guidance",
    "timing_author_title": "💡 Usage Context: Document Author Spoof",
    "timing_author_desc": "【When to use】When submitting academic papers or business proposals, preventing metadata from exposing ChatGPT or open-source export libraries.<br>【Recommended】Enter your real name, institutional acronym, or 'Author'.<br>【Protection】Overwrites dc:creator and cp:lastModifiedBy in docProps/core.xml.",
    "timing_rsid_title": "💡 Usage Context: DOCX RSID Session Injection",
    "timing_rsid_desc": "【When to use】When passing forensic document scrutiny. Machine-generated Word files typically have only 0 to 1 uniform RSID session—a dead giveaway.<br>【Recommended】15–20 sessions for shorter essays, 25–40 sessions for lengthy theses.<br>【Protection】Injects multi-node session chains in settings.xml and fragments runs to simulate realistic typing pauses.",
    "timing_pdf_title": "💡 Usage Context: PDF Producer Spoof Target",
    "timing_pdf_desc": "【When to use】When distributing PDF documents, preventing underlying streams from revealing Chromium, Skia, or python-pdf signatures.<br>【Recommended】Choose macOS Quartz if claiming Mac origin, or Microsoft Word for Windows environments.<br>【Protection】Spoofs Producer and Creator properties and thoroughly purges per-page XMP description streams.",
    "timing_perturb_title": "💡 Usage Context: Statistical Watermark Perturbation",
    "timing_perturb_desc": "【When to use】When content may contain Google SynthID green-token probabilistic watermarks or face strict AI classifier detection.<br>【Recommended】Strongly recommended to enable.<br>【Protection】Substitutes high-frequency AI transition clichés (e.g., 'It is noteworthy that') and disrupts n-gram chains to nullify z-score significance.",
    "res_clean_prefix": "✅ Sanitization Complete: ",
    "res_desc": "File structure reconstructed with human biomimetic traits and clean metadata",
    "btn_download": "💾 Download Sanitized File",
    "stat_rsid_injected": "Injected RSID Sessions",
    "stat_runs_split": "Fractal Run Splittings",
    "stat_ai_purged": "AI Signatures Purged",
    "stat_pkg_synthesized": "Word Package Synthesized",
    "stat_semantic_perturbs": "Semantic De-Patterning",
    "stat_ghost_removed": "Ghost Web Styles Removed",
    "stat_unicode_removed": "Zero-Width Chars Removed",
    "stat_human_minutes": "Spoofed Typing Duration",
    "stat_app_spoofed": "Spoofed Application",
    "stat_inspect_hint": "🔍 Click to inspect execution details",
    "unit_sessions": "Sessions",
    "unit_splits": "Splits",
    "unit_purged": "Purged",
    "unit_parts": "Parts",
    "unit_replacements": "Tuned",
    "unit_styles": "Cleaned",
    "unit_chars": "Chars",
    "unit_minutes": "Minutes",
    "txt_raw_header": "Original Text / Paste Area",
    "txt_btn_paste": "📋 Paste Clipboard",
    "txt_btn_clear": "Clear",
    "txt_raw_placeholder": "Paste text generated by ChatGPT, Claude, or other AI tools here to analyze invisible zero-width markers...",
    "txt_char_count": "Characters: ",
    "txt_alert_anomaly": "⚠️ Hidden characters detected!",
    "txt_clean_header": "Sanitized & De-fingerprinted Result",
    "txt_btn_copy": "📋 Copy Clean Text",
    "txt_clean_placeholder": "Purified text will appear here...",
    "txt_status_clean": "Pure & Fingerprint-Free",
    "audit_header": "🔬 Text Forensics Audit Report",
    "audit_risk_level": "AI Risk Level:",
    "audit_anomalies_found": "Detected Markers:",
    "audit_hidden_tags": "Hidden Style Tags:",
    "audit_watermark_entropy": "Watermark Entropy Rate:",
    "clip_header": "🛡️ Real-Time Clipboard Shield (Scheme C)",
    "clip_desc": "Runs in background. When you copy ChatGPT/Claude responses, automatically purges zero-width chars and strips HTML/CSS ghost styles in memory within 0.5s.",
    "clip_stream_title": "Live Intercepts (Recent Intercepts)",
    "clip_btn_refresh": "🔄 Refresh",
    "clip_empty": "No clipboard events yet. Enable shield and copy any text to see real-time sanitization.",
    "clip_item_tag": "Sanitized",
    "manual_sub": "This manual provides progressive procedural steps, underlying operational principles, and precision configuration guidance for every feature.",
    "manual_step1_badge": "Stage 1",
    "manual_step1_title": "System Clipboard Real-Time Shield (Scheme C)",
    "manual_step1_body": "<strong>How it works:</strong> The shield is enabled by default upon loading (green status indicator in upper right). When copying AI-generated text in your browser, the daemon purges watermarks in memory within 0.5s, stripping HTML ghost background colors and invisible unicode characters.",
    "manual_step1_tip": "💡 <strong>Tip:</strong> Paste directly into Word or documents—content arrives as clean standard text without residual <code>#F7F7F8</code> chat box HEX background shading.",
    "manual_step2_badge": "Stage 2",
    "manual_step2_title": "File Drag-and-Drop Sanitization & Biomimetic Structure (DOCX / PDF / MD / TXT)",
    "manual_step2_body": "<strong>How it works:</strong> Drag and drop your file into the upload zone to activate the OpenXML or PDF dictionary reconstruction engine:",
    "manual_step2_li1": "<strong>DOCX:</strong> Inversely injects 20–40 RSID session pools, fragments long runs at punctuation marks to mimic natural human typing cadence, synthesizes official font tables, web settings, and themes, and purges native Claude/ChatGPT metadata markers.",
    "manual_step2_li2": "<strong>PDF:</strong> Overwrites Producer and Creator to official standards (macOS Quartz or Word 365), eliminates per-page XMP streams, and simulates realistic human authoring timestamps.",
    "manual_step2_li3": "<strong>Markdown:</strong> Breaks overly rigid column spacing in tables, normalizes list indentation, and filters AI dialogue opening/closing clichés.",
    "manual_step3_badge": "Stage 3",
    "manual_step3_title": "Underlying Forensic Inspection & Secure Download",
    "manual_step3_body": "<strong>How it works:</strong> Once processing finishes, click any statistic card to open the forensic details modal and inspect injected hex codes or split samples. Click 'Download Sanitized File' to save directly from browser memory Blob objects with zero latency and full file integrity.",
    "faq_header": "💡 AI Fingerprints & NonAI Core Technology FAQ",
    "faq_q1": "What is the DOCX RSID vulnerability?",
    "faq_a1": "When humans compose in Word, every typing pause, backspace correction, and save event generates unique Revision Save IDs (RSIDs) in <code>document.xml</code>. Machine-generated DOCX files usually have only 1 uniform RSID or none at all, making them instantly identifiable. NonAI injects 20–40 authentic biomimetic sessions and fragments runs across paragraphs.",
    "faq_q2": "Why does copying text leave 'ghost background colors'?",
    "faq_a2": "Copying highlighted text from web chat windows attaches hidden styles like <code>&lt;span style=\"background-color: #f7f7f8\"&gt;</code> and distinctive web fonts. Pasting directly into documents preserves these styles in the underlying XML. NonAI Clipboard Shield intercepts and purges them instantly in memory.",
    "faq_q3": "How does NonAI counter statistical watermarks (e.g., SynthID) and neural classifiers?",
    "faq_a3": "Statistical watermarks bias token generation towards pseudo-random green lists, while neural classifiers detect rigid parallelism and uniform sentence lengths. NonAI disrupts n-gram chains, restructures AI clichés, and introduces natural sentence length variation (burstiness) to invalidate detector z-score significance.",
    "faq_q4": "Does NonAI guarantee complete privacy and offline operation?",
    "faq_a4": "Yes. NonAI operates with a strictly local, offline architecture. All file sanitization, binary reconstruction, and text processing occur entirely on your local machine or within your browser session, with zero data transmitted to external cloud servers.",
    "footer_text": "NonAI 2.0 • 100% Fully Local Offline Processing • Privacy & Anti-Fingerprint Shield",
    "modal_close": "Close",
    "modal_details": {
        "rsid": {
            "title": "DOCX RSID Biomimetic History Sessions - Typing Interruption Emulation",
            "desc": "<strong>What is an RSID (Revision Save ID)?</strong><br>An RSID is a 4-byte hexadecimal identifier automatically written by Microsoft Word whenever a user pauses keyboard input, makes backspace edits, or manually saves. AI-generated Word files typically lack RSIDs entirely or share a single uniform value throughout the document—a fatal giveaway checked first by forensic audit tools.",
            "sub": "Injected Biomimetic RSID Session Pool ({count} sessions total)"
        },
        "runs_split": {
            "title": "Fractal Run Splittings - Keystroke Rhythm Simulation",
            "desc": "<strong>Why split runs?</strong><br>When exporting DOCX files, AI tools pack entire paragraphs into a single continuous <code>&lt;w:r&gt;</code> run node. Genuine human typing naturally pauses at punctuation marks (commas, periods, semicolons) for cognitive rhythm. NonAI has fragmented text into natural runs across <strong>{count}</strong> punctuation breakpoints.",
            "sub": "Run Splitting Samples",
            "sample_desc": "Long monolithic text runs have been partitioned into distinct Runs nodes with authentic human pause cadence."
        },
        "claude_purged": {
            "title": "AI Native Signatures Purged - Origin Fingerprints Completely Stripped",
            "desc": "<strong>Resolved Vulnerability: Self-Incriminating AI Metadata</strong><br>AI export tools (such as Claude Docs) directly embed identifiers like <code>Claude Docs node/...</code> into <code>&lt;dc:description&gt;</code> within <code>docProps/core.xml</code>, alongside <code>customXml/</code> trees. Forensic scanners read these fields as definitive 100% provenance proof rather than probabilistic guesses.",
            "sub": "Executed Forensic Purge Items",
            "items": [
                "<strong>Clean Description:</strong> Completely removed <code>&lt;dc:description&gt;</code>; cleared custom keywords, categories, and subject tags.",
                "<strong>Remove Custom XML:</strong> Eliminated all <code>customXml/</code> directories and <code>docProps/custom.xml</code>.",
                "<strong>Global Stream Purge:</strong> Deep-scanned XML streams to erase all instances of <code>Claude Docs</code>, <code>Anthropic</code>, <code>ChatGPT</code>, etc."
            ]
        },
        "pkg_synthesized": {
            "title": "Word Official Structure Compliance - Package Integrity Restored",
            "desc": "<strong>Resolved Vulnerability: Missing Official Word Package Parts</strong><br>Official Microsoft Word saves always include <code>fontTable.xml</code> (font table), <code>webSettings.xml</code> (web settings), and <code>theme1.xml</code> (color theme) inside the ZIP container. Previous AI documents omitted these components, triggering alerts for 'unauthorized third-party Word synthesis'.",
            "sub": "Synthesized Microsoft Standard Package Components",
            "items": [
                "<code>word/fontTable.xml</code>: Standard font table containing Calibri, Times New Roman, and official fallbacks.",
                "<code>word/webSettings.xml</code>: Browser optimization parameters and PNG support flags.",
                "<code>word/theme/theme1.xml</code>: Official standard Microsoft Office color palette and typography schema.",
                "<code>[Content_Types].xml</code> & <code>document.xml.rels</code>: Validated schema relationship bindings."
            ]
        },
        "semantic": {
            "title": "Semantic & Syntactic De-Patterning - Transformer Neural Classifier Shield",
            "desc": "<strong>Resolved Vulnerability: Transformer Classifier Feature Extraction</strong><br>Neural AI detectors (e.g., OmniTraces INT8) analyze text perplexity distributions, sentence length variance, and rigid parallelisms. NonAI restructures rigid AI transitional phrases into natural, nuanced professional discourse, breaking neural feature embeddings.",
            "sub": "Neural Disruption & Optimization Metrics",
            "items": [
                "<strong>AI Clichés & Rigid Transitions Restructured:</strong> {replacements} instances",
                "<strong>Sentence Burstiness & Semicolon Rhythm Tuned:</strong> {reorganized} clauses",
                "<strong>N-gram Prediction Chains Disrupted:</strong> Nullified SynthID green-token statistical significance"
            ]
        },
        "ghost_styles": {
            "title": "Ghost Web CSS Styles & Background Purge - Dialog Formatting Neutralized",
            "desc": "<strong>Ghost Backgrounds from Web Dialogs:</strong><br>Highlighting and copying from ChatGPT or Claude web interfaces frequently injects gray background codes such as <code>#F7F7F8</code> into <code>&lt;w:shd&gt;</code>. NonAI has stripped orphan shading styles and restored clean, natural document backgrounds.",
            "sub": "Removed Ghost Styles & Font Bindings"
        },
        "unicode": {
            "title": "Invisible Unicode Watermark Sanitization - Zero-Width Character Stripping",
            "desc": "<strong>Invisible Unicode Barcodes:</strong><br>Certain AI tracking tools insert zero-width spaces (ZWSP U+200B), non-joiners (ZWNJ U+200C), or byte order marks (BOM U+FEFF) as steganographic markers. NonAI strips all invisible markers while preserving legitimate punctuation.",
            "before_label": "Detected Anomalous Invisible Characters",
            "after_label": "Sanitized State",
            "clean_status": "100% Clean Standard NFC Encoding"
        },
        "human_time": {
            "title": "Spoofed Typing Duration - Biomimetic Chronology Construction",
            "desc": "<strong>Typing Work-Time Anomaly:</strong><br>AI-exported documents typically leave <code>&lt;TotalTime&gt;0&lt;/TotalTime&gt;</code> in <code>docProps/app.xml</code>. NonAI calculates and injects realistic typing and contemplation intervals based on total word count.",
            "sub": "Biomimetic Timeline Model",
            "items": [
                "<strong>Simulated Total Editing Duration:</strong> {minutes} minutes (based on 32–35 wpm plus pause intervals)",
                "<strong>Revision Count:</strong> Revision #{revision}",
                "<strong>Creation Timestamp:</strong> {created}",
                "<strong>Last Modified Timestamp:</strong> {modified}"
            ]
        },
        "app_spoofed": {
            "title": "Spoofed Software Application - Metadata Overwrite",
            "desc": "<strong>Application Metadata:</strong><br>Replaces python-docx or open-source export library identifiers with legitimate Microsoft Office Word metadata properties.",
            "code_title": "Compliant docProps XML Attributes"
        },
        "pdf_producer": {
            "title": "PDF Metadata & XMP Stream Sanitization",
            "desc": "<strong>PDF Producer Spoofing & Stream Purge:</strong><br>Replaces open-source generators (e.g., wkhtmltopdf, Chromium) with official virtual printers and purges cross-page XMP stream structures.",
            "orig_producer": "Original Producer",
            "spoofed_producer": "Spoofed Producer",
            "spoofed_creator": "Spoofed Creator"
        },
        "markdown": {
            "title": "Markdown Structure De-Patterning - Natural Typography",
            "desc": "<strong>Markdown Overly Perfect Alignment:</strong><br>AI Markdown tables often feature rigidly padded whitespace alignment. NonAI normalizes tables into clean, natural human formatting and balances list bullets."
        }
    }
}

# 6. Complement missing audit and modal keys across all 7 languages
EXTRA_KEYS = {
    "zh-TW": {
        "audit_risk": "AI 殘留綜合風險評分",
        "audit_zero_width": "隱形字元 (Zero-Width)",
        "audit_spaces": "不尋常空白正規化",
        "audit_disruption": "n-gram 語意打散率",
        "footer_github": "GitHub 開源倉庫",
        "footer_sitemap": "網站地圖",
        "modal_title_default": "執行詳情與底層鑑識",
        "modal_btn_close": "確定關閉"
    },
    "en": {
        "audit_risk": "AI Residual Risk Score",
        "audit_zero_width": "Zero-Width Characters",
        "audit_spaces": "Normalized Spaces",
        "audit_disruption": "n-gram Disruption Rate",
        "footer_github": "GitHub Repository",
        "footer_sitemap": "Sitemap",
        "modal_title_default": "Execution Details & Forensic Breakdown",
        "modal_btn_close": "Close"
    },
    "zh-CN": {
        "audit_risk": "AI 残留综合风险评分",
        "audit_zero_width": "隐形字符 (Zero-Width)",
        "audit_spaces": "异常空格规范化",
        "audit_disruption": "n-gram 语义打散率",
        "footer_github": "GitHub 开源仓库",
        "footer_sitemap": "网站地图",
        "modal_title_default": "执行详情与底层鉴识",
        "modal_btn_close": "确定关闭"
    },
    "ja": {
        "audit_risk": "AI 指紋残留総合リスク評価",
        "audit_zero_width": "不可視文字 (Zero-Width)",
        "audit_spaces": "異常スペース正規化",
        "audit_disruption": "n-gram 統計的攪乱率",
        "footer_github": "GitHub リポジトリ",
        "footer_sitemap": "サイトマップ",
        "modal_title_default": "実行詳細とフォレンジック分析",
        "modal_btn_close": "閉じる"
    },
    "ko": {
        "audit_risk": "AI 잔존 종합 위험도",
        "audit_zero_width": "투명 유니코드 (Zero-Width)",
        "audit_spaces": "비정상 공백 정규화",
        "audit_disruption": "n-gram 통계적 교란율",
        "footer_github": "GitHub 저장소",
        "footer_sitemap": "사이트맵",
        "modal_title_default": "실행 세부 정보 및 포렌식 분석",
        "modal_btn_close": "닫기"
    },
    "th": {
        "audit_risk": "คะแนนความเสี่ยงลายเซ็น AI",
        "audit_zero_width": "อักขระล่องหน (Zero-Width)",
        "audit_spaces": "ปรับมาตรฐานช่องว่างผิดปกติ",
        "audit_disruption": "อัตราการรบกวน n-gram",
        "footer_github": "คลัง GitHub",
        "footer_sitemap": "แผนผังเว็บไซต์",
        "modal_title_default": "รายละเอียดการทำงานและการตรวจสอบนิติวิทยาศาสตร์",
        "modal_btn_close": "ปิดหน้าต่าง"
    },
    "ru": {
        "audit_risk": "Общий риск присутствия AI-следов",
        "audit_zero_width": "Невидимые символы (Zero-Width)",
        "audit_spaces": "Нормализованные пробелы",
        "audit_disruption": "Коэффициент разрушения n-грамм",
        "footer_github": "Репозиторий GitHub",
        "footer_sitemap": "Карта сайта",
        "modal_title_default": "Детали выполнения и форензик-анализ",
        "modal_btn_close": "Закрыть"
    }
}

for l, extras in EXTRA_KEYS.items():
    DATA[l].update(extras)

langs = ["zh-TW", "en", "zh-CN", "ja", "ko", "th", "ru"]
print("Languages loaded:", list(DATA.keys()))

base_keys = set(DATA["zh-TW"].keys())
print(f"Total base keys per language: {len(base_keys)}")

for l in langs:
    if l not in DATA:
        raise ValueError(f"Missing language: {l}")
    curr_keys = set(DATA[l].keys())
    missing_in_curr = base_keys - curr_keys
    missing_in_base = curr_keys - base_keys
    if missing_in_curr:
        raise ValueError(f"Language {l} missing keys: {missing_in_curr}")
    if missing_in_base:
        raise ValueError(f"Language {l} has extra keys: {missing_in_base}")
    
    # Check modal_details keys and subkeys
    base_modal = DATA["zh-TW"]["modal_details"]
    curr_modal = DATA[l]["modal_details"]
    if set(base_modal.keys()) != set(curr_modal.keys()):
        raise ValueError(f"Language {l} modal keys mismatch: {set(base_modal.keys()) ^ set(curr_modal.keys())}")
    for mk in base_modal:
        if set(base_modal[mk].keys()) != set(curr_modal[mk].keys()):
            raise ValueError(f"Language {l} modal subkey mismatch for {mk}: {set(base_modal[mk].keys()) ^ set(curr_modal[mk].keys())}")

    # Check prohibited words
    txt = json.dumps(DATA[l], ensure_ascii=False)
    assert "零基礎" not in txt, f"Prohibited word 零基礎 found in {l}"
    assert "手把手" not in txt, f"Prohibited word 手把手 found in {l}"

print(f"SUCCESS: All {len(langs)} languages validated with 100% key, subkey, and modal symmetry!")

# Write out to public/i18n.js and nonai/web/i18n.js
out_js = f"// NonAI Multilingual Localization Dictionary (7 Languages)\n// Supported: {', '.join(langs)}\n\nconst I18N_TRANSLATIONS = {json.dumps(DATA, indent=2, ensure_ascii=False)};\n"

for p in ["public/i18n.js", "nonai/web/i18n.js"]:
    with open(p, "w", encoding="utf-8") as f:
        f.write(out_js)
    print("Wrote:", p)
