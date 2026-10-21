"""
Semantic and Statistical Watermark Disruptor
Breaks n-gram prediction chains, disrupts SynthID green-token distributions,
and enhances human sentence burstiness.
"""

import random
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

# Common robotic AI transitional phrases and their human-like alternatives (Chinese & English)
AI_CLICHE_MAP_ZH = {
    "值得注意的是": ["另外", "注意", "同時", "不過也要看到"],
    "總結來說": ["簡單來說", "整體看來", "總結而言", "概括地說"],
    "綜上所述": ["綜合以上", "整體而言", "總之"],
    "不可否認的是": ["確實", "無疑地", "平心而論"],
    "顯著提升": ["明顯增加", "大幅改善", "顯著改善", "有效提高"],
    "深入探討": ["詳細分析", "進一步討論", "仔細看看", "檢視"],
    "至關重要": ["非常重要", "關鍵所在", "十分核心", "很關鍵"],
    "扮演著重要的角色": ["起到了關鍵作用", "十分關鍵", "具有重要影響"],
    "在當今快節奏的世界中": ["現今", "在目前環境下", "當前"],
    "這不僅僅是...更是...": ["除了...也是..."],
}

AI_CLICHE_MAP_EN = {
    "delve into": ["explore", "examine", "look into", "analyze"],
    "testament to": ["proof of", "evidence of", "sign of"],
    "crucial": ["key", "essential", "important", "vital"],
    "tapestry": ["mix", "blend", "combination", "collection"],
    "furthermore": ["also", "in addition", "plus"],
    "moreover": ["besides", "also", "on top of that"],
    "in summary": ["all in all", "in short", "overall"],
    "it is worth noting that": ["notably", "keep in mind that", "importantly"],
    "plays a crucial role": ["is key", "is essential", "matters greatly"],
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
    intensity: float = 0.5,  # 0.0 to 1.0
    disrupt_transitions: bool = True,
    vary_punctuation: bool = True
) -> PerturbResult:
    """
    Perturbs n-grams and token probabilities to disrupt statistical watermarks (SynthID)
    without degrading the semantic coherence.
    """
    if not text:
        return PerturbResult(text, text, 0, 0, 0.0)

    replacements = 0
    reorganized = 0
    output_text = text

    # 1. Replace AI cliché phrases with varied alternatives
    if disrupt_transitions:
        # Chinese clichés
        for phrase, alternatives in AI_CLICHE_MAP_ZH.items():
            if phrase in output_text:
                matches = output_text.count(phrase)
                for _ in range(matches):
                    if random.random() < (0.4 + 0.6 * intensity):
                        chosen = random.choice(alternatives)
                        # Replace one occurrence
                        output_text = output_text.replace(phrase, chosen, 1)
                        replacements += 1

        # English clichés (case-insensitive boundary match)
        for phrase, alternatives in AI_CLICHE_MAP_EN.items():
            pattern = re.compile(rf'\b{re.escape(phrase)}\b', re.IGNORECASE)
            def replace_match(m):
                nonlocal replacements
                if random.random() < (0.4 + 0.6 * intensity):
                    replacements += 1
                    choice = random.choice(alternatives)
                    # Preserve uppercase if original had it
                    if m.group(0)[0].isupper():
                        choice = choice.capitalize()
                    return choice
                return m.group(0)

            output_text = pattern.sub(replace_match, output_text)

    # 2. Punctuation and sentence structure variation
    # LLMs produce very uniform sentence lengths and standard punctuation.
    if vary_punctuation and intensity > 0.3:
        # For Chinese: occasionally adjust comma / period patterns
        lines = output_text.splitlines()
        new_lines = []
        for line in lines:
            if not line.strip() or line.strip().startswith("#") or line.strip().startswith("-"):
                new_lines.append(line)
                continue

            # Split clauses by commas
            clauses = line.split("，")
            if len(clauses) > 3 and random.random() < (intensity * 0.4):
                # Split a very long sentence into two by turning one comma into a period
                split_idx = len(clauses) // 2
                clauses[split_idx] = "。" + clauses[split_idx]
                line = "，".join(clauses).replace("，。", "。")
                reorganized += 1
            new_lines.append(line)
        output_text = "\n".join(new_lines)

    total_words = len(text.split()) if " " in text else len(text)
    disruption_rate = round(min(1.0, (replacements * 4 + reorganized * 6) / max(10, total_words)), 3)

    return PerturbResult(
        original_text=text,
        perturbed_text=output_text,
        replacements_made=replacements,
        sentences_reorganized=reorganized,
        estimated_ngram_disruption_rate=disruption_rate
    )
