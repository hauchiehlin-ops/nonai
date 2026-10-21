# -*- coding: utf-8 -*-
import json
import re

from scripts.build_full_i18n import DATA
import scripts.append_ja

# 5. ko (한국어)
DATA["ko"] = {
    "app_title": "NonAI - AI 디지털 지문 및 숨김 흔적 제거 시스템",
    "brand_sub": "AI 디지털 지문, 워터마크 및 하위 레이어 메타데이터 완전 제거 엔진",
    "watcher_label": "클립보드 보호기 (Scheme C)",
    "watcher_active": "실시간 감시 중",
    "watcher_inactive": "미작동",
    "watcher_btn_start": "보호 시작",
    "watcher_btn_stop": "보호 중지",
    "watcher_running": "보호 작동 중 (복사된 텍스트 자동 정화)",
    "watcher_stopped": "보호 미작동",
    "tab_files": "📁 파일 정화 작업대 (.docx, .pdf, .md, .txt)",
    "tab_text": "✍️ 실시간 텍스트 및 Hex 포렌식",
    "tab_clipboard": "📋 클립보드 활동 로그",
    "tab_manual": "📖 사용 및 포렌식 매뉴얼",
    "drop_title": "파일을 여기로 드래그하거나 클릭하여 선택하세요",
    "drop_subtitle": "지원 형식: Word (.docx), PDF (.pdf), Markdown (.md), 일반 텍스트 (.txt)",
    "tag_rsid": "DOCX RSID 생체모방 주입",
    "tag_pdf": "PDF XMP 메타데이터 위장",
    "tag_css": "웹 CSS 고스트 배경색 제거",
    "tag_unicode": "제로 너비 Unicode 정화",
    "adv_title": "⚙️ 고급 생체모방 매개변수 설정 (DOCX / PDF / 통계적 교란)",
    "lbl_author": "문서 작성자 위장 (Author):",
    "hint_author": "Word docProps/core.xml 작성자 필드에 기록",
    "lbl_rsid": "DOCX RSID 세션 주입 수:",
    "hint_rsid": "저장 횟수 및 타이핑 휴지기 기록 모방",
    "lbl_pdf": "PDF 생성 프로그램 위장 대상:",
    "lbl_perturb": "통계적 워터마크 교란 활성화 (n-gram 단절 및 유의어 조정)",
    "btn_timing": "ℹ️ 적용 타이밍",
    "btn_timing_title": "적용 타이밍 안내 보기",
    "timing_popover_heading": "💡 적용 타이밍 안내",
    "timing_author_title": "💡 적용 타이밍: 문서 작성자 위장",
    "timing_author_desc": "【사용 시점】학술 논문, 비즈니스 보고서 제출 시 속성이 ChatGPT나 오픈소스 라이브러리로 남는 것을 방지합니다.<br>【권장 설정】실명, 소속 기관 약어 또는 Author를 입력하십시오.<br>【방어 효과】docProps/core.xml의 dc:creator 및 cp:lastModifiedBy를 덮어씁니다.",
    "timing_rsid_title": "💡 적용 타이밍: DOCX RSID 세션 주입",
    "timing_rsid_desc": "【사용 시점】문서 포렌식 검사를 통과해야 할 때. AI 생성 Word 파일은 대개 RSID가 0~1개뿐인 결정적 결함이 있습니다.<br>【권장 설정】짧은 글은 15~20개, 긴 논문은 25~40개.<br>【방어 효과】settings.xml과 runs에 다중 세션 체인을 주입하여 실제 타이핑 멈춤 과정을 모방합니다.",
    "timing_pdf_title": "💡 적용 타이밍: PDF 생성기 위장 대상",
    "timing_pdf_desc": "【사용 시점】외부에 PDF 문서를 전달할 때 내부적으로 Chromium, Skia, python-pdf-lib이 노출되는 것을 방지합니다.<br>【권장 옵션】Mac 사용자는 macOS Quartz, Windows는 Microsoft Word 권장.<br>【방어 효과】Producer와 Creator 속성을 위장하고 XMP 스트림을 완전히 제거합니다.",
    "timing_perturb_title": "💡 적용 타이밍: 통계적 워터마크 교란",
    "timing_perturb_desc": "【사용 시점】Google SynthID 그린 토큰 워터마크나 엄격한 AI 탐지기를 우회해야 할 때.<br>【권장 설정】항상 활성화하는 것을 강력히 권장합니다.<br>【방어 효과】AI 빈출 상투구를 대체하고 n-gram 연결을 끊어 z-score 통계적 유의성을 무력화합니다.",
    "res_clean_prefix": "✅ 정화 완료: ",
    "res_desc": "파일 구조가 인간의 작성 생체 특징과 깨끗한 메타데이터로 재구성되었습니다",
    "btn_download": "💾 정화된 파일 다운로드",
    "stat_rsid_injected": "주입된 RSID 세션",
    "stat_runs_split": "Runs 프랙탈 분할",
    "stat_ai_purged": "AI 고유 서명 제거",
    "stat_pkg_synthesized": "Word 표준 패키지 구조화",
    "stat_semantic_perturbs": "문장 패턴 및 어휘 탈특징화",
    "stat_ghost_removed": "웹 고스트 스타일/배경색 제거",
    "stat_unicode_removed": "제로 너비 Unicode 제거",
    "stat_human_minutes": "위장 타이핑 소요 시간",
    "stat_app_spoofed": "위장 애플리케이션",
    "stat_inspect_hint": "🔍 클릭하여 실행 세부 정보 확인",
    "unit_sessions": "세션",
    "unit_splits": "곳 분할",
    "unit_purged": "건 제거",
    "unit_parts": "개 표준 구성요소",
    "unit_replacements": "곳 최적화",
    "unit_styles": "곳 제거",
    "unit_chars": "자",
    "unit_minutes": "분",
    "txt_raw_header": "원본 텍스트 / 붙여넣은 내용",
    "txt_btn_paste": "📋 클립보드 붙여넣기",
    "txt_btn_clear": "비우기",
    "txt_raw_placeholder": "ChatGPT, Claude 등 AI로 생성된 텍스트를 여기에 붙여넣으세요. 보이지 않는 숨김 문자와 메타데이터를 자동 분석합니다...",
    "txt_char_count": "글자 수: ",
    "txt_alert_anomaly": "⚠️ 비정상 숨김 문자 발견!",
    "txt_clean_header": "정화 및 지문 제거 결과",
    "txt_btn_copy": "📋 깨끗한 텍스트 복사",
    "txt_clean_placeholder": "정화된 텍스트가 여기에 표시됩니다...",
    "txt_status_clean": "순수 텍스트·지문 없음",
    "audit_header": "🔬 텍스트 심층 포렌식 보고서",
    "audit_risk_level": "AI 탐지 위험도 등급:",
    "audit_anomalies_found": "감지된 비정상 표식:",
    "audit_hidden_tags": "숨김 스타일 태그:",
    "audit_watermark_entropy": "워터마크 엔트로피 교란율:",
    "clip_header": "🛡️ 시스템 클립보드 실시간 보호기 (Scheme C)",
    "clip_desc": "백그라운드에서 상주하며, ChatGPT나 Claude에서 복사할 때 메모리에서 제로 너비 문자와 고스트 CSS 스타일을 즉시 제거합니다.",
    "clip_stream_title": "실시간 차단 로그 (Recent Intercepts)",
    "clip_btn_refresh": "🔄 새로고침",
    "clip_empty": "아직 차단된 이벤트가 없습니다. 보호를 시작한 후 텍스트를 복사하면 실시간 정화 과정을 확인할 수 있습니다.",
    "clip_item_tag": "정화 완료",
    "manual_sub": "본 매뉴얼은 체계적인 실행 절차, 기본 포렌식 원리 및 각 옵션의 최적 설정 지침을 제공합니다.",
    "manual_step1_badge": "단계 1",
    "manual_step1_title": "시스템 클립보드 실시간 보호 (Scheme C)",
    "manual_step1_body": "<strong>작동 방식:</strong> 시스템 실행 시 기본적으로 보호가 활성화되어 있습니다(우측 상단 녹색 표시). 브라우저에서 AI 텍스트를 복사하는 순간 0.5초 이내에 메모리 상에서 탈수 정화하여 배경색과 투명 문자를 제거합니다.",
    "manual_step1_tip": "💡 <strong>팁:</strong> Word나 문서 프로그램에 그대로 붙여넣어도 <code>#F7F7F8</code> 같은 채팅창 배경색이 남지 않습니다.",
    "manual_step2_badge": "단계 2",
    "manual_step2_title": "파일 드래그 정화 및 구조 생체모방 (DOCX / PDF / MD / TXT)",
    "manual_step2_body": "<strong>작동 방식:</strong> 업로드 영역으로 파일을 드래그하면 OpenXML 또는 PDF 사전 재구성 엔진이 즉시 실행됩니다:",
    "manual_step2_li1": "<strong>DOCX:</strong> 20~40개의 RSID 세션을 역주입하고, 문장부호에 따라 Runs를 분할하며, 표준 글꼴표/웹설정/테마를 합성하고 Claude 고유 태그를 제거합니다.",
    "manual_step2_li2": "<strong>PDF:</strong> Producer 및 Creator를 공식 표준(macOS Quartz 또는 Word 365)으로 덮어쓰고, 페이지별 XMP 스트림을 제거하여 실제 시간차를 모방합니다.",
    "manual_step2_li3": "<strong>Markdown:</strong> 기계적으로 정렬된 테이블 공백을 완화하고, 목록 들여쓰기를 자연화하며, AI 대화 서두와 결미를 필터링합니다.",
    "manual_step3_badge": "단계 3",
    "manual_step3_title": "심층 포렌식 정보 검증 및 안전한 다운로드",
    "manual_step3_body": "<strong>작동 방식:</strong> 처리가 완료되면 데이터 카드를 클릭하여 16진수 코드와 분할 샘플을 확인할 수 있습니다. '정화된 파일 다운로드'를 누르면 브라우저 메모리 Blob에서 직접 안전하게 다운로드됩니다.",
    "faq_header": "💡 AI 디지털 지문과 NonAI 핵심 기술 FAQ",
    "faq_q1": "Word 문서의 RSID 결함이란 무엇인가요?",
    "faq_a1": "사람이 Word에서 글을 작성할 때 멈춤, 수정, 저장할 때마다 <code>document.xml</code>에 수십 개의 RSID가 남습니다. AI 생성 문서는 이것이 0~1개뿐이어서 쉽게 식별됩니다. NonAI는 20~40개의 세션을 자연스럽게 역주입합니다.",
    "faq_q2": "AI 텍스트를 복사하면 '고스트 배경색'이 남는 이유는 무엇인가요?",
    "faq_a2": "웹 대화창에서 복사할 때 <code>&lt;span style=\"background-color: #f7f7f8\"&gt;</code> 같은 회색빛 배경과 전용 폰트가 클립보드에 묻어납니다. NonAI는 복사 즉시 순수 텍스트로 탈수 정화합니다.",
    "faq_q3": "통계적 워터마크(SynthID 등)와 신경망 탐지기를 어떻게 무력화하나요?",
    "faq_a3": "통계적 워터마크는 특정 단어 선택 확률을 조작하고, 분류기는 기계적 대구 구조와 고른 문장 길이를 감지합니다. NonAI는 n-gram 체인을 끊고 상투구를 재구성하여 자연스러운 문장 길이 편차(Burstiness)를 부여합니다.",
    "faq_q4": "NonAI는 완전한 오프라인 프라이버시를 보장하나요?",
    "faq_a4": "네. NonAI는 완전한 로컬 처리 아키텍처를 채택하고 있어 파일 처리 및 바이너리 생성이 사용자의 기기나 브라우저 메모리 내부에서만 수행되며 서버로 전송되지 않습니다.",
    "footer_text": "NonAI 2.0 • 100% 완전 오프라인 로컬 연산 • 프라이버시 보호 및 창작물 지문 방어",
    "modal_close": "닫기",
    "modal_details": {
        "rsid": {
            "title": "주입된 RSID 세션 - 심층 포렌식 분석",
            "desc": "<strong>RSID(수정 저장 식별자)란?</strong><br>Word에서 입력 정지, 삭제, 저장 시 기록되는 4바이트 16진수 태그입니다. AI 문서에는 이것이 없거나 전체 문서에 1개뿐이어서 검사 시 즉각 적발됩니다.",
            "sub": "주입된 생체모방 RSID 세션 풀 (총 {count}개)"
        },
        "runs_split": {
            "title": "Runs 프랙탈 분할 - 키보드 입력 리듬 모방",
            "desc": "<strong>왜 Runs 분할이 필요한가요?</strong><br>AI 도구는 문단 전체를 단일 연속 <code>&lt;w:r&gt;</code> 노드에 넣습니다. 인간이 타이핑할 때는 쉼표와 마침표에서 자연스러운 생각과 키 멈춤이 발생합니다. NonAI는 <strong>{count}</strong>곳의 문장부호에서 자연스럽게 분할했습니다.",
            "sub": "분할 샘플",
            "sample_desc": "긴 텍스트 노드가 실제 인간의 입력 휴지기 간격으로 분할되었습니다."
        },
        "claude_purged": {
            "title": "AI 고유 서명 제거 - 출처 지문 완전 멸균",
            "desc": "<strong>해결된 치명적 결함: 파일 자체의 AI 자백 표식</strong><br>Claude Docs 등은 내보낼 때 <code>docProps/core.xml</code>의 <code>&lt;dc:description&gt;</code>에 <code>Claude Docs node/...</code>를 남기고 <code>customXml/</code>을 포함합니다. 탐지기는 이를 추측이 아닌 확정 출처로 인식합니다.",
            "sub": "실행된 포렌식 제거 항목",
            "items": [
                "<strong>태그 제거:</strong> <code>&lt;dc:description&gt;</code>를 완전히 삭제하고 불필요한 키워드와 주제를 비움.",
                "<strong>사용자 지정 패키지 삭제:</strong> <code>customXml/</code> 및 <code>docProps/custom.xml</code> 완전 배제.",
                "<strong>전체 문자열 정화:</strong> XML 스트림 전체를 검사하여 <code>Claude Docs</code>, <code>Anthropic</code>, <code>ChatGPT</code> 등의 표식을 소멸."
            ]
        },
        "pkg_synthesized": {
            "title": "Word 표준 패키지 구조화 - 무결성 복원",
            "desc": "<strong>해결된 치명적 결함: Word 공식 패키지 구조 결락</strong><br>정품 Word로 저장한 파일에는 <code>fontTable.xml</code>(글꼴표), <code>webSettings.xml</code>(웹설정), <code>theme1.xml</code>(테마)이 필수입니다. AI 파일은 이것이 없어 'Word 명칭 사칭'으로 판정되었습니다.",
            "sub": "자동 합성된 Microsoft 표준 패키지 구성요소",
            "items": [
                "<code>word/fontTable.xml</code>: Calibri, Times New Roman, 맑은 고딕 등의 표준 글꼴표.",
                "<code>word/webSettings.xml</code>: 브라우저 최적화 및 PNG 지원 플래그.",
                "<code>word/theme/theme1.xml</code>: Office 공식 표준 색상 및 글꼴 체계.",
                "<code>[Content_Types].xml</code> 및 <code>document.xml.rels</code>: 합법적 스키마 바인딩 완료."
            ]
        },
        "semantic": {
            "title": "문장 패턴 및 어휘 탈특징화 - Transformer 신경망 차단",
            "desc": "<strong>해결된 결함: 신경망 분류기의 기계적 패턴 탐지</strong><br>OmniTraces 등 분류기는 텍스트 복잡도(Perplexity) 분포와 획일적 병렬 구조를 포착합니다. NonAI는 경직된 AI 표현을 자연스러운 전문 문맥으로 재구성합니다.",
            "sub": "신경망 교란 및 최적화 지표",
            "items": [
                "<strong>AI 상투구 및 경직된 문장 재구성:</strong> 총 {replacements}곳",
                "<strong>문장 길이 편차 및 세미콜론 리듬 최적화:</strong> 총 {reorganized}개 절",
                "<strong>N-gram 예측 체인 단절:</strong> SynthID 그린 리스트 통계적 유의성 무력화"
            ]
        },
        "ghost_styles": {
            "title": "웹 고스트 스타일/배경색 제거 - 대화창 서식 정화",
            "desc": "<strong>채팅창에서 묻어난 고스트 색상:</strong><br>웹에서 복사할 때 <code>#F7F7F8</code> 등의 배경색이 <code>&lt;w:shd&gt;</code>에 남는 문제를 해결하고 깨끗한 문서 스타일로 복원했습니다.",
            "sub": "제거된 고스트 스타일 및 폰트 항목"
        },
        "unicode": {
            "title": "제로 너비 Unicode 제거 - 비가시 워터마크 소멸",
            "desc": "<strong>보이지 않는 바코드 워터마크:</strong><br>일부 AI 시스템은 제로 너비 공백(ZWSP) 등을 무작위로 삽입하여 출처를 추적합니다. NonAI는 한글 문장부호를 완벽히 보호하면서 투명 마크만 제거합니다.",
            "before_label": "감지된 비정상 문자",
            "after_label": "정화 후 상태",
            "clean_status": "100% 순수 표준 NFC 인코딩"
        },
        "human_time": {
            "title": "위장 타이핑 소요 시간 - 타임라인 생체모방",
            "desc": "<strong>작성 소요 시간 결함:</strong><br>AI 생성 파일은 대개 <code>&lt;TotalTime&gt;0&lt;/TotalTime&gt;</code>으로 남아있습니다. NonAI는 글자 수에 기반하여 자연스러운 작성 및 생각 시간을 부여합니다.",
            "sub": "생체모방 타임라인 모델",
            "items": [
                "<strong>추정 작성 소요 시간:</strong> {minutes}분 (분당 32~35자 및 생각 멈춤 반영)",
                "<strong>수정 판올림 수:</strong> 제 {revision}회 수정",
                "<strong>생성 일시:</strong> {created}",
                "<strong>최종 수정 일시:</strong> {modified}"
            ]
        },
        "app_spoofed": {
            "title": "위장 애플리케이션 - 메타데이터 덮어쓰기",
            "desc": "<strong>애플리케이션 메타데이터:</strong><br>python-docx 등 오픈소스 식별자를 공식 Microsoft Office Word 속성으로 치환했습니다.",
            "code_title": "정상화된 docProps XML 속성"
        },
        "pdf_producer": {
            "title": "PDF 메타데이터 및 XMP 스트림 정화",
            "desc": "<strong>PDF 생성 프로그램 위장:</strong><br>wkhtmltopdf, Chromium 등을 공식 가상 프린터로 교체하고 페이지별 XMP 스트림을 제거했습니다.",
            "orig_producer": "원래 Producer",
            "spoofed_producer": "위장 후 Producer",
            "spoofed_creator": "위장 후 Creator"
        },
        "markdown": {
            "title": "Markdown 구조 탈특징화 - 자연스러운 서식",
            "desc": "<strong>기계적으로 완벽한 Markdown 서식 완화:</strong><br>과도하게 정렬된 표 공백을 자연스러운 간결 형태로 되돌리고 목록 기호를 무작위로 조율합니다."
        }
    }
}

