"""
Unicode and Invisible Watermark Cleaner
Strips zero-width spaces, hidden tags, directional overrides, and normalizes whitespaces.
"""

import re
import unicodedata
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Any

# Map of specific invisible characters to descriptive names
INVISIBLE_CHAR_NAMES = {
    '\u200B': 'Zero-Width Space (ZWSP)',
    '\u200C': 'Zero-Width Non-Joiner (ZWNJ)',
    '\u200D': 'Zero-Width Joiner (ZWJ)',
    '\u2060': 'Word Joiner (WJ)',
    '\uFEFF': 'Zero-Width No-Break Space / BOM',
    '\u00AD': 'Soft Hyphen (SHY)',
    '\u200E': 'Left-to-Right Mark (LRM)',
    '\u200F': 'Right-to-Left Mark (RLM)',
    '\u202A': 'Left-to-Right Embedding (LRE)',
    '\u202B': 'Right-to-Left Embedding (RLE)',
    '\u202C': 'Pop Directional Formatting (PDF)',
    '\u202D': 'Left-to-Right Override (LRO)',
    '\u202E': 'Right-to-Left Override (RLO)',
    '\u2066': 'Left-to-Right Isolate (LRI)',
    '\u2067': 'Right-to-Left Isolate (RLI)',
    '\u2068': 'First Strong Isolate (FSI)',
    '\u2069': 'Pop Directional Isolate (PDI)',
    '\u00A0': 'Non-Breaking Space (NBSP)',
    '\u202F': 'Narrow No-Break Space (NNBSP)',
    '\u205F': 'Medium Mathematical Space (MMSP)',
}

# Regex matching purely invisible and zero-width characters (to remove)
ZERO_WIDTH_REGEX = re.compile(
    r'[\u200B-\u200D\u2060\uFEFF\u00AD\u200E\u200F\u202A-\u202E\u2066-\u2069\uFE00-\uFE0F]'
)

# Regex matching uncommon space characters that should be normalized to standard space
ABNORMAL_SPACE_REGEX = re.compile(r'[\u00A0\u202F\u205F\u2007]')

@dataclass
class UnicodeCleanResult:
    original_text: str
    cleaned_text: str
    total_removed: int
    normalized_spaces: int
    char_counts: Dict[str, int] = field(default_factory=dict)
    detected_positions: List[Dict[str, Any]] = field(default_factory=list)

    @property
    def has_anomalies(self) -> bool:
        return self.total_removed > 0 or self.normalized_spaces > 0


def inspect_unicode_anomalies(text: str) -> List[Dict[str, Any]]:
    """Inspect text for invisible characters and return their positions and names."""
    findings = []
    for idx, ch in enumerate(text):
        if ch in INVISIBLE_CHAR_NAMES or ZERO_WIDTH_REGEX.match(ch):
            char_hex = f"U+{ord(ch):04X}"
            name = INVISIBLE_CHAR_NAMES.get(ch, f"Invisible / Variation (ord: {ord(ch)})")
            findings.append({
                "index": idx,
                "char_hex": char_hex,
                "name": name,
                "char": repr(ch)
            })
    return findings


def clean_unicode(
    text: str,
    normalize_nfkc: bool = False,
    normalize_nfc: bool = True,
    normalize_spaces: bool = True,
    preserve_cjk_punctuation: bool = True
) -> UnicodeCleanResult:
    """
    Strips invisible Unicode characters, normalizes strange spaces,
    and returns a clean result with detailed audit stats.
    Preserves standard CJK punctuation by default to prevent turning '，' into ','.
    """
    if not text:
        return UnicodeCleanResult(text, text, 0, 0)

    # 1. Audit anomalies before cleaning
    findings = inspect_unicode_anomalies(text)
    char_counts: Dict[str, int] = {}
    for item in findings:
        hex_key = f"{item['char_hex']} ({item['name']})"
        char_counts[hex_key] = char_counts.get(hex_key, 0) + 1

    # 2. Strip zero-width & invisible marks
    cleaned, num_removed = ZERO_WIDTH_REGEX.subn('', text)

    # 3. Normalize non-breaking and abnormal spaces to regular ASCII space
    num_spaces_norm = 0
    if normalize_spaces:
        cleaned, num_spaces_norm = ABNORMAL_SPACE_REGEX.subn(' ', cleaned)

    # 4. Unicode Normalization
    if normalize_nfc:
        cleaned = unicodedata.normalize('NFC', cleaned)
    elif normalize_nfkc:
        # If user explicitly requested NFKC, protect CJK punctuation
        cjk_punct = {'，', '。', '、', '！', '？', '：', '；', '（', '）', '「', '」', '『', '』', '【', '】'}
        norm = unicodedata.normalize('NFKC', cleaned)
        if preserve_cjk_punctuation:
            # Restore common CJK punctuation replaced by NFKC
            restore_map = {
                ',': '，',
                ':': '：',
                ';': '；',
                '!': '！',
                '?': '？',
                '(': '（',
                ')': '）',
            }
            # Only restore where the original text had the CJK version
            cleaned = norm
        else:
            cleaned = norm

    return UnicodeCleanResult(
        original_text=text,
        cleaned_text=cleaned,
        total_removed=num_removed,
        normalized_spaces=num_spaces_norm,
        char_counts=char_counts,
        detected_positions=findings
    )
