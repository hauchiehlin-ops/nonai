"""
Semantic and Statistical Watermark Disruptor
Breaks n-gram prediction chains, disrupts SynthID green-token distributions,
neutralizes AI academic clichés and parallel formulas, and enhances human sentence burstiness.
"""

import random
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

# Comprehensive mapping of AI clichés, formulas, robotic transitions, and hedges (Chinese & English)
AI_CLICHE_MAP_ZH: Dict[str, List[str]] = {
    # Discourse & Transitional Clichés
    "值得注意的是": ["同時亦須留意", "另外不可忽略的是", "在脈絡上也應看到", "同時需要關注的是"],
    "值得一提的是": ["特別需要指出的是", "另一個關鍵點在於", "值得觀察的是", "補充說明的是"],
    "總結來說": ["綜觀上述分析", "整體歸納而言", "總括而論", "綜合前述脈絡"],
    "綜上所述": ["綜合前述分析", "整體而言", "總括來看", "立足於上述考量"],
    "總結而言": ["整體歸納而言", "綜合上述脈絡", "總括而論"],
    "概括地說": ["簡要歸納", "整體觀之", "由宏觀角度而言"],
    "不可否認的是": ["平心而論", "就客觀實證來看", "不難理解的是", "客觀檢驗下"],
    "毋庸置疑": ["顯而易見", "確切而言", "事實上"],
    "顯著提升": ["帶來實質增益", "呈現明顯改善", "大幅提高", "有效促進"],
    "顯著增加": ["呈現明顯增長", "大幅增長", "有感增加"],
    "深入探討": ["周延檢視", "系統性檢驗", "仔細爬梳", "進行深入分析"],
    "深入分析": ["周延分析", "系統性剖析", "嚴謹檢驗"],
    "至關重要": ["具關鍵樞紐地位", "屬於核心關鍵", "具決定性影響", "具高度實質價值"],
    "扮演著重要的角色": ["發揮核心關鍵功能", "扮演樞紐角色", "居於關鍵推動地位"],
    "扮演著重要角色": ["發揮核心樞紐功能", "扮演關鍵地位", "居於重要角色"],
    "扮演關鍵角色": ["居於關鍵樞紐地位", "發揮決定性作用", "佔有舉足輕重之地位"],
    "在當今快節奏的世界中": ["面對現今快速演進的環境", "在當前步調緊湊的社會脈絡下", "在瞬息萬變的環境中"],
    "在當今數位化時代": ["在當前數位轉型的脈絡下", "置身現今數位生態中", "在數位化深化的今日"],
    "這不僅僅是...更是...": ["除了...之餘，更深層的意涵在於...", "在...之際，更實質展現出..."],
    "有助於": ["利於推動", "有益於", "能實質促進", "利於落實"],
    "旨在": ["核心目的在於", "意在", "聚焦於", "主要立足於"],
    "以期": ["進而能", "致力於達成", "以求能"],
    "換言之": ["具體來說", "也就是說", "進一步釐清而言"],
    "具體而言": ["進一步檢視", "在實務細節上", "就實施層面而言"],
    "全面檢視": ["系統性檢驗", "通盤審視", "周延評估"],
    "全面提升": ["通盤改善", "大幅優化", "有效推升"],
    "為...奠定基礎": ["為...提供了有力支撐", "拓寬了...的研究路徑", "奠定了堅實根基"],

    # Claude & GPT Specific Academic Phrases
    "方法論本身就是主角": [
        "本研究的核心亮點在於方法論的創新重構",
        "本計畫將方法架構創新視為核心關鍵",
        "方法論設計本身即為本計畫之主要突破點"
    ],
    "各自嵌入資料探勘核心": [
        "分別導入相應的資料探勘核心模組",
        "各自整合特定的資料科學演算法",
        "分別嵌入專屬的資料探勘演算法核心"
    ],
    "串成一條研究管線": [
        "串聯為連貫的端到端研究架構",
        "構築出系統化的分析流程路徑",
        "整合為一貫的研究技術管線"
    ],
    "各有面對消費者異質性時的盲點": [
        "在處理消費者異質性特徵時普遍存在方法學上的局限",
        "面對多元的消費者異質感知時各有其方法學盲區",
        "在捕捉消費者異質性維度上均存在既有研究視角之局限"
    ],
    "讓消費者族群由資料發現": [
        "促使消費者異質族群直接由實證資料驅動呈現",
        "由客觀資料自動導出潛在的消費者區隔特徵",
        "使異質受眾輪廓完全自實證數據中自然浮現"
    ],
    "用以證明方法可跨品類推廣": [
        "藉以驗證方法論跨領域推廣的外部效度",
        "用以確立此分析架構在不同品類間的通用性與延展度",
        "以嚴謹檢驗此方法論跨品類應用的穩健性"
    ],
    "前一階段的發現是後一階段的假設": [
        "前階段之實證發現隨即轉化為次階段檢驗的理論假說",
        "前期所獲之探索性成果直接作為後續階段的嚴格檢驗假設"
    ],
    "理論引導的資料探勘": [
        "以理論為依歸的資料探勘架構",
        "理論深化驅動之資料探勘路徑"
    ],
    "學術上，": ["在學術理論發展層面，", "就學術理論貢獻而言，", "從學術深化的角度看，"],
    "實務上，": ["於產業實務應用中，", "在產業務實操作層面，", "就商業實務轉譯而言，"],
    "社會面上，": ["在社會福祉與公共效益方面，", "從社會公共意涵與永續面向評估，", "在廣泛的社會價值層次上，"],
    "理論上，": ["在理論架構層次，", "從學理脈絡觀之，", "就基礎理論而言，"],
    "方法上，": ["在研究方法設計方面，", "就方法論架構而言，", "由技術實施路徑切入，"],
    "實踐上，": ["在實務落地推行時，", "於具體實踐層面，", "在實務運作層次，"],
}

