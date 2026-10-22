"""
Stage 1: Automated Semantic Restructuring & Burstiness Reshaper
Disrupts AI predictability, dismantles cliché transition templates,
destabilizes uniform sentence lengths (maximizes Burstiness CV > 0.65),
and dissolves rigid rule-of-three structures.
"""

import math
import random
import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Any, Optional

# Extended Lexical De-Patterning Dictionary (ZH & EN)
EXPANDED_CLICHE_MAP_ZH: Dict[str, List[str]] = {
    "值得注意的是": ["特別需要留意的是", "顯而易見的是", "在實務檢驗中", "事實上"],
    "值得一提的是": ["關鍵在於", "不容忽視的是", "另一個焦點在於", "具體觀察顯示"],
    "不可否認的是": ["平心而論", "實證結果確鑿", "無可爭辯的是", "客觀檢視下"],
    "毋庸置疑": ["確鑿無疑", "毫無懸念", "實質上已成定論"],
    "總結來說": ["概括全篇脈絡", "總括而論", "就整體研究視野觀之", "綜合評估後"],
    "綜上所述": ["綜合前述多維分析", "基於以上實證推論", "通盤梳理後", "整體而言"],
    "深入探討": ["周延剖析", "嚴密檢視", "細緻爬梳", "進行針對性考察"],
    "深入分析": ["系統性深究", "層層拆解", "周全考證"],
    "扮演著舉足輕重的角色": ["具決定性樞紐價值", "發揮基石效應", "具有實質引領作用"],
    "扮演著重要角色": ["發揮核心推動效能", "處於關鍵節點", "具有不可替代的作用"],
    "扮演關鍵角色": ["居於核心地位", "掌握關鍵推動力", "決定整體走向"],
    "雙刃劍": ["兼具效益與風險", "存在著一體兩面的拉扯", "帶來結構性利弊互見"],
    "一把雙刃劍": ["利弊交織的機制", "具有兩面特徵的策略", "具兩面影響之手段"],
    "顯著提升": ["帶來可觀增長", "實現實質跨越", "呈現大幅上揚"],
    "顯著增加": ["增幅極為明顯", "呈現放量攀升", "達到實質躍升"],
    "顯著改善": ["獲得顯見的優化", "迎來根本性轉機", "呈現正面成效"],
    "全面提升": ["全方位優化", "實現整體跨度改善", "全面推動升級"],
    "這不僅僅是": ["這不僅止於", "這絕非單純的", "這超越了原本的"],
    "更是": ["同時更是深化了", "進一步彰顯出", "實質昇華為"],
    "有助於": ["利於驅動", "實質助益於", "為...提供了有利契機"],
    "以期": ["藉此力求", "旨在促成", "為此竭力實現"],
    "換言之": ["直言之", "簡言之", "換個角度透視"],
    "在當今數位化時代": ["身處數位轉型深化階段", "面對資訊科技普及的當下", "在數位環境高度成熟的今日"],
    "在當今快節奏的世界中": ["面對步調緊迫的現代環境", "在急速變遷的生活形態下", "在瞬息萬變的局勢中"],
    "為...奠定基礎": ["為...築牢根基", "奠立了長遠的發展基石", "拓展出厚實的實踐底層"],
    "顯而易見": ["客觀檢視下", "實務觀察顯示", "不難發現"],
    "至關重要": ["居關鍵樞紐", "具有實質決定性", "不可或缺"],
    "毋庸置疑的是": ["確鑿無疑的是", "無可爭辯的是", "平心而論"],
    "這項研究旨在": ["在研究架構規劃上，我們首要聚焦於", "本項工作的核心著眼於", "本研究著手於"],
    "旨在探討": ["聚焦考察", "著眼於剖析", "致力於釐清"],
    "以期達到": ["力求促成", "以落實具體", "藉此實現實質"],
    "以期達到最佳之效益": ["藉此觀察實務效益", "以期獲致確切改善", "力求落實應用成效"],
    "以期達到之效益": ["以求實質成效", "用以驗證實務效益", "力求發揮實質助益"],
}

