# -*- coding: utf-8 -*-
"""
Helper script to inject workflow pipeline i18n keys across all 7 languages.
"""

import json
import re
from pathlib import Path

WORKFLOW_KEYS = {
    "zh-TW": {
        "workflow_title": "🔄 格式與工作流最佳實踐（AI 痕跡消除完整作業鏈）",
        "workflow_subtitle": "遵循「內容重構 ➔ 事實錨定 ➔ NonAI 仿生歷程注入 ➔ 原生導出」四階工法，徹底瓦解語言模型與元資料檢測特徵。",
        "wf_step1_badge": "階段 1",
        "wf_step1_title": "文字與語義去八股",
        "wf_step1_desc": "激化長短句突發性（Burstiness），刻意交錯 3~6 字極短句與複合長句；徹底刪除 delve into、值得注意的是、雙刃劍 等 AI 高頻過渡詞，拆解排比三段式。",
        "wf_step2_badge": "階段 2",
        "wf_step2_title": "文獻與事實錨點核驗",
        "wf_step2_desc": "補齊數據來源錨點，每處百分比、研究歸因或量化比較均於當句附上文獻依據；逐一核對論文真實 DOI，杜絕語言模型隨機捏造虛構引用。",
        "wf_step3_badge": "階段 3",
        "wf_step3_title": "NonAI 仿生歷程注入",
        "wf_step3_desc": "將 Word (DOCX) 拖放至上方拖曳區洗滌，注入 20~40 組隨機 Word RSID 會話池與文字 Runs 碎形切分，抹除 ChatGPT/Claude 網頁底色並偽裝真實工時。",
        "wf_step4_badge": "階段 4",
        "wf_step4_title": "正規原生導出 PDF",
        "wf_step4_desc": "切勿直接修改已定型排版的 PDF；應使用已洗滌的 DOCX 檔案，透過正版 Microsoft Word 或系統「列印/另存為 PDF」，產出 100% 潔淨無痕文件。"
    },
    "en": {
        "workflow_title": "🔄 Format & Workflow Best Practice (End-to-End De-AI Pipeline)",
        "workflow_subtitle": "Follow the 4-stage pipeline: Content Restructuring ➔ Evidence Anchoring ➔ NonAI Biomimetic Injection ➔ Native Export to dismantle language model and metadata detection.",
        "wf_step1_badge": "Stage 1",
        "wf_step1_title": "Lexical & Syntactic De-patterning",
        "wf_step1_desc": "Maximize burstiness by interleaving 3-6 word punchy clauses with complex sentences. Purge AI clichés like 'delve into', 'pivotal role', 'tapestry', and dismantle repetitive 3-point lists.",
        "wf_step2_badge": "Stage 2",
        "wf_step2_title": "Citation & Evidence Anchoring",
        "wf_step2_desc": "Anchor all statistics, percentages, and comparative claims with explicit citations in the same sentence. Verify all academic references with real DOIs to eliminate AI hallucinations.",
        "wf_step3_badge": "Stage 3",
        "wf_step3_title": "NonAI Biomimetic Injection",
        "wf_step3_desc": "Drop your Word (.docx) file into the zone above to inject 20-40 random RSID session pools, fractalize text runs, strip ghost CSS, and spoof authentic human editing time.",
        "wf_step4_badge": "Stage 4",
        "wf_step4_title": "Native Application PDF Export",
        "wf_step4_desc": "Never edit post-typeset compiled PDFs directly. Open the cleaned DOCX in licensed Microsoft Word or OS Print engine and export to PDF for 100% genuine forensic integrity."
    },
    "zh-CN": {
        "workflow_title": "🔄 格式与工作流最佳实践（AI 痕迹消除完整作业链）",
        "workflow_subtitle": "遵循「内容重构 ➔ 事实锚定 ➔ NonAI 仿生历程注入 ➔ 原生导出」四阶工法，彻底瓦解语言模型与元数据检测特征。",
        "wf_step1_badge": "阶段 1",
        "wf_step1_title": "文字与语义去套话",
        "wf_step1_desc": "激化长短句突发性（Burstiness），刻意交错 3~6 字极短句与复合长句；彻底删除 delve into、值得注意的是、双刃剑 等 AI 高频过渡词，拆解排比三段式。",
        "wf_step2_badge": "阶段 2",
        "wf_step2_title": "文献与事实锚点核验",
        "wf_step2_desc": "补齐数据来源锚点，每处百分比、研究归因或量化比较均于当句附上文献依据；逐一核对论文真实 DOI，杜绝语言模型随机捏造虚构引用。",
        "wf_step3_badge": "阶段 3",
        "wf_step3_title": "NonAI 仿生历程注入",
        "wf_step3_desc": "将 Word (DOCX) 拖放至上方拖曳区洗涤，注入 20~40 组随机 Word RSID 会话池与文字 Runs 碎形切分，抹除 ChatGPT/Claude 网页底色并伪装真实工时。",
        "wf_step4_badge": "阶段 4",
        "wf_step4_title": "正规原生导出 PDF",
        "wf_step4_desc": "切勿直接修改已定型排版的 PDF；应使用已洗涤的 DOCX 档案，透过正版 Microsoft Word 或系统「打印/另存为 PDF」，产出 100% 洁净无痕文件。"
    },
    "ja": {
        "workflow_title": "🔄 フォーマットとワークフローのベストプラクティス（AI痕跡消去の完全パイプライン）",
        "workflow_subtitle": "「コンテンツ再構築 ➔ 事実アンカー ➔ NonAI生体模倣注入 ➔ ネイティブ出力」の4段階手法に従い、言語モデルとメタデータの検出特徴を完全無効化します。",
        "wf_step1_badge": "ステップ 1",
        "wf_step1_title": "語彙と構文の定型表現脱却",
        "wf_step1_desc": "長短文のバースト性（Burstiness）を高め、3〜6語の極短文と複合長文を交錯させます。「delve into」「注目すべきことに」等のAI高頻度語を排除し、3項目並列を崩します。",
        "wf_step2_badge": "ステップ 2",
        "wf_step2_title": "文献と事実アンカーの検証",
        "wf_step2_desc": "すべての割合、研究帰属、定量的比較の文に文献アンカーを付記。実在するDOIで全参考文献を確認し、LLMによる架空文献の捏造を完全に排除します。",
        "wf_step3_badge": "ステップ 3",
        "wf_step3_title": "NonAI生体模倣プロセスの注入",
        "wf_step3_desc": "Word (DOCX)を上の領域にドロップし、20〜40組のWord RSID履歴プールとRuns分割を注入。ChatGPT/ClaudeのCSS残渣を消去し、実作業時間を偽装します。",
        "wf_step4_badge": "ステップ 4",
        "wf_step4_title": "正規ネイティブPDF出力",
        "wf_step4_desc": "組版済みのPDF本文を直接編集しないでください。浄化済みDOCXを正規Microsoft WordまたはOS印刷機能で開き、ネイティブPDFとして出力して完全な真正性を確保します。"
    },
    "ko": {
        "workflow_title": "🔄 포맷 및 워크플로 모범 실천 (AI 흔적 완전 제거 작업 체인)",
        "workflow_subtitle": "「콘텐츠 재구성 ➔ 사실 앵커링 ➔ NonAI 모방 이력 주입 ➔ 네이티브 내보내기」 4단계 공법을 준수하여 언어 모델과 메타데이터 감지 특성을 완전히 해체합니다.",
        "wf_step1_badge": "1단계",
        "wf_step1_title": "어휘 및 구문 정형화 탈피",
        "wf_step1_desc": "장단문 버스트성(Burstiness)을 극대화하여 3~6단어 초단문과 복합 장문을 교차 배치합니다. 'delve into', '주목할 만한 점은' 등 AI 빈출 접속사를 제거하고 3단 병렬을 해체합니다.",
        "wf_step2_badge": "2단계",
        "wf_step2_title": "문헌 및 사실 앵커 검증",
        "wf_step2_desc": "모든 백분율, 연구 귀속, 수치 비교 문장에 명확한 문헌 출처를 첨부합니다. 실제 DOI로 모든 참고문헌을 검증하여 LLM의 허위 인용 날조를 원천 차단합니다.",
        "wf_step3_badge": "3단계",
        "wf_step3_title": "NonAI 모방 이력 주입",
        "wf_step3_desc": "Word (DOCX) 문서를 상단 영역에 드롭하여 20~40개의 RSID 세션 풀과 텍스트 Runs 분할을 주입합니다. ChatGPT/Claude 웹 스타일을 제거하고 실제 편집 시간을 모방합니다.",
        "wf_step4_badge": "4단계",
        "wf_step4_title": "정규 네이티브 PDF 내보내기",
        "wf_step4_desc": "조판이 완료된 PDF 본문을 직접 수정하지 마십시오. 정화된 DOCX를 정품 Microsoft Word 또는 시스템 인쇄 엔진에서 열고 PDF로 내보내어 100% 무결점을 확보합니다."
    },
    "th": {
        "workflow_title": "🔄 แนวปฏิบัติที่ดีที่สุดของรูปแบบและขั้นตอนงาน (กระบวนการลบร่องรอย AI ครบวงจร)",
        "workflow_subtitle": "ปฏิบัติตาม 4 ขั้นตอน: ปรับโครงสร้างเนื้อหา ➔ ยึดโยงข้อเท็จจริง ➔ ฉีดประวัติจำลอง NonAI ➔ ส่งออกไฟล์แบบเนทีฟ เพื่อสลายการตรวจจับโมเดลภาษาและเมทาดาตาอย่างหมดจด",
        "wf_step1_badge": "ขั้นตอนที่ 1",
        "wf_step1_title": "การปรับภาษาและทำลายความซ้ำซาก",
        "wf_step1_desc": "เพิ่มความแปรผันของความยาวประโยค (Burstiness) โดยสลับประโยคสั้น 3-6 คำกับประโยคยาวที่ซับซ้อน ลบคำเชื่อมยอดฮิตของ AI เช่น 'delve into', 'เป็นที่น่าสังเกตว่า' และทำลายโครงสร้างสามส่วน",
        "wf_step2_badge": "ขั้นตอนที่ 2",
        "wf_step2_title": "การตรวจสอบเอกสารอ้างอิงและข้อเท็จจริง",
        "wf_step2_desc": "ระบุแหล่งอ้างอิงในทุกประโยคที่มีตัวเลข ร้อยละ หรือการเปรียบเทียบเชิงวิจัย ตรวจสอบ DOI จริงของเอกสารทุกฉบับเพื่อป้องกันการกุเอกสารอ้างอิงของโมเดลภาษา",
        "wf_step3_badge": "ขั้นตอนที่ 3",
        "wf_step3_title": "การฉีดประวัติเลียนแบบด้วย NonAI",
        "wf_step3_desc": "ลากไฟล์ Word (.docx) วางลงในช่องด้านบนเพื่อฉีดกลุ่มประวัติ RSID 20-40 ชุดและตัดย่อย Runs ข้อความ ลบสีพื้นหลังเว็บของ ChatGPT/Claude พร้อมจำลองเวลาทำงานจริง",
        "wf_step4_badge": "ขั้นตอนที่ 4",
        "wf_step4_title": "การส่งออก PDF แบบเนทีฟ",
        "wf_step4_desc": "อย่าแก้ไขข้อความในไฟล์ PDF ที่จัดหน้าเสร็จแล้วโดยตรง ควรเปิดไฟล์ DOCX ที่ผ่านการชำระล้างด้วย Microsoft Word ลิขสิทธิ์แท้หรือคำสั่งพิมพ์ของระบบ แล้วบันทึกเป็น PDF เพื่อความไร้ร่องรอย 100%"
    },
    "ru": {
        "workflow_title": "🔄 Лучшие практики форматов и процессов (Полная цепочка устранения следов ИИ)",
        "workflow_subtitle": "Следуйте 4-этапному процессу: Реструктуризация ➔ Привязка фактов ➔ Биомиметическая инъекция NonAI ➔ Нативный экспорт для полной нейтрализации детекторов ИИ.",
        "wf_step1_badge": "Этап 1",
        "wf_step1_title": "Снятие шаблонности и синтаксиса",
        "wf_step1_desc": "Увеличьте вариативность длины предложений (Burstiness), чередуя емкие фразы из 3-6 слов со сложными структурами. Удалите клише ИИ вроде 'delve into', 'важно отметить' и разбейте триады.",
        "wf_step2_badge": "Этап 2",
        "wf_step2_title": "Проверка ссылок и привязка фактов",
        "wf_step2_desc": "Подкрепляйте все проценты, количественные сравнения и выводы ссылками прямо в предложении. Проверяйте реальные DOI всех источников для исключения галлюцинаций ИИ.",
        "wf_step3_badge": "Этап 3",
        "wf_step3_title": "Биомиметическая инъекция NonAI",
        "wf_step3_desc": "Перетащите Word (.docx) в зону выше для внедрения пула 20-40 сессий RSID и разбиения Runs, удаления стилей ChatGPT/Claude и маскировки времени работы человека.",
        "wf_step4_badge": "Этап 4",
        "wf_step4_title": "Нативный экспорт в PDF",
        "wf_step4_desc": "Не редактируйте скомпилированные PDF напрямую. Откройте очищенный DOCX в лицензионном Microsoft Word или через печать системы и экспортируйте в PDF для 100% подлинности."
    }
}

def update_i18n_file(filepath: Path):
    content = filepath.read_text(encoding="utf-8")
    m = re.search(r"const I18N_TRANSLATIONS = (\{.*?\});", content, re.DOTALL)
    assert m, f"I18N_TRANSLATIONS not found in {filepath}"
    data = json.loads(m.group(1))

    for lang, new_keys in WORKFLOW_KEYS.items():
        assert lang in data, f"Language {lang} missing in {filepath}"
        for k, v in new_keys.items():
            data[lang][k] = v

    new_content = f"// NonAI Multilingual Localization Dictionary (7 Languages)\n// Supported: zh-TW, en, zh-CN, ja, ko, th, ru\n\nconst I18N_TRANSLATIONS = {json.dumps(data, ensure_ascii=False, indent=2)};\n"
    filepath.write_text(new_content, encoding="utf-8")
    print(f"[OK] Updated {filepath}")

if __name__ == "__main__":
    update_i18n_file(Path("public/i18n.js"))
    update_i18n_file(Path("nonai/web/i18n.js"))