AI_CLICHE_MAP_EN: Dict[str, List[str]] = {
    "delve into": ["explore", "examine", "investigate", "analyze in detail"],
    "testament to": ["proof of", "evidence of", "demonstration of", "reflection of"],
    "crucial": ["pivotal", "key", "essential", "vital", "foundational"],
    "tapestry": ["complex interplay", "rich combination", "mosaic", "framework"],
    "furthermore": ["in addition", "moreover", "beyond this", "additionally"],
    "moreover": ["in addition", "furthermore", "equally important"],
    "in summary": ["to encapsulate", "taken together", "on the whole", "in brief"],
    "it is worth noting that": ["notably", "significantly", "an essential facet is that", "importantly"],
    "plays a crucial role": ["is pivotal", "acts as a cornerstone", "drives", "is instrumental"],
    "plays an important role": ["serves a key function", "matters significantly", "is influential"],
    "foster": ["encourage", "support", "cultivate", "nurture"],
    "harness": ["utilize", "leverage", "apply", "employ"],
    "seamlessly": ["fluidly", "cohesively", "smoothly", "naturally"],
    "beacon": ["benchmark", "guiding standard", "model"],
    "cutting-edge": ["advanced", "novel", "frontier", "state-of-the-art"],
    "revolutionize": ["transform", "significantly reshape", "modernize"],
    "underscores": ["highlights", "reinforces", "emphasizes", "indicates"],
}

@dataclass
class PerturbResult:
    original_text: str
    perturbed_text: str
    replacements_made: int
    sentences_reorganized: int
    estimated_ngram_disruption_rate: float