EXPANDED_CLICHE_MAP_EN: Dict[str, List[str]] = {
    "delve into": ["examine", "explore", "investigate", "scrutinize", "probe into"],
    "delves into": ["examines", "explores", "investigates", "scrutinizes"],
    "delving into": ["examining", "exploring", "probing", "investigating"],
    "a pivotal role": ["a decisive function", "a central anchor", "an indispensable part"],
    "plays a pivotal role": ["directly steers", "is central to", "decisively influences"],
    "plays an important role": ["is influential", "serves as a backbone", "carries significant weight"],
    "a testament to": ["compelling evidence of", "a clear manifestation of", "proof of"],
    "rich tapestry": ["interwoven framework", "multifaceted landscape", "complex ecosystem"],
    "tapestry": ["mosaic", "interplay", "intricate array", "composite structure"],
    "in conclusion": ["ultimately", "taken together", "broadly speaking", "in the final analysis"],
    "in summary": ["on balance", "in sum", "to distill the core finding", "overall"],
    "it is worth noting that": ["notably,", "significantly,", "one crucial aspect is that"],
    "it is crucial to note that": ["crucially,", "of particular importance is that"],
    "furthermore": ["additionally", "beyond this", "equally significant", "meanwhile"],
    "moreover": ["in parallel", "what is more", "alongside this"],
    "foster": ["cultivate", "stimulate", "encourage", "drive forward"],
    "harness": ["leverage", "utilize", "deploy", "capitalize on"],
    "beacon": ["touchstone", "guiding benchmark", "reference standard"],
    "cutting-edge": ["contemporary", "state-of-the-art", "novel", "forward-looking"],
    "multifaceted": ["complex", "layered", "multi-dimensional", "nuanced"],
    "not only": ["beyond merely", "not simply"],
    "revolutionize": ["overhaul", "reshape", "redefine"],
    "seamlessly": ["cohesively", "directly", "unobtrusively", "coherently"],
}

# Lexical & Entity Diversity Map (ZH & EN)
# Prevents detector warnings like: "『學校』文字過常被重覆使用，於整體而言是過文字上的表現弱點"
ENTITY_DIVERSITY_MAP_ZH: Dict[str, List[str]] = {
    "學校": ["受試院校", "教學現場", "各級機構", "所屬場域", "該校", "辦學機構"],
    "學生": ["受試學員", "在學青年", "學習者", "參與對象", "學子"],
    "教師": ["教學人員", "指導師資", "前線教育者", "教師群", "授課教師"],
    "系統": ["架構機制", "該平台", "所建構之模組", "技術底層", "此套機制"],
    "研究": ["本項探討", "實證調查", "專案計畫", "實務考察", "分析工作"],
    "平台": ["系統環境", "操作介面", "數位中樞", "協同空間"],
    "機構": ["權責單位", "組織架構", "所屬單位", "外部機構"],
    "模型": ["推論架構", "分析模型", "演算框架", "預測模組"],
    "數據": ["實證資料", "觀測數值", "統計指標", "歷程記錄"],
}

ENTITY_DIVERSITY_MAP_EN: Dict[str, List[str]] = {
    "school": ["academic institution", "educational setting", "the campus", "learning center"],
    "student": ["learner", "participant", "attendee", "undergraduate"],
    "teacher": ["instructor", "educator", "pedagogue", "academic staff"],
    "system": ["framework", "architecture", "platform mechanism", "functional module"],
    "research": ["investigation", "inquiry", "empirical inquiry", "study project"],
    "platform": ["digital environment", "infrastructure", "operational system"],
}

HUMAN_PUNCHY_INJECTIONS_ZH: List[str] = [
    "事實並非如此。",
    "這項挑戰依舊存在。",
    "這一點尤為關鍵。",
    "實務情況往往更為複雜。",
    "然而情況並非如此單純。",
    "此項落差值得持續深究。"
]

HUMAN_PUNCHY_INJECTIONS_EN: List[str] = [
    "In practice, reality is more nuanced.",
    "This barrier remains evident.",
    "The empirical contrast is clear.",
    "Such distinctions are decisive."
]


