# -*- coding: utf-8 -*-
"""
Script to add execution logs, Stage 3/4 workflow inspection, and modal translations
to public/i18n.js and nonai/web/i18n.js across all 7 supported languages.
"""

import json
import re
from pathlib import Path

I18N_EXTENSIONS = {
    "zh-TW": {
        "wf_inspect_hint_step1": "🔍 點擊查看本階段處理歷程記錄",
        "wf_inspect_hint_step2": "🔍 點擊查看本階段審計歷程記錄",
        "wf_inspect_hint_step3": "🔍 點擊查看本階段注入歷程記錄",
        "wf_inspect_hint_step4": "📖 點擊查看原生導出作業指南",
        "wf_badge_executed": "⚡ ✅ 本檔案已自動執行",
        "wf_step1_badge_executed": "階段 1 ⚡ ✅ 本檔案已自動重構",
        "wf_step2_badge_executed": "階段 2 ⚡ ✅ 本檔案已自動審計",
        "wf_step3_badge_executed": "階段 3 ⚡ ✅ 本檔案已自動注入",
        "log_title": "📌 本檔案實際處理歷程記錄",
        "log_target_file": "目標檔案：",
        "log_status_executed": "已執行並生效",
        "log_status_verified": "鑑識通過（0 項異常 · 純淨安全）",
        "log_status_warning": "已檢測並徹底清除",
        "log_status_pending": "待上傳檔案",
        "log_pending_hint": "上傳檔案後，系統將於背景全自動執行此階段，並在此呈現本檔案處理歷程記錄。",
        "modal_details_stage3_workflow": {
            "title": "階段 3：NonAI 仿生歷程注入（自動偽裝）— 全要素執行報告",
            "desc": "NonAI 於檔案上傳時，已全自動注入底層仿生資料：包含 RSID 隨機會話池、文字 Runs 自然碎形化切分、AI 原生標記徹底剷除、Word 官方標準套件補齊、編輯工時偽裝與微軟 Word 軟體特徵注入，徹底瓦解文件鑑識檢測。",
            "sub": "本檔案仿生注入項目與鑑識指標清單"
        },
        "modal_details_stage4_workflow": {
            "title": "階段 4：正規原生導出 PDF — 原生無痕作業指南",
            "desc": "【關鍵步驟】切勿直接修改已定型排版的 PDF 或使用第三方線上轉檔網站！線上轉檔工具會在 PDF 元資料中殘留 Chromium、iText、LibreOffice 等特徵，一秒露餡。請下載洗滌後的 DOCX 檔案，使用本機正版 Microsoft Word 或系統原生列印產出 PDF，產出 100% 潔淨無痕文件。",
            "sub": "微軟 Word 本地原生無痕導出操作步驟"
        }
    },
    "zh-CN": {
        "wf_inspect_hint_step1": "🔍 点击查看本阶段处理历程记录",
        "wf_inspect_hint_step2": "🔍 点击查看本阶段审计历程记录",
        "wf_inspect_hint_step3": "🔍 点击查看本阶段注入历程记录",
        "wf_inspect_hint_step4": "📖 点击查看原生导出作业指南",
        "wf_badge_executed": "⚡ ✅ 本档案已自动执行",
        "wf_step1_badge_executed": "阶段 1 ⚡ ✅ 本档案已自动重构",
        "wf_step2_badge_executed": "阶段 2 ⚡ ✅ 本档案已自动审计",
        "wf_step3_badge_executed": "阶段 3 ⚡ ✅ 本档案已自动注入",
        "log_title": "📌 本档案实际处理历程记录",
        "log_target_file": "目标档案：",
        "log_status_executed": "已执行并生效",
        "log_status_verified": "鉴识通过（0 项异常 · 纯净安全）",
        "log_status_warning": "已检测并彻底清除",
        "log_status_pending": "待上传档案",
        "log_pending_hint": "上传档案后，系统将于后台全自动执行此阶段，并在此呈现本档案处理历程记录。",
        "modal_details_stage3_workflow": {
            "title": "阶段 3：NonAI 仿生历程注入（自动伪装）— 全要素执行报告",
            "desc": "NonAI 于档案上传时，已全自动注入底层仿生数据：包含 RSID 随机会话池、文字 Runs 自然碎形化切分、AI 原生标记彻底铲除、Word 官方标准套件补齐、编辑工时伪装与微软 Word 软件特征注入，彻底瓦解文件鉴识检测。",
            "sub": "本档案仿生注入项目与鉴识指标清单"
        },
        "modal_details_stage4_workflow": {
            "title": "阶段 4：正规原生导出 PDF — 原生无痕作业指南",
            "desc": "【关键步骤】切勿直接修改已定型排版的 PDF 或使用第三方在线转档网站！在线转档工具会在 PDF 元数据中残留 Chromium、iText、LibreOffice 等特征，一秒露馅。请下载洗涤后的 DOCX 档案，使用本机正版 Microsoft Word 或系统原生打印产出 PDF，产出 100% 洁净无痕文件。",
            "sub": "微软 Word 本地原生无痕导出操作步骤"
        }
    },
    "en": {
        "wf_inspect_hint_step1": "🔍 Click to view Stage 1 execution logs",
        "wf_inspect_hint_step2": "🔍 Click to view Stage 2 audit logs",
        "wf_inspect_hint_step3": "🔍 Click to view Stage 3 injection logs",
        "wf_inspect_hint_step4": "📖 Click to view native PDF export guide",
        "wf_badge_executed": "⚡ ✅ Automated for this file",
        "wf_step1_badge_executed": "Stage 1 ⚡ ✅ Auto-Restructured",
        "wf_step2_badge_executed": "Stage 2 ⚡ ✅ Auto-Audited",
        "wf_step3_badge_executed": "Stage 3 ⚡ ✅ Auto-Injected",
        "log_title": "📌 Execution Log for Current File",
        "log_target_file": "Target File:",
        "log_status_executed": "Executed & Active",
        "log_status_verified": "Forensic Verified (0 Anomalies · Safe)",
        "log_status_warning": "Detected & Thoroughly Purged",
        "log_status_pending": "File Upload Pending",
        "log_pending_hint": "Upload a document to automatically run this stage and view real-time execution logs for your file here.",
        "modal_details_stage3_workflow": {
            "title": "Stage 3: NonAI Biomimetic Injections — Full Execution Report",
            "desc": "Upon file upload, NonAI automatically injects low-level biomimetic artifacts: randomized RSID session chains, fractal text run splits, complete AI signature purge, official Word standard package synthesis, human editing time spoofing, and genuine MS Word software fingerprinting.",
            "sub": "Biomimetic Injections & Forensic Metrics for Current File"
        },
        "modal_details_stage4_workflow": {
            "title": "Stage 4: Native PDF Export — Forensic Integrity Guide",
            "desc": "Critical Protocol: Never use third-party online converters or edit compiled PDFs directly. Online converters inject signatures like Chromium, iText, or LibreOffice. Download the cleaned DOCX, open it in licensed Microsoft Word, and export/print to PDF locally.",
            "sub": "Step-by-Step Native Word PDF Export Protocol"
        }
    },
    "ja": {
        "wf_inspect_hint_step1": "🔍 クリックして実行ログを表示",
        "wf_inspect_hint_step2": "🔍 クリックして監査ログを表示",
        "wf_inspect_hint_step3": "🔍 クリックして注入ログを表示",
        "wf_inspect_hint_step4": "📖 クリックして出力ガイドを表示",
        "wf_badge_executed": "⚡ ✅ 実行完了",
        "wf_step1_badge_executed": "ステップ 1 ⚡ ✅ 自動再構築完了",
        "wf_step2_badge_executed": "ステップ 2 ⚡ ✅ 自動監査完了",
        "wf_step3_badge_executed": "ステップ 3 ⚡ ✅ 自動注入完了",
        "log_title": "📌 このファイルの実際の処理履歴ログ",
        "log_target_file": "対象ファイル：",
        "log_status_executed": "実行済み・反映完了",
        "log_status_verified": "鑑識合格（異常0件・安全）",
        "log_status_warning": "検出・完全消去済み",
        "log_status_pending": "ファイル未アップロード",
        "log_pending_hint": "ファイルをアップロードすると、自動的に処理が実行され、ここに履歴ログが表示されます。",
        "modal_details_stage3_workflow": {
            "title": "ステップ 3：NonAI 生体模倣履歴注入 — 総合実行レポート",
            "desc": "ファイルアップロード時に、RSIDセッションプール、Runsフラクタル分割、AI署名完全消去、標準パッケージ補完、編集時間偽装を全自動注入します。",
            "sub": "生体模倣注入項目と鑑識指標一覧"
        },
        "modal_details_stage4_workflow": {
            "title": "ステップ 4：正規ネイティブPDF出力 — 無痕作業ガイド",
            "desc": "オンライン変換サイトは使用せず、洗浄済みDOCXを正規Microsoft Wordで直接PDF出力してください。",
            "sub": "Microsoft Word ネイティブPDF出力手順"
        }
    },
    "ko": {
        "wf_inspect_hint_step1": "🔍 클릭하여 실행 로그 확인",
        "wf_inspect_hint_step2": "🔍 클릭하여 감사 로그 확인",
        "wf_inspect_hint_step3": "🔍 클릭하여 주입 로그 확인",
        "wf_inspect_hint_step4": "📖 클릭하여 내보내기 가이드 확인",
        "wf_badge_executed": "⚡ ✅ 실행 완료",
        "wf_step1_badge_executed": "1단계 ⚡ ✅ 자동 재구성 완료",
        "wf_step2_badge_executed": "2단계 ⚡ ✅ 자동 감사 완료",
        "wf_step3_badge_executed": "3단계 ⚡ ✅ 자동 주입 완료",
        "log_title": "📌 본 파일의 실제 처리 내역 로그",
        "log_target_file": "대상 파일:",
        "log_status_executed": "실행 완료 및 적용됨",
        "log_status_verified": "포렌식 검증 통과 (이상 0건 · 안전)",
        "log_status_warning": "감지 및 완전 삭제됨",
        "log_status_pending": "파일 업로드 대기 중",
        "log_pending_hint": "파일을 업로드하면 시스템이 자동으로 이 단계를 수행하고 처리 내역 로그를 표시합니다.",
        "modal_details_stage3_workflow": {
            "title": "3단계: NonAI 생체 모사 이력 주입 — 종합 실행 보고서",
            "desc": "파일 업로드 시 RSID 세션 체인, 텍스트 Runs 분할, AI 서명 제거, Word 표준 패키지 보완, 편집 시간 위장을 완전 자동으로 주입합니다.",
            "sub": "생체 모사 주입 항목 및 포렌식 지표 목록"
        },
        "modal_details_stage4_workflow": {
            "title": "4단계: 정규 네이티브 PDF 내보내기 — 가이드",
            "desc": "온라인 변환기를 사용하지 말고, 정화된 DOCX를 정품 Microsoft Word에서 직접 PDF로 내보내십시오.",
            "sub": "Microsoft Word 네이티브 PDF 내보내기 단계"
        }
    },
    "th": {
        "wf_inspect_hint_step1": "🔍 คลิกเพื่อดูบันทึกการทำงาน",
        "wf_inspect_hint_step2": "🔍 คลิกเพื่อดูบันทึกการตรวจสอบ",
        "wf_inspect_hint_step3": "🔍 คลิกเพื่อดูบันทึกการฉีดข้อมูล",
        "wf_inspect_hint_step4": "📖 คลิกเพื่อดูคู่มือการส่งออก",
        "wf_badge_executed": "⚡ ✅ ทำงานสำเร็จ",
        "wf_step1_badge_executed": "ขั้นตอนที่ 1 ⚡ ✅ ปรับโครงสร้างเสร็จสิ้น",
        "wf_step2_badge_executed": "ขั้นตอนที่ 2 ⚡ ✅ ตรวจสอบเสร็จสิ้น",
        "wf_step3_badge_executed": "ขั้นตอนที่ 3 ⚡ ✅ ฉีดข้อมูลเสร็จสิ้น",
        "log_title": "📌 บันทึกประวัติการประมวลผลไฟล์นี้",
        "log_target_file": "ไฟล์เป้าหมาย:",
        "log_status_executed": "ดำเนินการและมีผลแล้ว",
        "log_status_verified": "ผ่านการตรวจสอบ (ไม่มีความผิดปกติ ปลอดภัย)",
        "log_status_warning": "ตรวจพบและลบเรียบร้อยแล้ว",
        "log_status_pending": "รอการอัปโหลดไฟล์",
        "log_pending_hint": "เมื่ออัปโหลดไฟล์ ระบบจะทำงานขั้นตอนนี้โดยอัตโนมัติและแสดงบันทึกที่นี่",
        "modal_details_stage3_workflow": {
            "title": "ขั้นตอนที่ 3: การฉีดข้อมูลทางชีวภาพ NonAI — รายงานการทำงานครบวงจร",
            "desc": "ระบบฉีดข้อมูลจำลอง RSID, การแยก Runs, ลบรอยนิ้วมือ AI, เติมส่วนประกอบมาตรฐาน Word และจำลองเวลาพิมพ์อัตโนมัติ",
            "sub": "รายการการฉีดข้อมูลและตัวชี้วัดสำหรับไฟล์นี้"
        },
        "modal_details_stage4_workflow": {
            "title": "ขั้นตอนที่ 4: การส่งออกเป็น PDF แบบเนทีฟ — คู่มือการใช้งาน",
            "desc": "ห้ามใช้เว็บแปลงไฟล์ออนไลน์ ให้เปิดไฟล์ DOCX ที่ผ่านการล้างใน Microsoft Word ของแท้แล้วสั่งพิมพ์/บันทึกเป็น PDF",
            "sub": "ขั้นตอนการส่งออก PDF ผ่าน Microsoft Word"
        }
    },
    "ru": {
        "wf_inspect_hint_step1": "🔍 Нажмите для просмотра логов этапа",
        "wf_inspect_hint_step2": "🔍 Нажмите для просмотра аудита этапа",
        "wf_inspect_hint_step3": "🔍 Нажмите для просмотра логов инъекции",
        "wf_inspect_hint_step4": "📖 Руководство по нативному экспорту в PDF",
        "wf_badge_executed": "⚡ ✅ Выполнено для файла",
        "wf_step1_badge_executed": "Этап 1 ⚡ ✅ Автоматически перестроено",
        "wf_step2_badge_executed": "Этап 2 ⚡ ✅ Автоматически проверено",
        "wf_step3_badge_executed": "Этап 3 ⚡ ✅ Автоматически внедрено",
        "log_title": "📌 Фактический журнал обработки файла",
        "log_target_file": "Целевой файл:",
        "log_status_executed": "Выполнено и активно",
        "log_status_verified": "Проверка пройдена (0 аномалий · Чисто)",
        "log_status_warning": "Обнаружено и удалено",
        "log_status_pending": "Ожидание загрузки файла",
        "log_pending_hint": "После загрузки документа система автоматически выполнит этот этап и отобразит журнал обработки.",
        "modal_details_stage3_workflow": {
            "title": "Этап 3: Биомиметические инъекции NonAI — Полный отчет",
            "desc": "При загрузке автоматически внедряются пулы сессий RSID, фрактальное дробление Runs, очистка тегов ИИ, синтез пакетов Word и подмена времени работы.",
            "sub": "Список инъекций и криминалистические метрики"
        },
        "modal_details_stage4_workflow": {
            "title": "Этап 4: Нативный экспорт в PDF — Руководство",
            "desc": "Не используйте онлайн-конвертеры. Откройте очищенный DOCX в Microsoft Word и экспортируйте в PDF локально.",
            "sub": "Пошаговый протокол экспорта PDF через Word"
        }
    }
}

def update_file(path: Path):
    content = path.read_text(encoding="utf-8")
    m = re.search(r"const I18N_TRANSLATIONS = (\{.*?\});", content, re.DOTALL)
    assert m, f"I18N_TRANSLATIONS not found in {path}"
    data = json.loads(m.group(1))

    for lang, keys in I18N_EXTENSIONS.items():
        assert lang in data, f"Language {lang} missing"
        for k, v in keys.items():
            if k.startswith("modal_details_"):
                target_k = k.replace("modal_details_", "")
                if "modal_details" not in data[lang]:
                    data[lang]["modal_details"] = {}
                data[lang]["modal_details"][target_k] = v
            else:
                data[lang][k] = v

    new_content = f"// NonAI Multilingual Localization Dictionary (7 Languages)\n// Supported: zh-TW, en, zh-CN, ja, ko, th, ru\n\nconst I18N_TRANSLATIONS = {json.dumps(data, ensure_ascii=False, indent=2)};\n"
    path.write_text(new_content, encoding="utf-8")
    print(f"[OK] Successfully updated {path}")

if __name__ == "__main__":
    update_file(Path("public/i18n.js"))
    update_file(Path("nonai/web/i18n.js"))
