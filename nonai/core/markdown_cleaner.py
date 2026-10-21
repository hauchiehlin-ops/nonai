"""
Markdown Structure De-perfectionizer and Sanitizer
Transforms robotic, ultra-rigid Markdown into natural human-like formatting.
"""

import random
import re
from dataclasses import dataclass
from typing import List, Tuple
from nonai.core.unicode_cleaner import clean_unicode

@dataclass
class MarkdownCleanResult:
    cleaned_text: str
    unicode_chars_removed: int
    tables_de_perfectionized: int
    headers_adjusted: int
    lists_varied: int


def _de_perfectionize_table_line(line: str) -> str:
    """Transform rigid whitespace-padded table lines into natural compact markdown."""
    if not line.strip().startswith('|') or not line.strip().endswith('|'):
        return line
    cells = [c.strip() for c in line.strip().split('|')[1:-1]]
    
    # Check if this is a separator line (e.g. |:---|:---| or |---|---|)
    if all(re.match(r'^:?-+:?$', c) for c in cells if c):
        # Simplify separator to standard human-style | --- | --- |
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
    
    # Regular row: compact single-space padding
    return "| " + " | ".join(cells) + " |"


def clean_markdown(
    text: str,
    strip_unicode: bool = True,
    de_perfectionize_tables: bool = True,
    naturalize_headers: bool = True,
    allow_minor_list_variations: bool = True
) -> MarkdownCleanResult:
    """
    Cleans invisible unicode and applies humanization heuristics to markdown structures.
    """
    unicode_removed = 0
    if strip_unicode:
        u_res = clean_unicode(text)
        text = u_res.cleaned_text
        unicode_removed = u_res.total_removed

    lines = text.splitlines()
    new_lines = []
    tables_count = 0
    headers_count = 0
    lists_count = 0

    in_code_block = False

    for i, line in enumerate(lines):
        # Preserve code blocks exactly
        if line.strip().startswith("```"):
            in_code_block = not in_code_block
            new_lines.append(line)
            continue

        if in_code_block:
            new_lines.append(line)
            continue

        processed_line = line

        # 1. Table De-perfection
        if de_perfectionize_tables and processed_line.strip().startswith('|') and processed_line.strip().endswith('|'):
            processed_line = _de_perfectionize_table_line(processed_line)
            tables_count += 1

        # 2. List variations (simulate human occasional marker choice)
        if allow_minor_list_variations:
            # Check for bullet list item: "^(\s*)([-*+])\s+"
            m = re.match(r'^(\s*)([-*+])\s+(.+)$', processed_line)
            if m:
                indent, marker, content = m.groups()
                # If robotic all `- `, introduce subtle human variation for sub-bullets
                if len(indent) >= 2 and random.random() < 0.2:
                    alt_marker = '*' if marker == '-' else '-'
                    processed_line = f"{indent}{alt_marker} {content}"
                    lists_count += 1

        # 3. Headers
        if naturalize_headers and re.match(r'^#{1,6}\s+', processed_line):
            headers_count += 1

        new_lines.append(processed_line)

    result_text = "\n".join(new_lines)
    if text.endswith("\n") and not result_text.endswith("\n"):
        result_text += "\n"

    return MarkdownCleanResult(
        cleaned_text=result_text,
        unicode_chars_removed=unicode_removed,
        tables_de_perfectionized=tables_count,
        headers_adjusted=headers_count,
        lists_varied=lists_count
    )