@dataclass
class RestructureMetrics:
    original_sentence_count: int
    reshaped_sentence_count: int
    original_mean_len: float
    reshaped_mean_len: float
    original_std_dev: float
    reshaped_std_dev: float
    original_cv: float  # std_dev / mean
    reshaped_cv: float
    burstiness_boost_percent: float
    cliches_purged_count: int
    cliche_replacements: List[Dict[str, Any]]
    rules_of_three_disrupted: int
    short_punchy_sentences_created: int
    high_risk_residues_dissolved: int = 0
    entity_diversity_replacements_count: int = 0
    entity_diversity_details: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class RestructureResult:
    cleaned_text: str
    metrics: RestructureMetrics


def _dissolve_high_risk_residues(text: str) -> Tuple[str, int]:
    """
    Identifies and dismantles high-confidence AI residue sentences (60%~90% probability patterns),
    such as rigid tripartite structures: '本研究旨在...，進而...，以期達到...之效益'.
    Replaces them with active scholarly prose, varied pacing, and decomposed independent propositions.
    """
    dissolved_count = 0
    res = text

    # Pattern 1: 本研究旨在(?P<g1>.+?)，(進而|並)(?P<g2>.+?)，以期達到(?P<g3>.+?)之(?P<tail>效益|成效|目的|成果)
    p1 = re.compile(
        r'(?:本研究|本計畫|本論文|本研究案)?旨在(?P<g1>[^，。！？]+?)，(?:進而|並|同時)?(?P<g2>[^，。！？]+?)，以期達到(?P<g3>[^，。！？]+?)之(?:效益|成效|目的|成果|目標)',
        re.IGNORECASE
    )
    def _sub_p1(m):
        nonlocal dissolved_count
        dissolved_count += 1
        g1 = m.group("g1").strip()
        g2 = m.group("g2").strip()
        g3 = m.group("g3").strip()
        return f"在研究架構規劃上，我們首要聚焦於{g1}。後續分析則著重{g2}，藉此驗證{g3}的實際運作成效"
    res = p1.sub(_sub_p1, res)

    # Pattern 2: 旨在...，進而...，以期...
    p2 = re.compile(
        r'旨在(?P<g1>[^，。！？]+?)，(?:進而|並)?(?P<g2>[^，。！？]+?)，以期(?P<g3>[^，。！？]+?)(?=[。！？\n])',
        re.IGNORECASE
    )
    def _sub_p2(m):
        nonlocal dissolved_count
        dissolved_count += 1
        g1 = m.group("g1").strip()
        g2 = m.group("g2").strip()
        g3 = m.group("g3").strip()
        return f"主要著眼於{g1}，同時循序開展{g2}，藉以具體檢視{g3}"
    res = p2.sub(_sub_p2, res)

    # Pattern 3: 為此，本研究(將|透過)...以達到...
    p3 = re.compile(
        r'為此[，,]\s*(?:本研究|本計畫|本專案)?(?:將)?透過(?P<g1>[^，。！？]+?)，(?:以|用以)?達到(?P<g2>[^，。！？]+?)之(?P<tail>效益|成效|目的|成果|目標)',
        re.IGNORECASE
    )
    def _sub_p3(m):
        nonlocal dissolved_count
        dissolved_count += 1
        g1 = m.group("g1").strip()
        g2 = m.group("g2").strip()
        return f"為此，我們在方法設計上採取{g1}，力求落實{g2}的具體評估"
    res = p3.sub(_sub_p3, res)

    # English Pattern 1: aims to ... in order to ... thereby achieving ...
    p_en = re.compile(
        r'\b(?:This study|This project|This research)?\s*aims to\s+(?P<g1>[^,.]+?),\s*(?:thereby|in order to)\s+(?P<g2>[^,.]+?),\s*(?:thereby achieving|so as to achieve)\s+(?P<g3>[^.]+?)\b',
        re.IGNORECASE
    )
    def _sub_p_en(m):
        nonlocal dissolved_count
        dissolved_count += 1
        g1 = m.group("g1").strip()
        g2 = m.group("g2").strip()
        g3 = m.group("g3").strip()
        return f"Our operational inquiry centers primarily on {g1}. Through this lens, we examine {g2} while assessing tangible outcomes in {g3}"
    res = p_en.sub(_sub_p_en, res)

    return res, dissolved_count


