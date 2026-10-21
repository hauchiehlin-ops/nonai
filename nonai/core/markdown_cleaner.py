"""
Markdown Structure De-perfectionizer and Forensic Sanitizer
Transforms robotic, ultra-rigid Markdown into natural human-like formatting,
purges conversational AI bookends (preamble/postscript), and applies semantic de-patterning
while strictly preserving code blocks and technical syntax.
"""

import random
import re
from dataclasses import dataclass
from typing import List, Tuple
from nonai.core.unicode_cleaner import clean_unicode
from nonai.core.semantic_perturb import perturb_text

@dataclass
class MarkdownCleanResult:
    cleaned_text: str
    unicode_chars_removed: int
    tables_de_perfectionized: int
    headers_adjusted: int
    lists_varied: int
    ai_bookends_removed: int = 0
    semantic_replacements: int = 0
    semantic_reorganized: int = 0


# Conversational AI preambles and postscripts
AI_PREAMBLE_PATTERNS = [
    re.compile(r'^(certainly!?|sure!?|here is|here are|below is|here\'s)\s+(the|a|an|your)?.*?[：:\n]', re.IGNORECASE),
    re.compile(r'^(好的|沒問題|當然可以)[，,、！!。\s]*(以下是|這是|為您整理).*?[：:\n]'),
]

AI_POSTSCRIPT_PATTERNS = [
    re.compile(r'^(hope this helps!?|let me know if you have any (other )?questions!?|feel free to ask).*?$', re.IGNORECASE),
    re.compile(r'^(希望這對你有幫助|如有任何問題歡迎隨時提出|若有需要進一步調整請告訴我).*?$'),
]


def _de_perfectionize_table_line(line: str) -> str:
    """Transform rigid whitespace-padded table lines into natural compact markdown."""
    if not line.strip().startswith('|') or not line.strip().endswith('|'):
        return line
    cells = [c.strip() for c in line.strip().split('|')[1:-1]]
    
    # Check if this is a separator line (e.g. |:---|:---| or |---|---|)
    if all(re.match(r'^:?-+:?$', c) for c in cells if c):
        new_cells = []
        for c in cells:
            if c.startswith(':') and c.endswith(':'):
                new_cells.append(':---:')
            elif c.startswith(':'):
                new_cells.append(':---')
            elif c.endswith(':'):
                new_cells.append('---:')
            else:
                new_cells.append('---')
        return "| " + " | ".join(new_cells) + " |"
    
    return "| " + " | ".join(cells) + " |"


def clean_markdown(
    text: str,
    strip_unicode: bool = True,
    de_perfectionize_tables: bool = True,
    naturalize_headers: bool = True,
    allow_minor_list_variations: bool = True,
    strip_ai_bookends: bool = True,
    enable_perturb: bool = True,
    perturb_intensity: float = 0.65
) -> MarkdownCleanResult:
    """
    Cleans invisible unicode, purges conversational AI bookends, naturalizes tables,
    and applies semantic perturbation to narrative lines while protecting code blocks.
    """
    unicode_removed = 0
    if strip_unicode:
        u_res = clean_unicode(text)
        text = u_res.cleaned_text
        unicode_removed = u_res.total_removed

    lines = text.splitlines()
    tables_count = 0
    headers_count = 0
    lists_count = 0
    bookends_removed = 0
    semantic_replacements = 0
    semantic_reorganized = 0

    # 1. Strip conversational AI preambles from beginning
    if strip_ai_bookends and lines:
        while lines and not lines[0].strip():
            lines.pop(0)
        if lines:
            first_line = lines[0].strip()
            for pat in AI_PREAMBLE_PATTERNS:
                if pat.search(first_line):
                    lines.pop(0)
                    bookends_removed += 1
                    break

    # 2. Strip conversational AI postscripts from end
    if strip_ai_bookends and lines:
        while lines and not lines[-1].strip():
            lines.pop()
        if lines:
            last_line = lines[-1].strip()
            for pat in AI_POSTSCRIPT_PATTERNS:
                if pat.search(last_line):
                    lines.pop()
                    bookends_removed += 1
                    break

    new_lines = []
    in_code_block = False

    for line in lines:
        # Strictly protect code blocks from perturbation
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            new_lines.append(line)
            continue

        if in_code_block:
            new_lines.append(line)
            continue

        processed_line = line

        # Table De-perfection
        if de_perfectionize_tables and processed_line.strip().startswith('|') and processed_line.strip().endswith('|'):
            processed_line = _de_perfectionize_table_line(processed_line)
            tables_count += 1
            new_lines.append(processed_line)
            continue

        # List variations
        if allow_minor_list_variations:
            m = re.match(r'^(\s*)([-*+])\s+(.+)$', processed_line)
            if m:
                indent, marker, content = m.groups()
                if len(indent) >= 2 and random.random() < 0.2:
                    alt_marker = '*' if marker == '-' else '-'
                    processed_line = f"{indent}{alt_marker} {content}"
                    lists_count += 1

        # Headers
        if naturalize_headers and re.match(r'^#{1,6}\s+', processed_line):
            headers_count += 1
            new_lines.append(processed_line)
            continue

        # 3. Apply semantic perturbation to narrative paragraphs (avoid empty lines, blockquotes, code)
        if enable_perturb and processed_line.strip() and not processed_line.strip().startswith(">"):
            p_res = perturb_text(
                processed_line,
                intensity=perturb_intensity,
                disrupt_transitions=True,
                vary_punctuation=True
            )
            processed_line = p_res.perturbed_text
            semantic_replacements += p_res.replacements_made
            semantic_reorganized += p_res.sentences_reorganized

        new_lines.append(processed_line)

    result_text = "\n".join(new_lines)
    if text.endswith("\n") and not result_text.endswith("\n"):
        result_text += "\n"

    return MarkdownCleanResult(
        cleaned_text=result_text,
        unicode_chars_removed=unicode_removed,
        tables_de_perfectionized=tables_count,
        headers_adjusted=headers_count,
        lists_varied=lists_count,
        ai_bookends_removed=bookends_removed,
        semantic_replacements=semantic_replacements,
        semantic_reorganized=semantic_reorganized
    )
