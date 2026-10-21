# -*- coding: utf-8 -*-
"""
Helper script to inject Stage 1 & Stage 2 i18n keys and modal details into public/i18n.js and nonai/web/i18n.js.
"""

import json
import re
from pathlib import Path

STAGE_KEYS = {
    "zh-TW": {
        "stat_stage1_title": "階段 1：突發性與八股消除",
        "stat_stage2_title": "階段 2：事實錨定與文獻核驗",
        "modal_stage1_title": "階段 1：文字與語義去八股及突發性重構",
        "modal_stage2_title": "階段 2：事實錨點與文獻真偽核驗報告",
        "modal_details_stage1": {
            "title": "階段 1：文字與語義去八股及突發性重構",
            "desc": "演算法自動掃描並消解 AI 八股套話與機械式過渡詞，重構長短句長度分佈，將突發性離散係數（Burstiness CV）提升至 0.65 以上，徹底打散神經網絡語言模型的預測機率。",
            "sub": "八股詞替換明細與突發性指標"
        },
        "modal_details_stage2": {
            "title": "階段 2：事實錨點與文獻真偽核驗報告",
            "desc": "深度審查文章中所有包含百分比、統計數據與比較歸因的句子，精準定位未在當句提供文獻依據的事實漏洞；同時核驗參考文獻 DOI 與出版資訊，預警虛構引用。",
            "sub": "可查證事實與文獻完整性清單"
        }
    },
    "en": {
        "stat_stage1_title": "Stage 1: Burstiness & Cliché Purge",
        "stat_stage2_title": "Stage 2: Fact & Citation Audit",
        "modal_stage1_title": "Stage 1: Lexical De-patterning & Burstiness Reshaper",
        "modal_stage2_title": "Stage 2: Fact & Citation Anchoring Audit Report",
        "modal_details_stage1": {
            "title": "Stage 1: Lexical De-patterning & Burstiness Reshaper",
            "desc": "Automatically purges AI clichés and robotic transition markers, reshaping sentence length distributions to boost Burstiness CV above 0.65 to disrupt transformer probability models.",
            "sub": "Cliché Replacements & Burstiness Metrics"
        },
        "modal_details_stage2": {
            "title": "Stage 2: Fact & Citation Anchoring Audit Report",
            "desc": "Exhaustively audits all sentences with statistics, percentages, and comparative assertions for explicit citations; validates reference DOIs to detect hallucinated citations.",
            "sub": "Verifiable Claims & Reference Integrity Breakdown"
        }
    },
    "zh-CN": {
        "stat_stage1_title": "阶段 1：突发性与套话消除",
        "stat_stage2_title": "阶段 2：事实锚定与文献核验",
        "modal_stage1_title": "阶段 1：文字与语义去套话及突发性重构",
        "modal_stage2_title": "阶段 2：事实锚点与文献真伪核验报告",
        "modal_details_stage1": {
            "title": "阶段 1：文字与语义去套话及突发性重构",
            "desc": "算法自动扫描并消解 AI 套话与机械式过渡词，重构长短句长度分布，将突发性离散系数（Burstiness CV）提升至 0.65 以上，彻底打散神经网络语言模型的预测概率。",
            "sub": "套话替换明细与突发性指标"
        },
        "modal_details_stage2": {
            "title": "阶段 2：事实锚点与文献真伪核验报告",
            "desc": "深度审查文章中所有包含百分比、统计数据与比较归因的句子，精准定位未在当句提供文献依据的事实漏洞；同时核验参考文献 DOI 与出版信息，预警虚构引用。",
            "sub": "可查证事实与文献完整性清单"
        }
    },
    "ja": {
        "stat_stage1_title": "ステップ 1：バースト性と定型語消去",
        "stat_stage2_title": "ステップ 2：事実アンカーと文献検証",
        "modal_stage1_title": "ステップ 1：語彙脱定型化とバースト性再構築",
        "modal_stage2_title": "ステップ 2：事実アンカーと文献真正性検証レポート",
        "modal_details_stage1": {
            "title": "ステップ 1：語彙脱定型化とバースト性再構築",
            "desc": "AIの定型表現や機械的な接続詞を自動消去し、長短文の分布を再構築してバースト性CVを0.65以上に高め、言語モデルの予測確率を分散させます。",
            "sub": "定型語置換詳細とバースト性指標"
        },
        "modal_details_stage2": {
            "title": "ステップ 2：事実アンカーと文献真正性検証レポート",
            "desc": "割合、統計数値、比較主張を含むすべての文を精査し、引用欠落の事実ホールを特定。参考文献のDOIと出版情報を検証し、架空文献を警告します。",
            "sub": "検証可能事実と文献整合性リスト"
        }
    },
    "ko": {
        "stat_stage1_title": "1단계: 버스트성 및 상투어 제거",
        "stat_stage2_title": "2단계: 사실 앵커링 및 문헌 검증",
        "modal_stage1_title": "1단계: 어휘 정형화 탈피 및 버스트성 재구성",
        "modal_stage2_title": "2단계: 사실 앵커링 및 문헌 진위 검증 보고서",
        "modal_details_stage1": {
            "title": "1단계: 어휘 정형화 탈피 및 버스트성 재구성",
            "desc": "AI 상투어와 기계적 접속사를 자동 제거하고 문장 길이 분포를 재구성하여 버스트성 CV를 0.65 이상으로 끌어올려 언어 모델 확률을 완전히 분산시킵니다.",
            "sub": "상투어 대체 내역 및 버스트성 지표"
        },
        "modal_details_stage2": {
            "title": "2단계: 사실 앵커링 및 문헌 진위 검증 보고서",
            "desc": "백분율, 통계치, 비교 주장이 포함된 모든 문장을 심층 검토하여 출처가 누락된 허점을 식별하고, 참고문헌 DOI 및 출판 정보를 검증하여 가상 인용을 경고합니다.",
            "sub": "검증 가능 사실 및 문헌 무결성 목록"
        }
    },
    "th": {
        "stat_stage1_title": "ขั้นตอนที่ 1: การปรับภาษาและเพิ่มความแปรผัน",
        "stat_stage2_title": "ขั้นตอนที่ 2: การตรวจสอบข้อเท็จจริงและเอกสาร",
        "modal_stage1_title": "ขั้นตอนที่ 1: การลดความซ้ำซากของภาษาและปรับความยาวประโยค",
        "modal_stage2_title": "ขั้นตอนที่ 2: รายงานการเชื่อมโยงข้อเท็จจริงและความแท้จริงของเอกสาร",
        "modal_details_stage1": {
            "title": "ขั้นตอนที่ 1: การลดความซ้ำซากของภาษาและปรับความยาวประโยค",
            "desc": "สแกนและลบคำซ้ำซากของ AI อัตโนมัติ ปรับโครงสร้างประโยคสั้นยาวเพื่อดันค่า Burstiness CV เกิน 0.65 สลายความน่าจะเป็นของโมเดลภาษาอย่างสิ้นเชิง",
            "sub": "รายการคำที่ถูกแทนที่และดัชนี Burstiness"
        },
        "modal_details_stage2": {
            "title": "ขั้นตอนที่ 2: รายงานการเชื่อมโยงข้อเท็จจริงและความแท้จริงของเอกสาร",
            "desc": "ตรวจสอบประโยคที่มีตัวเลข ร้อยละ และการเปรียบเทียบอย่างละเอียดเพื่อชี้จุดบกพร่องที่ขาดการอ้างอิง พร้อมตรวจ DOI และข้อมูลการตีพิมพ์เพื่อป้องกันเอกสารลวง",
            "sub": "รายการข้อเท็จจริงที่ตรวจสอบได้และความสมบูรณ์ของเอกสาร"
        }
    },
    "ru": {
        "stat_stage1_title": "Этап 1: Вариативность и снятие штампов",
        "stat_stage2_title": "Этап 2: Проверка фактов и источников",
        "modal_stage1_title": "Этап 1: Снятие клише и реструктуризация вариативности (Burstiness)",
        "modal_stage2_title": "Этап 2: Проверка привязки фактов и аутентичности ссылок",
        "modal_details_stage1": {
            "title": "Этап 1: Снятие клише и реструктуризация вариативности (Burstiness)",
            "desc": "Автоматически очищает штампы ИИ и механические связки, перестраивая длину предложений и повышая CV вариативности выше 0.65 для сбивания вероятностных моделей.",
            "sub": "Список замен штампов и метрики вариативности"
        },
        "modal_details_stage2": {
            "title": "Этап 2: Проверка привязки фактов и аутентичности ссылок",
            "desc": "Глубокая проверка предложений с процентами, статистикой и сравнениями на наличие ссылок; верификация DOI и реквизитов для выявления галлюцинаций ИИ.",
            "sub": "Проверяемые факты и целостность списка литературы"
        }
    }
}