def _reduce_entity_repetition(text: str, char_window: int = 250) -> Tuple[str, int, List[Dict[str, Any]]]:
    """
    Suppresses excessive repetition of specific noun entities (e.g., '學校', '學生', '系統').
    Prevents detector flags such as: '「學校」文字過常被重覆使用，於整體而言是過文字上的表現弱點'.
    Uses context-aware lexical rotation across both intra-paragraph and sliding proximity windows.
    """
    total_replacements = 0
    details = []
    res = text

    # Process Chinese entities
    for entity, syn_list in ENTITY_DIVERSITY_MAP_ZH.items():
        if entity not in res or res.count(entity) < 2:
            continue

        matches = list(re.finditer(re.escape(entity), res))
        if len(matches) < 2:
            continue

        syn_pool = syn_list.copy()
        random.shuffle(syn_pool)

        new_chars = []
        last_idx = 0
        last_rep_pos = -9999

        for i, m in enumerate(matches):
            start, end = m.start(), m.end()
            new_chars.append(res[last_idx:start])

            # Keep the very first mention to anchor the concept
            if i == 0:
                new_chars.append(entity)
                last_rep_pos = start
            else:
                # If within proximity window of previous occurrence, substitute with varied synonym
                if (start - last_rep_pos) <= char_window or i % 2 == 1:
                    chosen_syn = syn_pool[(i - 1) % len(syn_pool)]
                    new_chars.append(chosen_syn)
                    total_replacements += 1
                    details.append({
                        "entity": entity,
                        "replacement": chosen_syn,
                        "position": start
                    })
                else:
                    new_chars.append(entity)
                last_rep_pos = start

            last_idx = end

        new_chars.append(res[last_idx:])
        res = "".join(new_chars)

    # Process English entities
    for entity, syn_list in ENTITY_DIVERSITY_MAP_EN.items():
        pattern = re.compile(rf'\b{re.escape(entity)}\b', re.IGNORECASE)
        matches = list(pattern.finditer(res))
        if len(matches) < 2:
            continue

        syn_pool = syn_list.copy()
        random.shuffle(syn_pool)

        new_chars = []
        last_idx = 0
        last_rep_pos = -9999

        for i, m in enumerate(matches):
            start, end = m.start(), m.end()
            new_chars.append(res[last_idx:start])
            orig_word = m.group(0)

            if i == 0:
                new_chars.append(orig_word)
                last_rep_pos = start
            else:
                if (start - last_rep_pos) <= char_window or i % 2 == 1:
                    chosen_syn = syn_pool[(i - 1) % len(syn_pool)]
                    if orig_word[0].isupper():
                        chosen_syn = chosen_syn.capitalize()
                    new_chars.append(chosen_syn)
                    total_replacements += 1
                    details.append({
                        "entity": entity,
                        "replacement": chosen_syn,
                        "position": start
                    })
                else:
                    new_chars.append(orig_word)
                last_rep_pos = start

            last_idx = end

        new_chars.append(res[last_idx:])
        res = "".join(new_chars)

    return res, total_replacements, details


def _split_into_sentences(text: str) -> List[str]:
    """Splits text into sentences for both Chinese and English while preserving basic boundaries."""
    # Split on standard punctuation
    parts = re.split(r'([。！？!?；;]\s*)', text)
    sentences = []
    i = 0
    while i < len(parts):
        s = parts[i]
        if i + 1 < len(parts):
            punc = parts[i + 1]
            sentences.append((s + punc).strip())
            i += 2
        else:
            if s.strip():
                sentences.append(s.strip())
            i += 1
    return [s for s in sentences if s]


def _calc_burstiness(sentences: List[str]) -> Tuple[float, float, float]:
    """Calculates Mean length, Standard Deviation, and Coefficient of Variation (CV)."""
    if not sentences:
        return 0.0, 0.0, 0.0
    lengths = [len(s) for s in sentences]
    mean_val = sum(lengths) / len(lengths)
    if len(lengths) <= 1 or mean_val == 0:
        return mean_val, 0.0, 0.0
    variance = sum((x - mean_val) ** 2 for x in lengths) / (len(lengths) - 1)
    std_dev = math.sqrt(variance)
    cv = std_dev / mean_val
    return round(mean_val, 2), round(std_dev, 2), round(cv, 4)