# 6. th (ภาษาไทย)
DATA["th"] = {
    "app_title": "NonAI - ระบบลบลายพิมพ์นิ้วมือดิจิทัลและร่องรอย AI",
    "brand_sub": "ระบบกำจัดลายน้ำ เมทาดาตา และร่องรอยการสังเคราะห์ของ AI ในระดับโครงสร้างไฟล์",
    "watcher_label": "ระบบเฝ้าระวังคลิปบอร์ด (Scheme C)",
    "watcher_active": "กำลังตรวจจับแบบเรียลไทม์",
    "watcher_inactive": "ไม่ได้เริ่มการทำงาน",
    "watcher_btn_start": "เริ่มการป้องกัน",
    "watcher_btn_stop": "หยุดการป้องกัน",
    "watcher_running": "ระบบกำลังทำงาน (ทำความสะอาดข้อความที่คัดลอกโดยอัตโนมัติ)",
    "watcher_stopped": "ระบบหยุดทำงาน",
    "tab_files": "📁 พื้นที่ทำความสะอาดไฟล์ (.docx, .pdf, .md, .txt)",
    "tab_text": "✍️ ตรวจสอบข้อความและ Hex แบบเรียลไทม์",
    "tab_clipboard": "📋 บันทึกกิจกรรมคลิปบอร์ด",
    "tab_manual": "📖 คู่มือการใช้งานและการตรวจพิสูจน์",
    "drop_title": "ลากไฟล์มาวางที่นี่ หรือคลิกเพื่อเลือกไฟล์",
    "drop_subtitle": "รองรับรูปแบบ: Word (.docx), PDF (.pdf), Markdown (.md), ข้อความล้วน (.txt)",
    "tag_rsid": "การจำลองประวัติ RSID ใน DOCX",
    "tag_pdf": "การจำลองเมทาดาตา XMP ใน PDF",
    "tag_css": "การลบสีพื้นหลังแฝงจากเว็บ CSS",
    "tag_unicode": "การล้างอักขระล่องหน Unicode Zero-Width",
    "adv_title": "⚙️ การตั้งค่าพารามิเตอร์จำลองขั้นสูง (DOCX / PDF / การรบกวนทางสถิติ)",
    "lbl_author": "จำลองชื่อผู้เขียนเอกสาร (Author):",
    "hint_author": "บันทึกลงในฟิลด์ผู้เขียนของ Word docProps/core.xml",
    "lbl_rsid": "จำนวนประวัติเซสชัน RSID ใน DOCX:",
    "hint_rsid": "จำลองจำนวนครั้งในการบันทึกและช่วงเวลาหยุดคิดขณะพิมพ์",
    "lbl_pdf": "โปรแกรมต้นทาง PDF ที่ต้องการจำลอง:",
    "lbl_perturb": "เปิดใช้งานการรบกวนลายน้ำทางสถิติ (ตัดวงจร n-gram, ปรับคำพ้อง)",
    "btn_timing": "ℹ️ เวลาที่เหมาะสม",
    "btn_timing_title": "คลิกเพื่อดูคำแนะนำจังหวะการใช้งาน",
    "timing_popover_heading": "💡 คำแนะนำจังหวะการใช้งาน",
    "timing_author_title": "💡 เวลาที่เหมาะสม: การจำลองชื่อผู้เขียนเอกสาร",
    "timing_author_desc": "【เมื่อใดควรใช้】การส่งเอกสารวิชาการหรือรายงานเพื่อป้องกันไม่ให้ระบุว่าเป็น ChatGPT หรือไลบรารีโอเพนซอร์ส<br>【คำแนะนำ】ใส่นามสกุลจริง ชื่อย่อองค์กร หรือ Author<br>【ผลลัพธ์】เขียนทับ dc:creator และ cp:lastModifiedBy ใน docProps/core.xml",
    "timing_rsid_title": "💡 เวลาที่เหมาะสม: การใส่ประวัติ RSID ใน DOCX",
    "timing_rsid_desc": "【เมื่อใดควรใช้】เมื่อต้องการผ่านการตรวจสอบเอกสาร ไฟล์ Word ที่ AI สร้างขึ้นมักมี RSID เพียง 0-1 ชุด<br>【คำแนะนำ】บทความสั้นใช้ 15-20 ชุด รายงานขนาดยาวใช้ 25-40 ชุด<br>【ผลลัพธ์】ใส่ชุดเซสชันลงใน settings.xml และตัดทอน runs เลียนแบบจังหวะพิมพ์ของมนุษย์",
    "timing_pdf_title": "💡 เวลาที่เหมาะสม: โปรแกรมต้นทาง PDF ที่ต้องการจำลอง",
    "timing_pdf_desc": "【เมื่อใดควรใช้】เมื่อต้องแชร์ไฟล์ PDF สู่ภายนอกโดยไม่ให้ตรวจพบ Chromium หรือ python-pdf-lib<br>【คำแนะนำ】ผู้ใช้ Mac แนะนำ macOS Quartz ผู้ใช้ Windows แนะนำ Microsoft Word<br>【ผลลัพธ์】จำลอง Producer และ Creator พร้อมล้างสตรีม XMP ทั้งหมด",
    "timing_perturb_title": "💡 เวลาที่เหมาะสม: การรบกวนลายน้ำทางสถิติ",
    "timing_perturb_desc": "【เมื่อใดควรใช้】เมื่อสงสัยว่ามีลายน้ำความน่าจะเป็นของ Google SynthID หรือต้องผ่านเครื่องมือตรวจจับ AI<br>【คำแนะนำ】แนะนำให้เปิดใช้งานเสมอ<br>【ผลลัพธ์】แทนที่สำนวนยอดนิยมของ AI ตัดวงจร n-gram และลดความแม่นยำของโมเดลตรวจจับ",
    "res_clean_prefix": "✅ ทำความสะอาดเสร็จสมบูรณ์: ",
    "res_desc": "โครงสร้างไฟล์ได้รับการสร้างขึ้นใหม่ด้วยคุณลักษณะธรรมชาติของมนุษย์และเมทาดาตาที่สะอาด",
    "btn_download": "💾 ดาวน์โหลดไฟล์ที่ทำความสะอาดแล้ว",
    "stat_rsid_injected": "เซสชัน RSID ที่ใส่เพิ่ม",
    "stat_runs_split": "การตัดแบ่ง Runs ตามจังหวะ",
    "stat_ai_purged": "ล้างลายเซ็น AI ทั้งหมด",
    "stat_pkg_synthesized": "โครงสร้างแพ็กเกจ Word",
    "stat_semantic_perturbs": "ขจัดรูปแบบประโยค AI",
    "stat_ghost_removed": "ล้างรูปแบบ/สีพื้นหลังแฝง",
    "stat_unicode_removed": "ลบอักขระล่องหน Unicode",
    "stat_human_minutes": "เวลาจำลองในการพิมพ์",
    "stat_app_spoofed": "โปรแกรมจำลอง",
    "stat_inspect_hint": "🔍 คลิกเพื่อดูรายละเอียดการทำงาน",
    "unit_sessions": "เซสชัน",
    "unit_splits": "จุดแบ่ง",
    "unit_purged": "รายการล้าง",
    "unit_parts": "ส่วนประกอบมาตรฐาน",
    "unit_replacements": "จุดปรับปรุง",
    "unit_styles": "จุดแก้ไข",
    "unit_chars": "ตัวอักษร",
    "unit_minutes": "นาที",
    "txt_raw_header": "ข้อความต้นฉบับ / สิ่งที่วาง",
    "txt_btn_paste": "📋 วางจากคลิปบอร์ด",
    "txt_btn_clear": "ล้างข้อความ",
    "txt_raw_placeholder": "วางข้อความที่สร้างจาก ChatGPT หรือ Claude ที่นี่ ระบบจะวิเคราะห์อักขระล่องหนและโค้ดแฝง...",
    "txt_char_count": "จำนวนตัวอักษร: ",
    "txt_alert_anomaly": "⚠️ ตรวจพบอักขระผิดปกติแฝงอยู่!",
    "txt_clean_header": "ผลลัพธ์หลังทำความสะอาดและลบรอยนิ้วมือ",
    "txt_btn_copy": "📋 คัดลอกข้อความสะอาด",
    "txt_clean_placeholder": "ข้อความที่ทำความสะอาดแล้วจะปรากฏที่นี่...",
    "txt_status_clean": "ข้อความบริสุทธิ์ ไม่มีรอยนิ้วมือ",
    "audit_header": "🔬 รายงานการตรวจพิสูจน์ข้อความ",
    "audit_risk_level": "ระดับความเสี่ยงในการตรวจพบ AI:",
    "audit_anomalies_found": "ตรวจพบร่องรอยผิดปกติ:",
    "audit_hidden_tags": "แท็กสไตล์ที่ซ่อนอยู่:",
    "audit_watermark_entropy": "อัตราการรบกวนลายน้ำ:",
    "clip_header": "🛡️ ระบบเฝ้าระวังคลิปบอร์ดแบบเรียลไทม์ (Scheme C)",
    "clip_desc": "ทำงานเบื้องหลัง เมื่อคัดลอกข้อความจาก ChatGPT หรือ Claude ระบบจะลบอักขระล่องหนและสไตล์แฝงในหน่วยความจำทันที",
    "clip_stream_title": "บันทึกการตรวจจับล่าสุด (Recent Intercepts)",
    "clip_btn_refresh": "🔄 รีเฟรช",
    "clip_empty": "ยังไม่มีเหตุการณ์ตรวจจับในคลิปบอร์ด เมื่อเริ่มการทำงาน ให้ลองคัดลอกข้อความเพื่อดูผลการทำความสะอาด",
    "clip_item_tag": "ทำความสะอาดแล้ว",
    "manual_sub": "คู่มือนี้ให้ขั้นตอนการทำงานที่ชัดเจน อธิบายหลักการทางนิติวิทยาศาสตร์ของไฟล์ และการตั้งค่าที่เหมาะสม",
    "manual_step1_badge": "ขั้นตอนที่ 1",
    "manual_step1_title": "การปกป้องคลิปบอร์ดแบบเรียลไทม์ (Scheme C)",
    "manual_step1_body": "<strong>การทำงาน:</strong> ระบบจะเปิดทำงานตามค่าเริ่มต้นเมื่อโหลดหน้าเว็บ (ไฟสีเขียวด้านบนขวา) เมื่อคัดลอกข้อความ AI ระบบจะล้างอักขระล่องหนและสีพื้นหลังแฝงภายใน 0.5 วินาที",
    "manual_step1_tip": "💡 <strong>คำแนะนำ:</strong> สามารถวางลงใน Word ได้ทันทีโดยไม่ติดสีพื้นหลังแชท เช่น <code>#F7F7F8</code>",
    "manual_step2_badge": "ขั้นตอนที่ 2",
    "manual_step2_title": "การลากไฟล์เพื่อทำความสะอาดและจำลองโครงสร้าง (DOCX / PDF / MD / TXT)",
    "manual_step2_body": "<strong>การทำงาน:</strong> ลากไฟล์มาวางในพื้นที่อัปโหลด ระบบจะเริ่มเครื่องมือสร้างโครงสร้างไฟล์ใหม่ตามรูปแบบ:",
    "manual_step2_li1": "<strong>DOCX:</strong> ใส่ประวัติ RSID 20-40 ชุด ตัดแบ่ง Runs ตามเครื่องหมายวรรคตอน สังเคราะห์ตารางฟอนต์มาตรฐาน การตั้งค่าเว็บ และธีม พร้อมล้างลายเซ็นของ Claude/ChatGPT",
    "manual_step2_li2": "<strong>PDF:</strong> เขียนทับ Producer และ Creator เป็นมาตรฐานระบบ ลบสตรีม XMP และจำลองเวลาสร้างเอกสารย้อนหลังอย่างสมจริง",
    "manual_step2_li3": "<strong>Markdown:</strong> ปรับระยะตารางที่ตรงเกินไปให้เป็นธรรมชาติ และตัดคำเกริ่นนำหรือคำลงท้ายของ AI",
    "manual_step3_badge": "ขั้นตอนที่ 3",
    "manual_step3_title": "การตรวจสอบข้อมูลเชิงลึกและการดาวน์โหลดอย่างปลอดภัย",
    "manual_step3_body": "<strong>การทำงาน:</strong> เมื่อประมวลผลเสร็จสิ้น คลิกการ์ดข้อมูลเพื่อดูรหัสฐานสิบหกและตัวอย่างการตัดแบ่ง การคลิก 'ดาวน์โหลดไฟล์' จะสร้างไฟล์จากหน่วยความจำ Blob ของเบราว์เซอร์โดยตรง ปลอดภัยและรวดเร็ว",
    "faq_header": "💡 คำถามที่พบบ่อยเกี่ยวกับร่องรอย AI และ NonAI",
    "faq_q1": "ข้อบกพร่องของ RSID ในไฟล์ Word ที่สร้างโดย AI คืออะไร?",
    "faq_a1": "เมื่อมนุษย์พิมพ์ Word จะเกิดรหัส RSID บันทึกใน <code>document.xml</code> ทุกครั้งที่หยุด คิด หรือบันทึก แต่ไฟล์จาก AI มักมี RSID เพียง 0 หรือ 1 ชุด NonAI จะสร้างชุดเซสชันจำลอง 20-40 ชุดเพื่อลบร่องรอยนี้",
    "faq_q2": "เหตุใดการคัดลอกข้อความ AI จึงติดสีพื้นหลังแปลกๆ?",
    "faq_a2": "การคัดลอกจากหน้าต่างเว็บจะดึงโค้ด HTML <code>&lt;span style=\"background-color: #f7f7f8\"&gt;</code> มาด้วย ทำให้ฝังในไฟล์ Word โดยถาวร NonAI จะลบสีพื้นหลังแปลกปลอมออกให้หมด",
    "faq_q3": "NonAI ต้านทานลายน้ำทางสถิติ (เช่น SynthID) และเครื่องมือตรวจจับได้อย่างไร?",
    "faq_a3": "ลายน้ำทางสถิติจะปรับความน่าจะเป็นของการเลือกคำ และเครื่องมือตรวจจับจะจับคู่โครงสร้างประโยคที่ตายตัว NonAI จะตัดวงจร n-gram และปรับจังหวะประโยคให้มีความผันแปรอย่างเป็นธรรมชาติ",
    "faq_q4": "NonAI รับประกันความเป็นส่วนตัวและการทำงานแบบออฟไลน์หรือไม่?",
    "faq_a4": "ใช่ NonAI ทำงานแบบออฟไลน์ในเครื่องของคุณอย่างสมบูรณ์ ข้อมูลไฟล์และการประมวลผลทั้งหมดเกิดขึ้นบนคอมพิวเตอร์หรือในหน่วยความจำเบราว์เซอร์ของคุณ ไม่มีการส่งไปเก็บยังเซิร์ฟเวอร์ภายนอก",
    "footer_text": "NonAI 2.0 • ประมวลผลแบบออฟไลน์ 100% บนเครื่องของคุณ • ปลอดภัยและเป็นส่วนตัว",
    "modal_close": "ปิดหน้าต่าง",
    "modal_details": {
        "rsid": {
            "title": "เซสชัน RSID ที่ใส่เพิ่ม - รายละเอียดการตรวจพิสูจน์",
            "desc": "<strong>RSID คืออะไร?</strong><br>รหัสระบุการบันทึกการแก้ไขใน Word ซึ่งบันทึกทุกครั้งที่มีการพิมพ์ ลบ หรือบันทึก ไฟล์จาก AI มักไม่มีรหัสดังกล่าว ซึ่งทำให้ถูกตรวจพบได้ง่าย",
            "sub": "ชุดเซสชัน RSID จำลองที่สร้างขึ้น (ทั้งหมด {count} ชุด)"
        },
        "runs_split": {
            "title": "การตัดแบ่ง Runs ตามจังหวะ - จำลองการกดแป้นพิมพ์",
            "desc": "<strong>ทำไมต้องแบ่ง Runs?</strong><br>เครื่องมือ AI มักรวมทั้งย่อหน้าไว้ในโหนด <code>&lt;w:r&gt;</code> เดียว ในขณะที่มนุษย์จะมีจังหวะหยุดพักตามเครื่องหมายวรรคตอน NonAI ได้ตัดแบ่งที่เครื่องหมายวรรคตอนจำนวน <strong>{count}</strong> จุด",
            "sub": "ตัวอย่างการตัดแบ่ง",
            "sample_desc": "ข้อความยาวถูกแบ่งออกเป็นช่วงจังหวะการพิมพ์ที่สมจริง"
        },
        "claude_purged": {
            "title": "ล้างลายเซ็น AI ทั้งหมด - กำจัดร่องรอยต้นกำเนิด",
            "desc": "<strong>แก้ไขข้อบกพร่องสำคัญ: การประกาศแหล่งที่มาของ AI ในไฟล์</strong><br>เครื่องมืออย่าง Claude Docs จะใส่แท็ก <code>Claude Docs node/...</code> ลงใน <code>docProps/core.xml</code> ซึ่งเป็นหลักฐานชัดเจนว่าสร้างโดย AI",
            "sub": "รายการที่ดำเนินการลบ",
            "items": [
                "<strong>ลบแท็ก:</strong> นำแท็ก <code>&lt;dc:description&gt;</code> ออก และล้างคำค้นหาและหัวข้อที่ผิดปกติ",
                "<strong>ลบแพ็กเกจพิเศษ:</strong> กำจัดโฟลเดอร์ <code>customXml/</code> และ <code>docProps/custom.xml</code> ทั้งหมด",
                "<strong>สแกนข้อความทั้งระบบ:</strong> ตรวจสอบสตรีม XML เพื่อลบร่องรอย <code>Claude Docs</code>, <code>Anthropic</code>, <code>ChatGPT</code>"
            ]
        },
        "pkg_synthesized": {
            "title": "โครงสร้างแพ็กเกจ Word - ความสมบูรณ์ของไฟล์",
            "desc": "<strong>แก้ไขข้อบกพร่องสำคัญ: ส่วนประกอบ Word ขาดหาย</strong><br>ไฟล์ที่บันทึกจาก Microsoft Word แท้จะต้องมี <code>fontTable.xml</code>, <code>webSettings.xml</code> และ <code>theme1.xml</code> ไฟล์จาก AI ที่ขาดสิ่งเหล่านี้จะถูกระบุว่าเป็นการปลอมแปลง",
            "sub": "ส่วนประกอบมาตรฐาน Microsoft ที่สังเคราะห์ขึ้น",
            "items": [
                "<code>word/fontTable.xml</code>: ตารางฟอนต์มาตรฐาน",
                "<code>word/webSettings.xml</code>: การตั้งค่าเบราว์เซอร์และการรองรับ PNG",
                "<code>word/theme/theme1.xml</code>: โครงสร้างสีและแบบอักษรมาตรฐานของ Office",
                "<code>[Content_Types].xml</code> และ <code>document.xml.rels</code>: ผูกความสัมพันธ์ตามมาตรฐานสมบูรณ์"
            ]
        },
        "semantic": {
            "title": "ขจัดรูปแบบประโยค AI - เกราะป้องกัน Transformer",
            "desc": "<strong>แก้ไขข้อบกพร่อง: การตรวจจับโครงสร้างประโยค AI</strong><br>เครื่องมือตรวจจับอาศัยการกระจายความซับซ้อนของคำและรูปแบบประโยคคู่ขนานที่ตายตัว NonAI ปรับปรุงสำนวนให้ลื่นไหลและเป็นธรรมชาติของมนุษย์",
            "sub": "ตัวชี้วัดการปรับปรุงภาษา",
            "items": [
                "<strong>ปรับสำนวนที่ตายตัวของ AI:</strong> ทั้งหมด {replacements} จุด",
                "<strong>ปรับจังหวะความยาวประโยค:</strong> ทั้งหมด {reorganized} ส่วน",
                "<strong>ตัดวงจรการทำนาย n-gram:</strong> ลดความเด่นชัดทางสถิติของ SynthID"
            ]
        },
        "ghost_styles": {
            "title": "ล้างรูปแบบ/สีพื้นหลังแฝง - ทำความสะอาดสไตล์เว็บ",
            "desc": "<strong>สีพื้นหลังแฝงจากคลิปบอร์ด:</strong><br>การคัดลอกจากหน้าเว็บมักนำสี <code>#F7F7F8</code> ติดมาด้วย NonAI ได้ลบสไตล์ที่ไม่จำเป็นออกและคืนค่ารูปแบบดั้งเดิมที่สะอาด",
            "sub": "รายการสไตล์และฟอนต์แฝงที่ลบออก"
        },
        "unicode": {
            "title": "ลบอักขระล่องหน Unicode - ขจัดลายน้ำแฝง",
            "desc": "<strong>บาร์โค้ดล่องหน:</strong><br>ระบบ AI บางระบบใส่อักขระ Zero-Width เพื่อติดตามการใช้งาน NonAI ลบอักขระเหล่านี้ออกทั้งหมดโดยยังคงรักษาเครื่องหมายวรรคตอนไว้อย่างครบถ้วน",
            "before_label": "อักขระผิดปกติที่พบ",
            "after_label": "สถานะหลังทำความสะอาด",
            "clean_status": "รหัส NFC มาตรฐาน สะอาด 100%"
        },
        "human_time": {
            "title": "เวลาจำลองในการพิมพ์ - สร้างไทม์ไลน์สมจริง",
            "desc": "<strong>ข้อบกพร่องเรื่องเวลาในการพิมพ์:</strong><br>ไฟล์จาก AI มักแสดงเวลาการพิมพ์เป็น 0 นาที NonAI คำนวณเวลาที่สมเหตุสมผลตามจำนวนคำเพื่อจำลองการพิมพ์จริง",
            "sub": "โมเดลการคำนวณเวลาเสมือนจริง",
            "items": [
                "<strong>เวลาจำลอง:</strong> {minutes} นาที (คำนวณจากความเร็ว 32-35 คำ/นาที รวมช่วงหยุดคิด)",
                "<strong>ลำดับการแก้ไข:</strong> ครั้งที่ {revision}",
                "<strong>เวลาสร้าง:</strong> {created}",
                "<strong>เวลาแก้ไขล่าสุด:</strong> {modified}"
            ]
        },
        "app_spoofed": {
            "title": "โปรแกรมจำลอง - การเขียนทับเมทาดาตา",
            "desc": "<strong>เมทาดาตาของโปรแกรม:</strong><br>แทนที่ชื่อไลบรารีโอเพนซอร์สด้วยคุณสมบัติทางการของ Microsoft Office Word",
            "code_title": "โครงสร้าง docProps XML ที่ถูกต้อง"
        },
        "pdf_producer": {
            "title": "การล้างเมทาดาตา PDF และสตรีม XMP",
            "desc": "<strong>การจำลองโปรแกรมสร้าง PDF:</strong><br>แทนที่ wkhtmltopdf หรือ Chromium ด้วยระบบเครื่องพิมพ์เสมือนจริง และล้างสตรีม XMP ในทุกหน้า",
            "orig_producer": "Producer เดิม",
            "spoofed_producer": "Producer ที่จำลอง",
            "spoofed_creator": "Creator ที่จำลอง"
        },
        "markdown": {
            "title": "การผ่อนคลายโครงสร้าง Markdown - การจัดรูปแบบธรรมชาติ",
            "desc": "<strong>โครงสร้างที่ตรงเกินไปของ Markdown:</strong><br>ตารางและรายการที่สร้างจาก AI มักมีความสม่ำเสมอเกินไป NonAI ปรับให้กระชับและเป็นธรรมชาติเหมือนมนุษย์เขียน"
        }
    }
}