def update_file(path: Path):
    content = path.read_text(encoding="utf-8")
    m = re.search(r"const I18N_TRANSLATIONS = (\{.*?\});", content, re.DOTALL)
    assert m, f"I18N_TRANSLATIONS not found in {path}"
    data = json.loads(m.group(1))

    for lang, keys in STAGE_KEYS.items():
        assert lang in data, f"Language {lang} missing"
        data[lang]["stat_stage1_title"] = keys["stat_stage1_title"]
        data[lang]["stat_stage2_title"] = keys["stat_stage2_title"]
        data[lang]["modal_stage1_title"] = keys["modal_stage1_title"]
        data[lang]["modal_stage2_title"] = keys["modal_stage2_title"]

        if "modal_details" in data[lang]:
            data[lang]["modal_details"]["stage1_restructure"] = keys["modal_details_stage1"]
            data[lang]["modal_details"]["stage2_fact_citation"] = keys["modal_details_stage2"]

    new_content = f"// NonAI Multilingual Localization Dictionary (7 Languages)\n// Supported: zh-TW, en, zh-CN, ja, ko, th, ru\n\nconst I18N_TRANSLATIONS = {json.dumps(data, ensure_ascii=False, indent=2)};\n"
    path.write_text(new_content, encoding="utf-8")
    print(f"[OK] Successfully updated {path}")

if __name__ == "__main__":
    update_file(Path("public/i18n.js"))
    update_file(Path("nonai/web/i18n.js"))