def restructure_semantics_and_burstiness(
    text: str,
    target_cv: float = 0.70,
    enable_cliche_purge: bool = True,
    enable_burstiness_boost: bool = True,
    enable_high_risk_residue_dissolve: bool = True,
    enable_entity_diversity: bool = True
) -> RestructureResult:
    """
    Performs Stage 1 Automated Semantic Restructuring:
    1. Dissolves high-risk residue templates (60%-90% probability patterns like '旨在...進而...以期...').
    2. Replaces AI clichés with natural human academic and discursive phrasing.
    3. Suppresses excessive repetition of specific noun entities (e.g., '學校', '學生').
    4. Dismantles rigid Rule-of-Three parallel formulas.
    5. Re-shapes sentence lengths and injects human cadence to boost burstiness (CV >= 0.70).
    """
    if not text or not text.strip():
        empty_metrics = RestructureMetrics(0, 0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0, [], 0, 0, 0, 0, [])
        return RestructureResult(text, empty_metrics)

    orig_sentences = _split_into_sentences(text)
    orig_mean, orig_std, orig_cv = _calc_burstiness(orig_sentences)

    processed_text = text
    cliche_replacements = []
    cliches_purged = 0
    rules_of_three = 0
    high_risk_dissolved = 0
    entity_replacements = 0
    entity_details = []

    # Step 0: Dissolve High-Risk Residue Templates
    if enable_high_risk_residue_dissolve:
        processed_text, high_risk_dissolved = _dissolve_high_risk_residues(processed_text)

    # Step 1: Lexical De-Patterning (AI Cliché Purge)
    if enable_cliche_purge:
        # Chinese clichés
        for cliché, replacements in EXPANDED_CLICHE_MAP_ZH.items():
            if cliché in processed_text:
                count = processed_text.count(cliché)
                chosen = random.choice(replacements)
                processed_text = processed_text.replace(cliché, chosen)
                cliches_purged += count
                cliche_replacements.append({
                    "original": cliché,
                    "replacement": chosen,
                    "count": count,
                    "lang": "zh"
                })

        # English clichés
        for cliché, replacements in EXPANDED_CLICHE_MAP_EN.items():
            pattern = re.compile(rf'\b{re.escape(cliché)}\b', re.IGNORECASE)
            matches = pattern.findall(processed_text)
            if matches:
                chosen = random.choice(replacements)
                processed_text = pattern.sub(chosen, processed_text)
                count = len(matches)
                cliches_purged += count
                cliche_replacements.append({
                    "original": cliché,
                    "replacement": chosen,
                    "count": count,
                    "lang": "en"
                })

        # Step 1b: Rule-of-Three dismantling
        # Chinese: 首先... 其次... 最後... -> 一方面... 此外... 終局而言...
        r3_zh = re.compile(r'首先[，,]\s*(.*?)[。.]\s*其次[，,]\s*(.*?)[。.]\s*最後[，,]\s*(.*?)[。.]')
        def _sub_r3_zh(m):
            nonlocal rules_of_three
            rules_of_three += 1
            return f"一方面，{m.group(1)}。此外，{m.group(2)}。而在終局的綜合考量下，{m.group(3)}。"
        processed_text = r3_zh.sub(_sub_r3_zh, processed_text)

        # English: First, ... Second, ... Finally, ...
        r3_en = re.compile(r'\bFirst[ly]?[,:]\s*(.*?)[.]\s*Second[ly]?[,:]\s*(.*?)[.]\s*Third[ly]?|Finally[,:]\s*(.*?)[.]', re.IGNORECASE)
        def _sub_r3_en(m):
            nonlocal rules_of_three
            rules_of_three += 1
            return f"On one hand, {m.group(1)}. Simultaneously, {m.group(2)}. Looking further, {m.group(3)}."
        processed_text = r3_en.sub(_sub_r3_en, processed_text)

    # Step 1c: Entity Diversity & Repetition Suppression
    if enable_entity_diversity:
        processed_text, entity_replacements, entity_details = _reduce_entity_repetition(processed_text)

    # Step 2: Burstiness Reshaper (Sentence Length Entropy & Human Cadence Injection)
    short_sentences_created = 0
    if enable_burstiness_boost:
        paragraphs = processed_text.split('\n')
        reshaped_paragraphs = []

        for para in paragraphs:
            if not para.strip():
                reshaped_paragraphs.append(para)
                continue

            para_sentences = _split_into_sentences(para)
            new_para_sentences = []

            for s in para_sentences:
                # Check for long compound Chinese sentences (> 45 chars) with natural clause breaks
                if len(s) > 45 and any(c in s for c in ['，且', '，並', '，同時', '，進而', '，因而']):
                    # Break into punchy short clause
                    for conj in ['，且', '，並', '，同時', '，進而', '，因而']:
                        if conj in s:
                            parts = s.split(conj, 1)
                            p1 = parts[0].strip() + "。"
                            p2 = "這也" + parts[1].strip() if not parts[1].strip().startswith("這") else parts[1].strip()
                            new_para_sentences.extend([p1, p2])
                            short_sentences_created += 1
                            break
                    else:
                        new_para_sentences.append(s)

                # Check for long compound English sentences (> 28 words) with conjunctions
                elif len(s.split()) > 28 and any(conj in s for conj in [', and ', ', which ', ', but ', ', whereas ']):
                    for conj in [', and ', ', which ', ', but ', ', whereas ']:
                        if conj in s:
                            parts = s.split(conj, 1)
                            p1 = parts[0].strip() + "."
                            lead_word = "Indeed, " if conj in [', and ', ', which '] else "Conversely, "
                            p2 = lead_word + parts[1].strip()[0].upper() + parts[1].strip()[1:]
                            new_para_sentences.extend([p1, p2])
                            short_sentences_created += 1
                            break
                    else:
                        new_para_sentences.append(s)
                else:
                    new_para_sentences.append(s)

            # Local entropy check: If paragraph still has uniform long sentences, inject punchy transition
            _, _, local_cv = _calc_burstiness(new_para_sentences)
            if len(new_para_sentences) >= 3 and local_cv < 0.40:
                is_zh = any(ord(c) > 128 for c in para)
                if is_zh:
                    injection = random.choice(HUMAN_PUNCHY_INJECTIONS_ZH)
                    # Insert after 2nd sentence
                    new_para_sentences.insert(2, injection)
                    short_sentences_created += 1
                else:
                    injection = random.choice(HUMAN_PUNCHY_INJECTIONS_EN)
                    new_para_sentences.insert(2, injection)
                    short_sentences_created += 1

            reshaped_paragraphs.append(" ".join(new_para_sentences) if any(ord(c) < 128 for c in para) else "".join(new_para_sentences))

        processed_text = "\n".join(reshaped_paragraphs)

    # Calculate final reshaped metrics
    final_sentences = _split_into_sentences(processed_text)
    reshaped_mean, reshaped_std, reshaped_cv = _calc_burstiness(final_sentences)

    boost_ratio = round(((reshaped_cv - orig_cv) / max(orig_cv, 0.001)) * 100, 1)

    metrics = RestructureMetrics(
        original_sentence_count=len(orig_sentences),
        reshaped_sentence_count=len(final_sentences),
        original_mean_len=orig_mean,
        reshaped_mean_len=reshaped_mean,
        original_std_dev=orig_std,
        reshaped_std_dev=reshaped_std,
        original_cv=orig_cv,
        reshaped_cv=reshaped_cv,
        burstiness_boost_percent=boost_ratio,
        cliches_purged_count=cliches_purged,
        cliche_replacements=cliche_replacements,
        rules_of_three_disrupted=rules_of_three,
        short_punchy_sentences_created=short_sentences_created,
        high_risk_residues_dissolved=high_risk_dissolved,
        entity_diversity_replacements_count=entity_replacements,
        entity_diversity_details=entity_details[:20]
    )

    return RestructureResult(cleaned_text=processed_text, metrics=metrics)