# 7. ru (Русский)
DATA["ru"] = {
    "app_title": "NonAI - Удаление цифровых отпечатков и следов ИИ",
    "brand_sub": "Глубокая очистка водяных знаков ИИ, метаданных и синтетических артефактов",
    "watcher_label": "Монитор буфера обмена (Scheme C)",
    "watcher_active": "Активный перехват",
    "watcher_inactive": "Не активен",
    "watcher_btn_start": "Включить защиту",
    "watcher_btn_stop": "Остановить",
    "watcher_running": "Защита активна (автоочистка при копировании)",
    "watcher_stopped": "Защита отключена",
    "tab_files": "📁 Очистка файлов (.docx, .pdf, .md, .txt)",
    "tab_text": "✍️ Текст и Hex-анализ в реальном времени",
    "tab_clipboard": "📋 Журнал буфера обмена",
    "tab_manual": "📖 Руководство и экспертиза",
    "drop_title": "Перетащите файлы сюда или нажмите для выбора",
    "drop_subtitle": "Поддерживаемые форматы: Word (.docx), PDF (.pdf), Markdown (.md), Текст (.txt)",
    "tag_rsid": "Биомиметическая инъекция RSID в DOCX",
    "tag_pdf": "Маскировка метаданных XMP в PDF",
    "tag_css": "Удаление скрытых стилей и цветов CSS",
    "tag_unicode": "Очистка невидимых символов Unicode",
    "adv_title": "⚙️ Расширенные параметры биомиметики (DOCX / PDF / Пертурбация)",
    "lbl_author": "Подмена автора документа (Author):",
    "hint_author": "Записывается в поля автора Word docProps/core.xml",
    "lbl_rsid": "Количество сессий RSID для DOCX:",
    "hint_rsid": "Имитирует паузы при наборе текста и количество сохранений",
    "lbl_pdf": "Целевой генератор PDF:",
    "lbl_perturb": "Включить пертурбацию водяных знаков (разрыв n-грамм, синонимы)",
    "btn_timing": "ℹ️ Когда применять",
    "btn_timing_title": "Показать рекомендации по применению",
    "timing_popover_heading": "💡 Руководство по применению",
    "timing_author_title": "💡 Применение: Подмена автора документа",
    "timing_author_desc": "【Когда использовать】При подаче научных статей или отчетов, чтобы исключить упоминание ChatGPT или библиотек.<br>【Рекомендация】Укажите свое имя, организацию или Author.<br>【Эффект】Перезаписывает dc:creator и cp:lastModifiedBy в docProps/core.xml.",
    "timing_rsid_title": "💡 Применение: Инъекция сессий RSID в DOCX",
    "timing_rsid_desc": "【Когда использовать】Для прохождения экспертизы документов. В файлах от ИИ обычно всего 0–1 RSID, что является явным маркером генерации.<br>【Рекомендация】15–20 для небольших заметок, 25–40 для диссертаций.<br>【Эффект】Внедряет цепочки сессий в settings.xml и разбивает фрагменты текста (runs), имитируя паузы при наборе.",
    "timing_pdf_title": "💡 Применение: Целевой генератор PDF",
    "timing_pdf_desc": "【Когда использовать】При передаче PDF третьим лицам, чтобы скрыть следы Chromium, Skia или python-pdf-lib.<br>【Рекомендация】Для macOS — macOS Quartz, для Windows — Microsoft Word.<br>【Эффект】Подменяет Producer и Creator, полностью очищая потоки XMP.",
    "timing_perturb_title": "💡 Применение: Пертурбация водяных знаков",
    "timing_perturb_desc": "【Когда использовать】При риске наличия водяных знаков Google SynthID или строгой проверке детекторами ИИ.<br>【Рекомендация】Настоятельно рекомендуется держать включенным.<br>【Эффект】Заменяет шаблонные штампы ИИ, разрывает n-граммы и снижает статистическую вероятность генерации.",
    "res_clean_prefix": "✅ Очистка завершена: ",
    "res_desc": "Структура файла перестроена с человеческими биомиметическими паттернами и чистыми метаданными",
    "btn_download": "💾 Скачать очищенный файл",
    "stat_rsid_injected": "Внедрено сессий RSID",
    "stat_runs_split": "Разбиений фрагментов Runs",
    "stat_ai_purged": "Удаление следов ИИ",
    "stat_pkg_synthesized": "Структура пакета Word",
    "stat_semantic_perturbs": "Депаттернизация семантики",
    "stat_ghost_removed": "Удалено скрытых стилей CSS",
    "stat_unicode_removed": "Удалено невидимых символов Unicode",
    "stat_human_minutes": "Имитированное время набора",
    "stat_app_spoofed": "Поддельное приложение",
    "stat_inspect_hint": "🔍 Нажмите для подробного отчета",
    "unit_sessions": "сессий",
    "unit_splits": "разбиений",
    "unit_purged": "очищено",
    "unit_parts": "компонентов",
    "unit_replacements": "оптимизаций",
    "unit_styles": "стилей",
    "unit_chars": "символов",
    "unit_minutes": "мин",
    "txt_raw_header": "Исходный текст / Вставка",
    "txt_btn_paste": "📋 Вставить",
    "txt_btn_clear": "Очистить",
    "txt_raw_placeholder": "Вставьте текст, сгенерированный ChatGPT, Claude и т.д. Система автоматически найдет скрытые невидимые символы...",
    "txt_char_count": "Символов: ",
    "txt_alert_anomaly": "⚠️ Обнаружены скрытые маркеры!",
    "txt_clean_header": "Результат очистки",
    "txt_btn_copy": "📋 Копировать чистый текст",
    "txt_clean_placeholder": "Очищенный текст появится здесь...",
    "txt_status_clean": "100% чистый текст без отпечатков",
    "audit_header": "🔬 Экспертный отчет по тексту",
    "audit_risk_level": "Уровень риска детекции ИИ:",
    "audit_anomalies_found": "Обнаружено скрытых меток:",
    "audit_hidden_tags": "Скрытые теги стилей:",
    "audit_watermark_entropy": "Коэффициент пертурбации:",
    "clip_header": "🛡️ Монитор буфера обмена (Scheme C)",
    "clip_desc": "Работает в фоне. При копировании текста из ChatGPT или Claude мгновенно удаляет невидимые пробелы и фоновые стили CSS.",
    "clip_stream_title": "Журнал перехватов (Recent Intercepts)",
    "clip_btn_refresh": "🔄 Обновить",
    "clip_empty": "Событий пока нет. Включите монитор и скопируйте текст ИИ для проверки работы.",
    "clip_item_tag": "Очищено",
    "manual_sub": "В данном руководстве последовательно изложены этапы работы, принципы экспертизы документов и точные настройки.",
    "manual_step1_badge": "Этап 1",
    "manual_step1_title": "Мониторинг буфера обмена (Scheme C)",
    "manual_step1_body": "<strong>Принцип работы:</strong> Монитор активен по умолчанию при загрузке (зеленый индикатор вверху). При копировании текста ИИ в браузере он за 0,5 секунды удаляет скрытые символы и фон.",
    "manual_step1_tip": "💡 <strong>Совет:</strong> При вставке в Word не останется серых рамок чата вроде <code>#F7F7F8</code>.",
    "manual_step2_badge": "Этап 2",
    "manual_step2_title": "Очистка файлов и биомиметика (DOCX / PDF / MD / TXT)",
    "manual_step2_body": "<strong>Принцип работы:</strong> Перетащите файл в зону загрузки для автоматической реконструкции структуры:",
    "manual_step2_li1": "<strong>DOCX:</strong> Внедряет пул из 20–40 сессий RSID, разделяет фрагменты текста по знакам препинания, синтезирует таблицы шрифтов, настройки и удаляет метатеги Claude/ChatGPT.",
    "manual_step2_li2": "<strong>PDF:</strong> Подменяет Producer и Creator на стандартные системные, удаляет потоки XMP со страниц и формирует естественную разницу во времени создания.",
    "manual_step2_li3": "<strong>Markdown:</strong> Устраняет машинное выравнивание пробелов в таблицах и отсекает шаблонные вводные и заключительные фразы ИИ.",
    "manual_step3_badge": "Этап 3",
    "manual_step3_title": "Анализ отчета и безопасное скачивание",
    "manual_step3_body": "<strong>Принцип работы:</strong> Нажмите на любую карточку статистики для просмотра 16-ричных кодов и примеров разбиения. Кнопка 'Скачать' отдает файл напрямую из памяти браузера Blob без задержек.",
    "faq_header": "💡 Часто задаваемые вопросы об отпечатках ИИ и NonAI",
    "faq_q1": "В чем заключается уязвимость RSID в файлах Word от ИИ?",
    "faq_a1": "При реальном наборе текста человеком в <code>document.xml</code> сохраняются десятки меток RSID. Файлы от ИИ генерируются за один проход и имеют 0 или 1 RSID. NonAI внедряет 20–40 сессий и фрагментирует текстовые узлы.",
    "faq_q2": "Почему при копировании текста ИИ остается скрытый фоновый цвет?",
    "faq_a2": "При копировании из веб-интерфейса в буфер попадает HTML <code>&lt;span style=\"background-color: #f7f7f8\"&gt;</code>, который въедается в структуру документа. NonAI нейтрализует этот фон.",
    "faq_q3": "Как NonAI защищает от водяных знаков SynthID и нейросетевых классификаторов?",
    "faq_a3": "Водяные знаки основаны на смещении вероятностей слов, а классификаторы вычисляют предсказуемость фраз и монотонность длины предложений. NonAI разрывает n-граммы, перефразирует штампы и вносит естественную вариативность длины предложений (Burstiness).",
    "faq_q4": "Гарантирует ли NonAI полную конфиденциальность и автономность?",
    "faq_a4": "Да. NonAI работает полностью локально на вашем устройстве или в памяти браузера. Обработка файлов и генерация бинарных данных происходят без отправки на внешние серверы.",
    "footer_text": "NonAI 2.0 • 100% Локальная офлайн-обработка • Защита конфиденциальности и авторского стиля",
    "modal_close": "Закрыть",
    "modal_details": {
        "rsid": {
            "title": "Сессии RSID - Экспертный анализ",
            "desc": "<strong>Что такое RSID?</strong><br>4-байтный 16-ричный идентификатор, сохраняемый Word при правках и паузах. В файлах от ИИ RSID отсутствует либо одинаков для всего документа, что мгновенно выявляется при анализе.",
            "sub": "Внедренный пул сессий биомиметических RSID ({count} сессий)"
        },
        "runs_split": {
            "title": "Разбиение Runs - Имитация набора текста",
            "desc": "<strong>Зачем разбивать Runs?</strong><br>ИИ пакует целые абзацы в один непрерывный узел <code>&lt;w:r&gt;</code>. Человек делает естественные паузы на запятых и точках. NonAI произвел естественное фрагментирование в <strong>{count}</strong> точках препинания.",
            "sub": "Примеры фрагментирования",
            "sample_desc": "Длинные фрагменты разбиты на естественные интервалы набора текста."
        },
        "claude_purged": {
            "title": "Удаление следов ИИ - Полная очистка происхождения",
            "desc": "<strong>Устранена критическая уязвимость: явные признания ИИ в коде</strong><br>Инструменты вроде Claude Docs вставляют в <code>docProps/core.xml</code> тег <code>Claude Docs node/...</code> и директорию <code>customXml/</code>. Это служит прямым доказательством генерации без статистического анализа.",
            "sub": "Выполненные операции очистки",
            "items": [
                "<strong>Удаление тегов:</strong> Полностью вырезан <code>&lt;dc:description&gt;</code>, очищены поля ключевых слов и темы.",
                "<strong>Удаление пакетов:</strong> Исключены папка <code>customXml/</code> и файл <code>docProps/custom.xml</code>.",
                "<strong>Глобальное сканирование:</strong> Из всех XML-потоков удалены упоминания <code>Claude Docs</code>, <code>Anthropic</code>, <code>ChatGPT</code>."
            ]
        },
        "pkg_synthesized": {
            "title": "Структура пакета Word - Восстановление целостности",
            "desc": "<strong>Устранена критическая уязвимость: неполный пакет Word</strong><br>Оригинальный Microsoft Word всегда сохраняет <code>fontTable.xml</code>, <code>webSettings.xml</code> и <code>theme1.xml</code>. Файлы от ИИ лишены их, что выдает подмену приложения.",
            "sub": "Синтезированные стандартные компоненты Microsoft",
            "items": [
                "<code>word/fontTable.xml</code>: Стандартная таблица шрифтов Calibri, Times New Roman и др.",
                "<code>word/webSettings.xml</code>: Оптимизация для браузера и флаги поддержки PNG.",
                "<code>word/theme/theme1.xml</code>: Официальная цветовая и шрифтовая схема Office.",
                "<code>[Content_Types].xml</code> и <code>document.xml.rels</code>: Зарегистрированы корректные связи."
            ]
        },
        "semantic": {
            "title": "Депаттернизация семантики - Защита от нейросетевых детекторов",
            "desc": "<strong>Устранена уязвимость: паттерны классификаторов Transformer</strong><br>Детекторы (например, OmniTraces INT8) анализируют гладкость перплексии и шаблонные триады. NonAI перестраивает жесткие конструкции в живой научный язык.",
            "sub": "Метрики пертурбации текста",
            "items": [
                "<strong>Перефразировано штампов ИИ:</strong> {replacements} вхождений",
                "<strong>Оптимизирована длина предложений и ритм:</strong> {reorganized} предложений",
                "<strong>Разрыв цепочек n-грамм:</strong> Разрушена статистическая значимость водяных знаков SynthID"
            ]
        },
        "ghost_styles": {
            "title": "Удаление скрытых стилей CSS - Очистка форматирования",
            "desc": "<strong>Скрытый фон чата:</strong><br>Копирование из веб-чатов часто переносит серый оттенок <code>#F7F7F8</code> в <code>&lt;w:shd&gt;</code>. NonAI полностью очищает документ от посторонних стилей.",
            "sub": "Удаленные стили и шрифты"
        },
        "unicode": {
            "title": "Удаление невидимых символов - Очистка скрытых водяных знаков",
            "desc": "<strong>Невидимые водяные знаки:</strong><br>Некоторые системы вставляют пробелы нулевой ширины (ZWSP) как штрихкод. NonAI удаляет все скрытые метки, сохраняя стандартную пунктуацию.",
            "before_label": "Обнаружено аномалий",
            "after_label": "Статус после очистки",
            "clean_status": "100% чистый стандартный NFC"
        },
        "human_time": {
            "title": "Имитированное время набора - Биомиметика таймлайна",
            "desc": "<strong>Уязвимость времени редактирования:</strong><br>Файлы от ИИ имеют <code>&lt;TotalTime&gt;0&lt;/TotalTime&gt;</code>. NonAI рассчитывает реалистичное время работы человека на основе объема текста.",
            "sub": "Биомиметическая модель времени",
            "items": [
                "<strong>Расчетное время работы:</strong> {minutes} минут (из расчета 32–35 сл/мин плюс паузы на размышления)",
                "<strong>Номер редакции:</strong> Редакция №{revision}",
                "<strong>Дата создания:</strong> {created}",
                "<strong>Дата изменения:</strong> {modified}"
            ]
        },
        "app_spoofed": {
            "title": "Поддельное приложение - Замена метаданных",
            "desc": "<strong>Метаданные приложения:</strong><br>Библиотечные сигнатуры (например, python-docx) заменены на легитимные свойства Microsoft Office Word.",
            "code_title": "Корректные свойства docProps XML"
        },
        "pdf_producer": {
            "title": "Очистка метаданных PDF и потоков XMP",
            "desc": "<strong>Маскировка генератора PDF:</strong><br>Замена wkhtmltopdf или Chromium на системный виртуальный принтер с полным удалением потоков XMP со страниц.",
            "orig_producer": "Исходный Producer",
            "spoofed_producer": "Подмененный Producer",
            "spoofed_creator": "Подмененный Creator"
        },
        "markdown": {
            "title": "Депаттернизация Markdown - Естественная верстка",
            "desc": "<strong>Слишком идеальная верстка Markdown:</strong><br>ИИ выравнивает таблицы с точностью до пробела. NonAI приводит их к естественному компактному виду и варьирует маркеры списков."
        }
    }
}

# Verify symmetry
base_keys = set(DATA["zh-TW"].keys())
for l in langs:
    curr_keys = set(DATA[l].keys())
    diff = base_keys.symmetric_difference(curr_keys)
    if diff:
        raise ValueError(f"Language {l} has key mismatch: {diff}")
    # Verify prohibited words
    txt = json.dumps(DATA[l], ensure_ascii=False)
    assert "零基礎" not in txt, f"Prohibited word found in {l}"
    assert "手把手" not in txt, f"Prohibited word found in {l}"

print(f"All {len(langs)} languages validated with 100% key symmetry and 0 prohibited words!")

# Write output to public/i18n.js and nonai/web/i18n.js
out_js = f"// NonAI Multilingual Localization Dictionary (7 Languages)\n// Supported: {', '.join(langs)}\n\nconst I18N_TRANSLATIONS = {json.dumps(DATA, indent=2, ensure_ascii=False)};\n"

for p in ["public/i18n.js", "nonai/web/i18n.js"]:
    with open(p, "w", encoding="utf-8") as f:
        f.write(out_js)
    print("Wrote:", p)
