"""
Stage 2: Fact & Citation Anchoring Auditor
Scans documents for unanchored empirical claims (numbers, percentages, comparative assertions)
and audits reference bibliography for completeness, authentic DOIs, and AI hallucination patterns.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple


@dataclass
class UnanchoredClaimItem:
    sentence_index: int
    sentence_text: str
    claim_type: str  # "percentage", "statistical", "comparative", "attribution"
    matched_clue: str
    risk_level: str  # "high", "medium"
    recommendation: str


@dataclass
class ReferenceAuditItem:
    entry_index: int
    raw_text: str
    doi: Optional[str]
    has_author: bool
    has_year: bool
    has_source: bool
    is_complete: bool
    hallucination_risk: str  # "low", "medium", "high"
    notes: str


@dataclass
class FactCitationAuditResult:
    total_sentences_checked: int
    total_claims_detected: int
    unanchored_claims_count: int
    anchored_claims_count: int
    unanchored_rate: float
    unanchored_claims: List[UnanchoredClaimItem]
    total_references_detected: int
    valid_references_count: int
    suspicious_references_count: int
    references: List[ReferenceAuditItem]
    fact_integrity_score: int  # 0 to 100
    summary_verdict: str


# Claim Detection Regex Patterns
PATTERNS_PERCENTAGE = re.compile(r'(\d+(?:\.\d+)?%|\d+(?:\.\d+)?\s*percent|[一二三四五六七八九十]+成|\d+成)', re.IGNORECASE)
PATTERNS_STATISTICAL = re.compile(r'(\bp\s*[<>=]\s*0?\.\d+|\b[nN]\s*=\s*\d+|\bR²\s*=\s*0?\.\d+|\br\s*=\s*0?\.\d+|\b\d+(?:\.\d+)?\s*(?:times|folds|倍)|\b(?:19|20)\d{2}\s*年)', re.IGNORECASE)
PATTERNS_COMPARATIVE = re.compile(r'(顯著(?:提升|降低|增加|減少|高於|低於)|大幅(?:成長|下滑|領先|超越)|significantly\s+(?:higher|lower|increased|decreased|greater|improved)|substantially\s+(?:higher|lower|increased|reduced))', re.IGNORECASE)
PATTERNS_ATTRIBUTION = re.compile(r'(研究(?:表明|指出|顯示|發現|證實)|文獻(?:指出|紀載|顯示)|數據(?:顯示|證實)|調查(?:發現|顯示)|studies\s+(?:show|indicate|demonstrate|suggest|reveal)|research\s+(?:shows|indicates|reveals|confirms)|scholars\s+(?:argue|found|demonstrated))', re.IGNORECASE)

# Citation Anchor Regex Patterns
PATTERNS_CITATION_ANCHOR = re.compile(
    r'(\[\s*\d+(?:\s*[,–-]\s*\d+)*\s*\]'  # [1], [1, 2], [1-3]
    r'|\[\s*[A-Z][a-zA-Z\s\.,&]+(?:\s+et\s+al\.?)?,?\s*(?:19|20)\d{2}[a-z]?\s*\]'  # [Smith et al., 2021]
    r'|\(\s*[A-Z][a-zA-Z\s\.,&]+(?:\s+et\s+al\.?)?,?\s*(?:19|20)\d{2}[a-z]?(?:,\s*p{1,2}\.?\s*\d+)?\s*\)'  # (Zhang et al., 2023, p. 12)
    r'|（\s*[^\）]+?(?:等|等人|，)?\s*(?:19|20)\d{2}[a-z]?(?:[，,]\s*[第pP]?\s*\d+\s*[頁pP]?)?\s*）)',  # （陳等人，2022）
    re.IGNORECASE
)

# Reference Section Header Regex
PATTERNS_REF_HEADER = re.compile(r'(?:^|\n)\s*(?:References|Bibliography|Works\s+Cited|參考文獻|引用文獻|文獻資料)\s*(?::|\n)', re.IGNORECASE)
PATTERNS_DOI = re.compile(r'\b(10\.\d{4,9}/[-._;()/:A-Za-z0-9]+)\b')


def _split_sentences_for_audit(text: str) -> List[str]:
    """Segment body text into analytical units."""
    raw = re.split(r'([。！？!?\n]+)', text)
    result = []
    i = 0
    while i < len(raw):
        s = raw[i].strip()
        if i + 1 < len(raw):
            punct = raw[i + 1].strip()
            if s:
                result.append(f"{s}{punct}")
            i += 2
        else:
            if s:
                result.append(s)
            i += 1
    return [s for s in result if len(s) >= 4]


def audit_fact_citations(text: str) -> FactCitationAuditResult:
    """
    Executes Stage 2 Fact & Citation Anchoring Audit on arbitrary text.
    1. Identifies sentences with empirical claims (quant numbers, comparative claims, study attributions).
    2. Flags unanchored claims lacking citation references in the same sentence.
    3. Analyzes reference section for DOI completeness and hallucination markers.
    """
    if not text or not text.strip():
        return FactCitationAuditResult(
            total_sentences_checked=0,
            total_claims_detected=0,
            unanchored_claims_count=0,
            anchored_claims_count=0,
            unanchored_rate=0.0,
            unanchored_claims=[],
            total_references_detected=0,
            valid_references_count=0,
            suspicious_references_count=0,
            references=[],
            fact_integrity_score=100,
            summary_verdict="未檢測到有效文字內容"
        )

    # 1. Separate body text from references if present
    body_text = text
    ref_text = ""
    ref_match = PATTERNS_REF_HEADER.search(text)
    if ref_match:
        split_pos = ref_match.start()
        body_text = text[:split_pos]
        ref_text = text[ref_match.end():]

    sentences = _split_sentences_for_audit(body_text)
    total_claims = 0
    unanchored_claims: List[UnanchoredClaimItem] = []
    anchored_claims = 0

    for idx, s in enumerate(sentences, start=1):
        has_anchor = bool(PATTERNS_CITATION_ANCHOR.search(s))
        
        # Check claim types
        m_pct = PATTERNS_PERCENTAGE.search(s)
        m_stat = PATTERNS_STATISTICAL.search(s)
        m_comp = PATTERNS_COMPARATIVE.search(s)
        m_attr = PATTERNS_ATTRIBUTION.search(s)

        matched_clue = None
        claim_type = None
        risk = "medium"

        if m_pct:
            matched_clue = m_pct.group(1)
            claim_type = "percentage"
            risk = "high"
        elif m_stat:
            matched_clue = m_stat.group(1)
            claim_type = "statistical"
            risk = "high"
        elif m_comp:
            matched_clue = m_comp.group(1)
            claim_type = "comparative"
            risk = "medium"
        elif m_attr:
            matched_clue = m_attr.group(1)
            claim_type = "attribution"
            risk = "medium"

        if claim_type:
            total_claims += 1
            if has_anchor:
                anchored_claims += 1
            else:
                # Build specific actionable recommendation
                if claim_type == "percentage":
                    rec = f"該句包含具體百分比「{matched_clue}」，請在句末補上精確的實驗數據來源或文獻錨點標籤（如 [Smith et al., 2023]）。"
                elif claim_type == "statistical":
                    rec = f"該句包含統計數值「{matched_clue}」，需具備相應的實證資料庫或作者年份引用。"
                elif claim_type == "comparative":
                    rec = f"該句包含比較性結論「{matched_clue}」，缺乏直接引用依據，容易被檢測器標記為泛泛之談。"
                else:
                    rec = f"該句指涉「{matched_clue}」卻未說明是哪一篇文獻，請指明具體作者與出版年份。"

                unanchored_claims.append(UnanchoredClaimItem(
                    sentence_index=idx,
                    sentence_text=s if len(s) <= 120 else s[:117] + "...",
                    claim_type=claim_type,
                    matched_clue=matched_clue,
                    risk_level=risk,
                    recommendation=rec
                ))

    # 2. Reference Bibliography Audit
    reference_items: List[ReferenceAuditItem] = []
    suspicious_refs_count = 0
    valid_refs_count = 0

    if ref_text.strip():
        # Split references by lines or numbered tags
        raw_ref_lines = [line.strip() for line in re.split(r'\n+(?=\[?\d+\]?\.?\s*|[A-Z][a-zA-Z]+,?\s+[A-Z]\.|\n)', ref_text) if len(line.strip()) >= 15]
        
        for r_idx, ref_line in enumerate(raw_ref_lines, start=1):
            doi_match = PATTERNS_DOI.search(ref_line)
            doi_val = doi_match.group(1) if doi_match else None

            has_year = bool(re.search(r'\b(?:19|20)\d{2}\b', ref_line))
            has_author = bool(re.search(r'^[A-Z][a-zA-Z\s\.,&]+', ref_line) or re.search(r'^\[\d+\]\s*[A-Z\u4e00-\u9fa5]+', ref_line))

            # Check for journal publication indicators (volume, issue, pages, publisher, or DOI)
            has_volume_pages = bool(re.search(r'(?:\b\d+\s*\(\s*\d+\s*\)\s*[,:]\s*\d+[-–]\d+|\bpp?\.?\s*\d+[-–]\d+|\bvol\.?\s*\d+)', ref_line, re.IGNORECASE))
            has_publisher = bool(re.search(r'(?:Press|Publishers?|Publishing|IEEE|ACM|Elsevier|Springer|Wiley|Routledge|Sage|Oxford|Cambridge|出版社|學報)', ref_line, re.IGNORECASE))
            has_journal = bool(re.search(r'\b(?:Journal|Conference|Proceedings|Transactions|Letters|Review)\b', ref_line, re.IGNORECASE) and not re.search(r'\bWithout Journal\b', ref_line, re.IGNORECASE))

            has_source = (has_volume_pages or has_publisher or (has_journal and (has_volume_pages or doi_val)) or doi_val is not None)

            is_complete = bool(has_year and has_author and has_source)
            risk = "low"
            notes = "文獻格式完整"

            if not doi_val and not (has_volume_pages or has_publisher):
                risk = "high"
                notes = "⚠️ 缺少期刊卷期、頁碼與 DOI 索引，疑似語言模型隨機捏造之虛構引用"
                suspicious_refs_count += 1
            elif not doi_val:
                risk = "medium"
                notes = "未附帶 DOI 永久連結，建議補齊 Crossref 檢索序號"
                valid_refs_count += 1
            else:
                risk = "low"
                notes = f"DOI 格式正確 ({doi_val})"
                valid_refs_count += 1

            reference_items.append(ReferenceAuditItem(
                entry_index=r_idx,
                raw_text=ref_line if len(ref_line) <= 140 else ref_line[:137] + "...",
                doi=doi_val,
                has_author=has_author,
                has_year=has_year,
                has_source=has_source,
                is_complete=is_complete,
                hallucination_risk=risk,
                notes=notes
            ))

    # Calculate Fact Integrity Score (0 - 100)
    unanchored_count = len(unanchored_claims)
    unanchored_rate = round((unanchored_count / max(total_claims, 1)) * 100, 1)

    score = 100
    if total_claims > 0:
        score -= min(int(unanchored_rate * 0.6), 55)
    if suspicious_refs_count > 0:
        score -= min(suspicious_refs_count * 15, 35)
    score = max(min(score, 100), 10)

    if score >= 85:
        verdict = "事實錨定度優異：文獻引用緊密，無顯著虛浮數據或捏造引用"
    elif score >= 65:
        verdict = f"存在部分未錨定主張：檢測到 {unanchored_count} 處包含數據/比較卻未標註來源，建議補齊錨點"
    else:
        verdict = f"高風險事實漏洞：檢測到 {unanchored_count} 處未錨定主張與 {suspicious_refs_count} 處疑似虛構文獻，極易被 AI 鑑識器抓取強訊號"

    return FactCitationAuditResult(
        total_sentences_checked=len(sentences),
        total_claims_detected=total_claims,
        unanchored_claims_count=unanchored_count,
        anchored_claims_count=anchored_claims,
        unanchored_rate=unanchored_rate,
        unanchored_claims=unanchored_claims,
        total_references_detected=len(reference_items),
        valid_references_count=valid_refs_count,
        suspicious_references_count=suspicious_refs_count,
        references=reference_items,
        fact_integrity_score=score,
        summary_verdict=verdict
    )