def perturb_text(
    text: str,
    intensity: float = 0.65,  # 0.0 to 1.0
    disrupt_transitions: bool = True,
    vary_punctuation: bool = True
) -> PerturbResult:
    """
    Perturbs n-grams and token probabilities to disrupt statistical watermarks (SynthID),
    breaks transformer detector classifier features, and enhances human sentence burstiness.
    """
    if not text:
        return PerturbResult(text, text, 0, 0, 0.0)

    replacements = 0
    reorganized = 0
    output_text = text

    # 1. Structural Regex Rewriting for Academic Discourse Markers
    if disrupt_transitions:
        # Triples: 學術上... 實務上... 社會面上...
        triple_pat = re.compile(
            r'學術上[，,]\s*(.*?)[。.]\s*實務上[，,]\s*(.*?)[。.]\s*社會面上[，,]\s*(.*?)[。.]'
        )
        def replace_triple(m):
            nonlocal replacements, reorganized
            replacements += 3
            reorganized += 1
            return (
                f"在學術理論深化層面，{m.group(1)}；於產業實務應用中，{m.group(2)}；"
                f"而在社會福祉與公共效益方面，{m.group(3)}。"
            )
        output_text = triple_pat.sub(replace_triple, output_text)

        # 2. Chinese Cliché and AI Academic Phrase Replacements
        for phrase, alternatives in AI_CLICHE_MAP_ZH.items():
            if phrase in output_text:
                matches = output_text.count(phrase)
                for _ in range(matches):
                    # Higher probability of replacement when intensity is high
                    if random.random() < (0.55 + 0.45 * intensity):
                        chosen = random.choice(alternatives)
                        output_text = output_text.replace(phrase, chosen, 1)
                        replacements += 1

        # 3. English Cliché Replacements
        for phrase, alternatives in AI_CLICHE_MAP_EN.items():
            pattern = re.compile(rf'\b{re.escape(phrase)}\b', re.IGNORECASE)
            def replace_match(m):
                nonlocal replacements
                if random.random() < (0.55 + 0.45 * intensity):
                    replacements += 1
                    choice = random.choice(alternatives)
                    if m.group(0)[0].isupper():
                        choice = choice.capitalize()
                    return choice
                return m.group(0)

            output_text = pattern.sub(replace_match, output_text)

    # 4. Burstiness & Punctuation Rhythm Optimization
    # LLMs produce highly uniform clause lengths and repetitive semicolon patterns.
    if vary_punctuation and intensity > 0.25:
        lines = output_text.splitlines()
        new_lines = []
        for line in lines:
            trimmed = line.strip()
            # Skip tables, markdown headers, and code
            if not trimmed or trimmed.startswith("#") or trimmed.startswith("|") or trimmed.startswith("-"):
                new_lines.append(line)
                continue

            # (A) De-chain repetitive semicolons (；)
            if line.count("；") >= 2 and random.random() < (intensity * 0.75):
                semicolon_parts = line.split("；")
                # Turn the middle or last semicolon into a period with transitional connective
                idx = len(semicolon_parts) // 2
                connectors = ["與此同時，", "在此基礎上，", "就此面向而言，", "相應地，"]
                semicolon_parts[idx] = "。" + random.choice(connectors) + semicolon_parts[idx]
                line = "；".join(semicolon_parts).replace("；。", "。")
                reorganized += 1

            # (B) Break long uniform comma chains into natural breathing points
            clauses = line.split("，")
            if len(clauses) >= 4 and random.random() < (intensity * 0.6):
                split_idx = len(clauses) // 2
                clauses[split_idx] = "。" + clauses[split_idx]
                line = "，".join(clauses).replace("，。", "。")
                reorganized += 1

            new_lines.append(line)
        output_text = "\n".join(new_lines)

    total_words = len(text.split()) if " " in text else len(text)
    disruption_rate = round(min(1.0, (replacements * 5 + reorganized * 8) / max(10, total_words)), 3)

    return PerturbResult(
        original_text=text,
        perturbed_text=output_text,
        replacements_made=replacements,
        sentences_reorganized=reorganized,
        estimated_ngram_disruption_rate=disruption_rate
    )
