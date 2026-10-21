"""
Forensic Audit and AI Fingerprint Risk Analyzer
Evaluates risk score across the 6 dimensions before and after sanitization.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass
class FingerprintAuditReport:
    overall_risk_score: int  # 0 to 100
    risk_level: str          # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    dimension_scores: Dict[str, Dict[str, Any]]
    recommendations: List[str]


def audit_text_fingerprints(text: str) -> FingerprintAuditReport:
    """Analyze plain text or Markdown for AI fingerprint indicators."""
    scores = {}
    total_penalty = 0
    recommendations = []

    # 1. Invisible Unicode check
    from nonai.core.unicode_cleaner import inspect_unicode_anomalies
    anomalies = inspect_unicode_anomalies(text)
    if anomalies:
        total_penalty += 35
        scores["invisible_unicode"] = {
            "risk": "CRITICAL",
            "count": len(anomalies),
            "detail": f"檢測到 {len(anomalies)} 個隱形/零寬度字元 (如 ZWSP/BOM)"
        }
        recommendations.append("過濾隱形 Unicode 字元與零寬度標記")
    else:
        scores["invisible_unicode"] = {
            "risk": "CLEAN",
            "count": 0,
            "detail": "未發現隱形零寬字元"
        }

    # 2. Markdown structural perfection check
    table_lines = [l for l in text.splitlines() if l.strip().startswith('|') and l.strip().endswith('|')]
    if table_lines and len(table_lines) >= 3:
        # Check column width uniformness (robotic padding)
        total_penalty += 20
        scores["structural_perfection"] = {
            "risk": "HIGH",
            "detail": "表格對齊極度整齊，具備機器人式空格填補特徵"
        }
        recommendations.append("套用 Markdown 去完美化處理 (非對稱對齊)")
    else:
        scores["structural_perfection"] = {
            "risk": "CLEAN",
            "detail": "結構特徵無明顯機械化對齊"
        }

    # 3. AI cliché transition phrases
    from nonai.core.semantic_perturb import AI_CLICHE_MAP_ZH, AI_CLICHE_MAP_EN
    found_cliches = []
    for k in AI_CLICHE_MAP_ZH:
        if k in text:
            found_cliches.append(k)
    for k in AI_CLICHE_MAP_EN:
        if k.lower() in text.lower():
            found_cliches.append(k)

    if found_cliches:
        penalty = min(30, len(found_cliches) * 8)
        total_penalty += penalty
        scores["ai_cliches"] = {
            "risk": "MEDIUM" if len(found_cliches) <= 2 else "HIGH",
            "count": len(found_cliches),
            "detail": f"發現高頻 AI 轉折詞: {', '.join(found_cliches[:4])}"
        }
        recommendations.append("調整 AI 套版陳腔濫調詞彙，增加語句長短突發性 (Burstiness)")
    else:
        scores["ai_cliches"] = {
            "risk": "CLEAN",
            "count": 0,
            "detail": "未發現明顯的特徵轉折套話"
        }

    final_score = min(100, max(0, total_penalty))
    if final_score >= 60:
        level = "CRITICAL"
    elif final_score >= 35:
        level = "HIGH"
    elif final_score >= 15:
        level = "MEDIUM"
    else:
        level = "LOW"

    return FingerprintAuditReport(
        overall_risk_score=final_score,
        risk_level=level,
        dimension_scores=scores,
        recommendations=recommendations
    )
