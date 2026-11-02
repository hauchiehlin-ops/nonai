"""
DOCX Sanitizer and RSID Biomimetic Injector
Cleans web CSS/HTML artifacts, spoofs complete Microsoft Office Word package metadata,
purges all AI provenance tags (e.g. Claude Docs, Anthropic), synthesizes mandatory Word files
(fontTable.xml, webSettings.xml, theme1.xml), applies paragraph-level deep semantic humanization
and citation anchoring, forcibly highlights all modified text spans with yellow highlighter
(<w:highlight w:val="yellow"/>), and enforces strict cross-file RSID & revision invariants.
"""

import difflib
import io
import os
import random
import re
import zipfile
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Set
from lxml import etree

from nonai.core.unicode_cleaner import clean_unicode
from nonai.core.semantic_perturb import perturb_text, PerturbResult
from nonai.core.semantic_restructure import restructure_semantics_and_burstiness, RestructureResult
from nonai.core.fact_citation_auditor import (
    audit_fact_citations,
    bind_citations_and_hedge,
    FactCitationAuditResult,
    PATTERNS_REF_HEADER,
)

# OpenXML Namespaces
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
CP_NS = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC_NS = "http://purl.org/dc/elements/1.1/"
DCTERMS_NS = "http://purl.org/dc/terms/"
EP_NS = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
PR_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
A_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
XML_SPACE = "{http://www.w3.org/XML/1998/namespace}space"

NSMAP = {
    "w": W_NS,
    "cp": CP_NS,
    "dc": DC_NS,
    "dcterms": DCTERMS_NS,
    "ep": EP_NS,
    "xsi": XSI_NS,
}

DEFAULT_SETTINGS_XML = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" mc:Ignorable="w14 w15">
  <w:defaultTabStop w:val="720"/>
  <w:characterSpacingControl w:val="doNotCompress"/>
  <w:compat>
    <w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/>
  </w:compat>
</w:settings>"""

DEFAULT_FONTTABLE_XML = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:fonts xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" mc:Ignorable="w14 w15">
  <w:font w:name="Calibri">
    <w:panose1 w:val="020F0502020204030204"/>
    <w:charset w:val="00"/>
    <w:family w:val="swiss"/>
    <w:pitch w:val="variable"/>
    <w:sig w:usb0="E0002AFF" w:usb1="C000247B" w:usb2="00000009" w:usb3="00000000" w:csb0="000001FF" w:csb1="00000000"/>
  </w:font>
  <w:font w:name="Times New Roman">
    <w:panose1 w:val="02020603050405020304"/>
    <w:charset w:val="00"/>
    <w:family w:val="roman"/>
    <w:pitch w:val="variable"/>
    <w:sig w:usb0="E0002EFF" w:usb1="C000785B" w:usb2="00000009" w:usb3="00000000" w:csb0="000001FF" w:csb1="00000000"/>
  </w:font>
  <w:font w:name="\xe5\xbe\xae\xe8\xbb\x9f\xe6\xad\xa3\xe9\xbb\x91\xe9\xab\x94">
    <w:altName w:val="Microsoft JhengHei"/>
    <w:panose1 w:val="020B0604030504040204"/>
    <w:charset w:val="88"/>
    <w:family w:val="swiss"/>
    <w:pitch w:val="variable"/>
    <w:sig w:usb0="800002BF" w:usb1="3807FCDF" w:usb2="00000010" w:usb3="00000000" w:csb0="00100001" w:csb1="00000000"/>
  </w:font>
  <w:font w:name="\xe6\x96\xb0\xe7\xb4\xb0\xe6\x98\x8e\xe9\xab\x94">
    <w:altName w:val="PMingLiU"/>
    <w:panose1 w:val="02020500000000000000"/>
    <w:charset w:val="88"/>
    <w:family w:val="roman"/>
    <w:pitch w:val="variable"/>
    <w:sig w:usb0="800002BF" w:usb1="3807FCDF" w:usb2="00000010" w:usb3="00000000" w:csb0="00100001" w:csb1="00000000"/>
  </w:font>
</w:fonts>"""

DEFAULT_WEBSETTINGS_XML = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:webSettings xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" mc:Ignorable="w14 w15">
  <w:optimizeForBrowser/>
  <w:allowPNG/>
  <w:relyOnVML/>
</w:webSettings>"""

DEFAULT_THEME1_XML = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Office Theme">
  <a:themeElements>
    <a:clrScheme name="Office">
      <a:dk1><a:sysClr val="windowText" lastClr="000000"/></a:dk1>
      <a:lt1><a:sysClr val="window" lastClr="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="44546A"/></a:dk2>
      <a:lt2><a:srgbClr val="E7E6E6"/></a:lt2>
      <a:accent1><a:srgbClr val="4472C4"/></a:accent1>
      <a:accent2><a:srgbClr val="ED7D31"/></a:accent2>
      <a:accent3><a:srgbClr val="A5A5A5"/></a:accent3>
      <a:accent4><a:srgbClr val="FFC000"/></a:accent4>
      <a:accent5><a:srgbClr val="5B9BD5"/></a:accent5>
      <a:accent6><a:srgbClr val="70AD47"/></a:accent6>
      <a:hlink><a:srgbClr val="0563C1"/></a:hlink>
      <a:folHlink><a:srgbClr val="954F72"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="Office">
      <a:majorFont>
        <a:latin typeface="Calibri Light" panose="020F0302020204030204"/>
        <a:ea typeface=""/>
        <a:cs typeface=""/>
      </a:majorFont>
      <a:minorFont>
        <a:latin typeface="Calibri" panose="020F0502020204030204"/>
        <a:ea typeface=""/>
        <a:cs typeface=""/>
      </a:minorFont>
    </a:fontScheme>
    <a:fmtScheme name="Office">
      <a:fillStyleLst>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
        <a:gradFill rotWithShape="1"><a:gsLst><a:gs pos="0"><a:schemeClr val="phClr"><a:lumOff val="20000"/></a:schemeClr></a:gs><a:gs pos="100000"><a:schemeClr val="phClr"><a:lumOff val="10000"/></a:schemeClr></a:gs></a:gsLst><a:lin ang="16200000" scaled="1"/></a:gradFill>
        <a:gradFill rotWithShape="1"><a:gsLst><a:gs pos="0"><a:schemeClr val="phClr"><a:tint val="40000"/></a:schemeClr></a:gs><a:gs pos="100000"><a:schemeClr val="phClr"><a:tint val="80000"/></a:schemeClr></a:gs></a:gsLst><a:lin ang="16200000" scaled="1"/></a:gradFill>
      </a:fillStyleLst>
      <a:lnStyleLst>
        <a:ln w="9525" cap="flat" cmpd="s" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>
        <a:ln w="25400" cap="flat" cmpd="s" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>
        <a:ln w="38100" cap="flat" cmpd="s" algn="ctr"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>
      </a:lnStyleLst>
      <a:effectStyleLst>
        <a:effectStyle><a:effectLst/></a:effectStyle>
        <a:effectStyle><a:effectLst/></a:effectStyle>
        <a:effectStyle><a:effectLst/></a:effectStyle>
      </a:effectStyleLst>
      <a:bgFillStyleLst>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
        <a:gradFill rotWithShape="1"><a:gsLst><a:gs pos="0"><a:schemeClr val="phClr"><a:tint val="40000"/></a:schemeClr></a:gs><a:gs pos="100000"><a:schemeClr val="phClr"><a:tint val="80000"/></a:schemeClr></a:gs></a:gsLst><a:lin ang="16200000" scaled="1"/></a:gradFill>
        <a:gradFill rotWithShape="1"><a:gsLst><a:gs pos="0"><a:schemeClr val="phClr"><a:tint val="40000"/></a:schemeClr></a:gs><a:gs pos="100000"><a:schemeClr val="phClr"><a:tint val="80000"/></a:schemeClr></a:gs></a:gsLst><a:lin ang="16200000" scaled="1"/></a:gradFill>
      </a:bgFillStyleLst>
    </a:fmtScheme>
  </a:themeElements>
  <a:objectDefaults/>
  <a:extraClrSchemeLst/>
</a:theme>"""


@dataclass
class DocxSanitizeResult:
    cleaned_bytes: bytes
    total_rsids_injected: int
    paragraphs_modified: int
    runs_split: int
    ghost_styles_removed: int
    metadata_spoofed: bool
    unicode_chars_removed: int
    original_rsid_count: int
    final_rsid_count: int
    estimated_human_minutes: int
    rsid_pool: List[str] = field(default_factory=list)
    ghost_style_items: List[str] = field(default_factory=list)
    split_samples: List[Dict[str, str]] = field(default_factory=list)
    metadata_spoof_details: Dict[str, Any] = field(default_factory=dict)
    semantic_replacements: int = 0
    semantic_reorganized: int = 0
    claude_signatures_purged: int = 0
    missing_parts_synthesized: List[str] = field(default_factory=list)
    stage1_restructure_metrics: Optional[Dict[str, Any]] = None
    stage2_fact_citation_audit: Optional[Dict[str, Any]] = None
    highlighted_changes: int = 0


def _generate_rsid_pool(count: int = 30) -> List[str]:
    """Generate a pool of realistic 8-digit hexadecimal RSID strings."""
    pool = set()
    while len(pool) < count:
        val = random.randint(0x00010000, 0x00FFFFFF)
        pool.add(f"{val:08X}")
    return sorted(list(pool))


def _is_inside_table(elem: etree._Element) -> bool:
    """Check if an XML element is inside a table, table cell, or table properties."""
    curr = elem.getparent()
    while curr is not None:
        tag = curr.tag
        if tag in (f"{{{W_NS}}}tc", f"{{{W_NS}}}tbl", f"{{{W_NS}}}tcPr", f"{{{W_NS}}}tblPr", f"{{{W_NS}}}trPr"):
            return True
        curr = curr.getparent()
    return False


def _is_inside_drawing_or_shape(elem: etree._Element) -> bool:
    """Check if an XML element is inside DrawingML, VML, SmartArt, or shape containers."""
    curr = elem.getparent()
    while curr is not None:
        tag = curr.tag.lower()
        if any(marker in tag for marker in ("drawing", "pict", "shape", "graphic", "dgm", "omath")):
            return True
        curr = curr.getparent()
    return False


def _clone_rpr_with_yellow_highlight(
    base_rpr: Optional[etree._Element],
    enable_highlight: bool = True
) -> etree._Element:
    """
    Clones an existing <w:rPr> (or creates a new one) and forcibly injects
    <w:highlight w:val="yellow"/> in ECMA-376 compliant schema order.
    """
    if base_rpr is not None:
        rpr = etree.fromstring(etree.tostring(base_rpr))
    else:
        rpr = etree.Element(f"{{{W_NS}}}rPr")

    if not enable_highlight:
        return rpr

    # Remove any pre-existing w:highlight to prevent duplicate elements
    for old_hl in list(rpr.findall(f"{{{W_NS}}}highlight")):
        rpr.remove(old_hl)

    hl_elem = etree.Element(f"{{{W_NS}}}highlight")
    hl_elem.set(f"{{{W_NS}}}val", "yellow")

    # ECMA-376 CT_RPr element ordering: w:highlight comes before w:u, w:effect, w:bdr, w:shd, w:fitText, w:vertAlign, w:rtl, w:cs, w:em, w:lang
    after_tags = {
        f"{{{W_NS}}}u",
        f"{{{W_NS}}}effect",
        f"{{{W_NS}}}bdr",
        f"{{{W_NS}}}shd",
        f"{{{W_NS}}}fitText",
        f"{{{W_NS}}}vertAlign",
        f"{{{W_NS}}}rtl",
        f"{{{W_NS}}}cs",
        f"{{{W_NS}}}em",
        f"{{{W_NS}}}lang",
        f"{{{W_NS}}}eastAsianLayout",
        f"{{{W_NS}}}specVanish",
        f"{{{W_NS}}}oMath",
    }
    inserted = False
    for idx, child in enumerate(rpr):
        if child.tag in after_tags:
            rpr.insert(idx, hl_elem)
            inserted = True
            break
    if not inserted:
        rpr.append(hl_elem)

    return rpr


def _is_simple_narrative_paragraph(p: etree._Element) -> bool:
    """
    Checks whether a paragraph <w:p> consists of standard text runs (<w:r> with only <w:rPr> and <w:t>)
    so that its full text can be safely merged, restructured at paragraph level, diffed, and rebuilt
    with yellow highlights on modified segments without losing any inline objects (hyperlinks, fields, drawings).
    """
    if _is_inside_table(p) or _is_inside_drawing_or_shape(p):
        return False

    allowed_p_children = {
        f"{{{W_NS}}}pPr",
        f"{{{W_NS}}}r",
        f"{{{W_NS}}}bookmarkStart",
        f"{{{W_NS}}}bookmarkEnd",
        f"{{{W_NS}}}proofErr",
    }
    has_text_run = False
    for child in p:
        if child.tag not in allowed_p_children:
            return False
        if child.tag == f"{{{W_NS}}}r":
            for r_child in child:
                if r_child.tag not in (f"{{{W_NS}}}rPr", f"{{{W_NS}}}t"):
                    return False
                if r_child.tag == f"{{{W_NS}}}t" and r_child.text:
                    has_text_run = True
    return has_text_run


def _rebuild_paragraph_runs_with_diff_highlights(
    p: etree._Element,
    orig_text: str,
    new_text: str,
    char_rpr_list: List[Optional[etree._Element]],
    highlight_changes: bool = True,
    force_highlight_if_equal: bool = False
) -> int:
    """
    Rebuilds the <w:r> children of paragraph `p` by comparing `orig_text` and `new_text`
    via difflib.SequenceMatcher:
    - Unchanged spans ('equal') preserve their original <w:rPr>.
    - Modified or inserted spans ('replace', 'insert') receive their corresponding <w:rPr>
      PLUS mandatory <w:highlight w:val="yellow"/>!
    - If a pure deletion occurred ('delete' with no 'replace'/'insert') or unicode was stripped,
      marks the adjacent character run with yellow highlight so every sanitized change is visible.
    Returns the number of highlighted modification spans created.
    """
    # Collect and remove existing <w:r> and <w:proofErr> elements while keeping <w:pPr> and bookmarks
    for child in list(p):
        if child.tag in (f"{{{W_NS}}}r", f"{{{W_NS}}}proofErr"):
            p.remove(child)

    default_rpr = char_rpr_list[0] if char_rpr_list else None
    highlighted_spans_count = 0

    def get_rpr_at(orig_idx: int) -> Optional[etree._Element]:
        if not char_rpr_list:
            return None
        clamped = max(0, min(orig_idx, len(char_rpr_list) - 1))
        return char_rpr_list[clamped]

    def append_run(text_segment: str, base_rpr: Optional[etree._Element], is_highlighted: bool):
        nonlocal highlighted_spans_count
        if not text_segment:
            return
        r_elem = etree.Element(f"{{{W_NS}}}r")
        if is_highlighted and highlight_changes:
            rpr_to_use = _clone_rpr_with_yellow_highlight(base_rpr, enable_highlight=True)
            r_elem.append(rpr_to_use)
            r_elem.set("data-nonai-highlighted", "1")
            highlighted_spans_count += 1
        elif base_rpr is not None:
            r_elem.append(etree.fromstring(etree.tostring(base_rpr)))

        t_elem = etree.SubElement(r_elem, f"{{{W_NS}}}t")
        if text_segment.startswith(" ") or text_segment.endswith(" ") or "  " in text_segment:
            t_elem.set(XML_SPACE, "preserve")
        t_elem.text = text_segment
        p.append(r_elem)

    if orig_text == new_text:
        if force_highlight_if_equal and highlight_changes:
            append_run(new_text, default_rpr, is_highlighted=True)
        else:
            # Group consecutive characters that share the exact same rPr object
            if not new_text:
                return 0
            seg_start = 0
            curr_rpr = get_rpr_at(0)
            for idx in range(1, len(new_text)):
                next_rpr = get_rpr_at(idx)
                if next_rpr is not curr_rpr:
                    append_run(new_text[seg_start:idx], curr_rpr, is_highlighted=False)
                    seg_start = idx
                    curr_rpr = next_rpr
            append_run(new_text[seg_start:], curr_rpr, is_highlighted=False)
        return highlighted_spans_count

    matcher = difflib.SequenceMatcher(None, orig_text, new_text, autojunk=False)
    opcodes = matcher.get_opcodes()

    has_replace_or_insert = any(tag in ("replace", "insert") for tag, _, _, _, _ in opcodes)
    delete_touch_indices: Set[int] = set()
    if not has_replace_or_insert:
        for tag, i1, i2, j1, j2 in opcodes:
            if tag == "delete":
                delete_touch_indices.add(max(0, min(j1, len(new_text) - 1)))

    for tag, i1, i2, j1, j2 in opcodes:
        if j1 >= j2:
            continue
        segment_text = new_text[j1:j2]
        base_rpr = get_rpr_at(i1)

        if tag in ("replace", "insert"):
            append_run(segment_text, base_rpr, is_highlighted=True)
        elif tag == "equal":
            # Check if this equal segment contains a pure-deletion touch point
            if delete_touch_indices and any( j1 <= d_idx < j2 for d_idx in delete_touch_indices ):
                append_run(segment_text, base_rpr, is_highlighted=True)
            else:
                # Preserve original rPr transitions across the equal range
                seg_start = 0
                curr_rpr = get_rpr_at(i1)
                for offset in range(1, j2 - j1):
                    next_rpr = get_rpr_at(i1 + offset)
                    if next_rpr is not curr_rpr:
                        append_run(segment_text[seg_start:offset], curr_rpr, is_highlighted=False)
                        seg_start = offset
                        curr_rpr = next_rpr
                append_run(segment_text[seg_start:], curr_rpr, is_highlighted=False)

    return highlighted_spans_count


def _clean_text_nodes_and_perturb(
    root: etree._Element,
    enable_perturb: bool = True,
    intensity: float = 0.7,
    highlight_changes: bool = True,
    preserve_punctuation: bool = True
) -> Tuple[int, int, int, int, Dict[str, Any], Dict[str, Any]]:
    """
    1. Strips invisible unicode characters and normalizes non-standard spaces across ALL <w:t> elements.
    2. Performs paragraph-level (<w:p>) semantic restructuring, transition word neutralization
       (首先/其次/最後/此外), perturbation, and proximity citation anchoring & hedging.
       STRICT CONSTRAINT: When preserve_punctuation=True, all existing punctuation marks are 100% preserved.
    3. Rebuilds modified paragraphs with mandatory yellow highlight (<w:highlight w:val="yellow"/>)
       ONLY on modified/inserted text spans, leaving unchanged punctuation and text intact.
    4. Runs Stage 1 and Stage 2 audits on the final document text.
    Returns (unicode_cleaned, semantic_replacements, semantic_reorganized, highlighted_changes, stage1_metrics, stage2_audit).
    """
    total_unicode_cleaned = 0
    total_replacements = 0
    total_reorganized = 0
    total_highlighted = 0

    # Pass 1: Clean Unicode and non-standard spaces on EVERY <w:t> in the document
    t_elem_unicode_touched: Set[etree._Element] = set()
    for t_elem in root.iter(f"{{{W_NS}}}t"):
        if t_elem.text:
            clean_res = clean_unicode(t_elem.text)
            if clean_res.has_anomalies:
                total_unicode_cleaned += clean_res.total_removed + clean_res.normalized_spaces
                t_elem.text = clean_res.cleaned_text
                t_elem_unicode_touched.add(t_elem)

    # Pass 2: Paragraph-level semantic restructuring + citation binding + yellow highlighting
    all_paragraphs = list(root.iter(f"{{{W_NS}}}p"))
    narrative_p_records = []
    in_references_section = False

    for p in all_paragraphs:
        p_raw_text = "".join(t.text for t in p.iter(f"{{{W_NS}}}t") if t.text)
        if PATTERNS_REF_HEADER.search("\n" + p_raw_text.strip() + "\n"):
            in_references_section = True

        if not in_references_section and _is_simple_narrative_paragraph(p):
            char_rpr_list: List[Optional[etree._Element]] = []
            orig_chars: List[str] = []
            had_unicode_touch = False
            for r in p.findall(f"{{{W_NS}}}r"):
                rpr = r.find(f"{{{W_NS}}}rPr")
                for t in r.findall(f"{{{W_NS}}}t"):
                    if t in t_elem_unicode_touched:
                        had_unicode_touch = True
                    if t.text:
                        orig_chars.append(t.text)
                        char_rpr_list.extend([rpr] * len(t.text))
            orig_p_text = "".join(orig_chars)
            if orig_p_text.strip():
                narrative_p_records.append({
                    "p": p,
                    "orig_text": orig_p_text,
                    "curr_text": orig_p_text,
                    "char_rpr_list": char_rpr_list,
                    "had_unicode_touch": had_unicode_touch,
                })
        else:
            # For complex paragraphs (e.g. containing hyperlinks/fields) outside tables/drawings,
            # process individual <w:t> nodes if enable_perturb is True
            if enable_perturb and not in_references_section and not _is_inside_table(p) and not _is_inside_drawing_or_shape(p):
                for r in p.iter(f"{{{W_NS}}}r"):
                    child_tags = [c.tag for c in r]
                    if any(tag not in (f"{{{W_NS}}}rPr", f"{{{W_NS}}}t") for tag in child_tags):
                        continue
                    t_elem = r.find(f"{{{W_NS}}}t")
                    if t_elem is not None and t_elem.text and len(t_elem.text.strip()) > 3:
                        orig_t = t_elem.text
                        s_res = restructure_semantics_and_burstiness(
                            orig_t,
                            target_cv=0.70,
                            enable_high_risk_residue_dissolve=True,
                            enable_entity_diversity=True,
                            preserve_punctuation=preserve_punctuation
                        )
                        new_t = s_res.cleaned_text
                        total_replacements += (
                            s_res.metrics.cliches_purged_count +
                            s_res.metrics.entity_diversity_replacements_count
                        )
                        total_reorganized += (
                            s_res.metrics.rules_of_three_disrupted +
                            s_res.metrics.short_punchy_sentences_created +
                            s_res.metrics.high_risk_residues_dissolved
                        )
                        p_res = perturb_text(
                            new_t,
                            intensity=intensity,
                            disrupt_transitions=True,
                            vary_punctuation=False,
                            preserve_punctuation=preserve_punctuation
                        )
                        new_t = p_res.perturbed_text
                        total_replacements += p_res.replacements_made
                        total_reorganized += p_res.sentences_reorganized

                        if new_t != orig_t or t_elem in t_elem_unicode_touched:
                            t_elem.text = new_t
                            if highlight_changes:
                                rpr = r.find(f"{{{W_NS}}}rPr")
                                new_rpr = _clone_rpr_with_yellow_highlight(rpr, enable_highlight=True)
                                if rpr is not None:
                                    r.remove(rpr)
                                r.insert(0, new_rpr)
                                r.set("data-nonai-highlighted", "1")
                                total_highlighted += 1

    # Process narrative paragraphs at full-paragraph and cross-paragraph granularity
    if narrative_p_records:
        if enable_perturb:
            # 2A. Cross-paragraph Citation Proximity Binding & Claim Hedging
            joined_narrative = "\n".join(rec["curr_text"] for rec in narrative_p_records)
            bound_narrative, bound_c, hedged_c = bind_citations_and_hedge(
                joined_narrative,
                auto_bind_proximate=True,
                hedge_isolated_claims=True
            )
            split_bound = bound_narrative.split("\n")
            if len(split_bound) == len(narrative_p_records):
                for rec, b_text in zip(narrative_p_records, split_bound):
                    rec["curr_text"] = b_text
                total_replacements += bound_c + hedged_c

            # 2B. Paragraph-level Semantic Restructure & Perturbation
            for rec in narrative_p_records:
                curr_t = rec["curr_text"]
                if len(curr_t.strip()) > 3:
                    s_res = restructure_semantics_and_burstiness(
                        curr_t,
                        target_cv=0.70,
                        enable_high_risk_residue_dissolve=True,
                        enable_entity_diversity=True,
                        preserve_punctuation=preserve_punctuation
                    )
                    curr_t = s_res.cleaned_text
                    total_replacements += (
                        s_res.metrics.cliches_purged_count +
                        s_res.metrics.entity_diversity_replacements_count
                    )
                    total_reorganized += (
                        s_res.metrics.rules_of_three_disrupted +
                        s_res.metrics.short_punchy_sentences_created +
                        s_res.metrics.high_risk_residues_dissolved
                    )

                    p_res = perturb_text(
                        curr_t,
                        intensity=intensity,
                        disrupt_transitions=True,
                        vary_punctuation=False,
                        preserve_punctuation=preserve_punctuation
                    )
                    curr_t = p_res.perturbed_text
                    total_replacements += p_res.replacements_made
                    total_reorganized += p_res.sentences_reorganized
                    rec["curr_text"] = curr_t

        # 2C. Rebuild paragraph runs and apply mandatory yellow highlight on all modified spans
        for rec in narrative_p_records:
            orig_t = rec["orig_text"]
            new_t = rec["curr_text"]
            had_uni = rec["had_unicode_touch"]
            if new_t != orig_t or had_uni:
                hl_added = _rebuild_paragraph_runs_with_diff_highlights(
                    rec["p"],
                    orig_t,
                    new_t,
                    rec["char_rpr_list"],
                    highlight_changes=highlight_changes,
                    force_highlight_if_equal=had_uni
                )
                total_highlighted += hl_added

    # Also highlight any protected/table <w:t> where invisible unicode or abnormal space was cleaned
    if highlight_changes:
        for t_elem in t_elem_unicode_touched:
            r_parent = t_elem.getparent()
            if r_parent is not None and r_parent.tag == f"{{{W_NS}}}r":
                if r_parent.get("data-nonai-highlighted") != "1":
                    rpr = r_parent.find(f"{{{W_NS}}}rPr")
                    new_rpr = _clone_rpr_with_yellow_highlight(rpr, enable_highlight=True)
                    if rpr is not None:
                        r_parent.remove(rpr)
                    r_parent.insert(0, new_rpr)
                    r_parent.set("data-nonai-highlighted", "1")
                    total_highlighted += 1

    # Collect final document text for Stage 1 & Stage 2 reporting
    final_para_texts = []
    for p in root.iter(f"{{{W_NS}}}p"):
        pt = "".join(t.text for t in p.iter(f"{{{W_NS}}}t") if t.text)
        if pt.strip():
            final_para_texts.append(pt)
    full_doc_text = "\n".join(final_para_texts)

    fact_audit = audit_fact_citations(full_doc_text)
    stage2_audit_dict = {
        "fact_integrity_score": fact_audit.fact_integrity_score,
        "summary_verdict": fact_audit.summary_verdict,
        "total_claims_detected": fact_audit.total_claims_detected,
        "unanchored_claims_count": fact_audit.unanchored_claims_count,
        "anchored_claims_count": fact_audit.anchored_claims_count,
        "unanchored_rate": fact_audit.unanchored_rate,
        "unanchored_claims": [
            {
                "sentence_index": c.sentence_index,
                "sentence_text": c.sentence_text,
                "claim_type": c.claim_type,
                "matched_clue": c.matched_clue,
                "risk_level": c.risk_level,
                "recommendation": c.recommendation,
                "suggested_citation": c.suggested_citation,
                "proximate_citation_found": c.proximate_citation_found
            } for c in fact_audit.unanchored_claims[:20]
        ],
        "total_references_detected": fact_audit.total_references_detected,
        "valid_references_count": fact_audit.valid_references_count,
        "suspicious_references_count": fact_audit.suspicious_references_count,
        "references": [
            {
                "entry_index": r.entry_index,
                "raw_text": r.raw_text,
                "doi": r.doi,
                "is_complete": r.is_complete,
                "hallucination_risk": r.hallucination_risk,
                "notes": r.notes
            } for r in fact_audit.references[:20]
        ]
    }

    stage1_metrics_res = restructure_semantics_and_burstiness(
        full_doc_text,
        target_cv=0.70,
        enable_cliche_purge=False,
        enable_burstiness_boost=False,
        enable_high_risk_residue_dissolve=False,
        enable_entity_diversity=False
    )
    stage1_metrics_dict = {
        "original_cv": stage1_metrics_res.metrics.original_cv,
        "reshaped_cv": stage1_metrics_res.metrics.reshaped_cv,
        "burstiness_boost_percent": stage1_metrics_res.metrics.burstiness_boost_percent,
        "cliches_purged_count": total_replacements,
        "short_punchy_sentences_created": total_reorganized,
        "high_risk_residues_dissolved": total_reorganized,
        "entity_diversity_replacements_count": total_replacements,
        "entity_diversity_details": [],
        "cliche_replacements": []
    }

    return (
        total_unicode_cleaned,
        total_replacements,
        total_reorganized,
        total_highlighted,
        stage1_metrics_dict,
        stage2_audit_dict,
    )


def _strip_ghost_shading_and_fonts(root: etree._Element) -> Tuple[int, List[str]]:
    """
    Remove inline shading (<w:shd>) caused by copying from ChatGPT/Claude
    and clean suspicious web fonts.
    Strictly preserves table cell shading (<w:tcPr>), Gantt charts, colored progress blocks,
    drawings/shapes, and <w:highlight w:val="yellow"/> revision highlights.
    """
    removed_count = 0
    items = []
    # 1. Remove background shading in runs and paragraphs outside tables and drawings
    for shd in list(root.iter(f"{{{W_NS}}}shd")):
        if _is_inside_table(shd) or _is_inside_drawing_or_shape(shd):
            continue

        parent = shd.getparent()
        if parent is None:
            continue

        if parent.tag not in (f"{{{W_NS}}}rPr", f"{{{W_NS}}}pPr"):
            continue

        fill = shd.get(f"{{{W_NS}}}fill", "").upper()
        if fill and fill not in ("AUTO", "NONE", "FFFFFF"):
            parent.remove(shd)
            removed_count += 1
            items.append(f'<w:shd w:fill="{fill}"/> (對話框背景 HEX 色碼)')

    # 2. Neutralize AI web fonts (Inter, Söhne, etc.), preserving fonts inside tables & drawings
    ai_fonts = {"INTER", "SÖHNE", "SOEHNE", "SYSTEM-UI", "ROBOTO"}
    for rFonts in list(root.iter(f"{{{W_NS}}}rFonts")):
        if _is_inside_table(rFonts) or _is_inside_drawing_or_shape(rFonts):
            continue

        for attr in [f"{{{W_NS}}}ascii", f"{{{W_NS}}}hAnsi", f"{{{W_NS}}}cs"]:
            val = rFonts.get(attr)
            if val and val.upper() in ai_fonts:
                rFonts.attrib.pop(attr, None)
                removed_count += 1
                items.append(f'<w:rFonts {attr}="{val}"/> (AI 網頁預設字體)')
    return removed_count, items


def _purge_all_rsid_attributes(root: etree._Element) -> None:
    """
    Exhaustively strips ALL pre-existing w:rsid* attributes and temporary nonai markers
    from every XML element in `root`, guaranteeing zero unregistered leftover RSIDs.
    """
    for elem in root.iter():
        to_del = [
            attr_name for attr_name in elem.attrib
            if "rsid" in attr_name.lower()
        ]
        for attr_name in to_del:
            elem.attrib.pop(attr_name, None)


def _fragment_and_inject_rsids(
    doc_root: etree._Element,
    rsid_pool: List[str]
) -> Tuple[int, int, int, List[Dict[str, str]]]:
    """
    1. Purges 100% of pre-existing w:rsid* attributes across `doc_root` so no unregistered RSIDs remain.
    2. Allocates RSIDs across paragraphs using character-weighted Temporal Session Clustering,
       guaranteeing that no single RSID ever dominates the document (>15% chars or paragraphs).
    3. Fragments long text runs into natural keystroke chunks and assigns realistic session + revision RSIDs.
    Returns (paragraphs_modified, runs_split, total_rsids_assigned, split_samples).
    """
    # Step 1: Total purge of any pre-existing RSID attributes in document.xml
    _purge_all_rsid_attributes(doc_root)

    p_count = 0
    runs_split_count = 0
    rsids_assigned = 0
    samples: List[Dict[str, str]] = []

    pause_punctuation = re.compile(r'([，。、；：！？,\.\?!;:])')

    all_paragraphs = list(doc_root.iter(f"{{{W_NS}}}p"))
    total_p = len(all_paragraphs)
    p_char_lengths = [len("".join(p.itertext())) for p in all_paragraphs]
    total_doc_chars = max(1, sum(p_char_lengths))

    pool_size = len(rsid_pool)
    # Maximum characters and paragraphs allowed in a single contiguous writing session block
    max_chars_per_block = max(80, total_doc_chars // max(8, pool_size))
    max_paras_per_block = max(1, total_p // max(8, pool_size))

    session_cursor = 0
    curr_block_chars = 0
    curr_block_paras = 0

    for idx, p in enumerate(all_paragraphs):
        p_count += 1
        p_chars = p_char_lengths[idx]

        # Advance session cursor when current writing block reaches character or paragraph cap
        if curr_block_paras >= max_paras_per_block or (curr_block_chars + p_chars > max_chars_per_block and curr_block_paras >= 1):
            session_cursor = (session_cursor + 1) % pool_size
            curr_block_chars = 0
            curr_block_paras = 0

        curr_block_chars += p_chars
        curr_block_paras += 1

        base_session_rsid = rsid_pool[session_cursor]
        p_prop_rsid = rsid_pool[(session_cursor + (idx % 3)) % pool_size]
        p_default_rsid = rsid_pool[(session_cursor + ((idx + 1) % 2)) % pool_size]

        p.set(f"{{{W_NS}}}rsidR", base_session_rsid)
        p.set(f"{{{W_NS}}}rsidRDefault", p_default_rsid)
        p.set(f"{{{W_NS}}}rsidP", p_prop_rsid)
        rsids_assigned += 3

        is_protected = _is_inside_table(p) or _is_inside_drawing_or_shape(p)

        # Step 2: Process and fragment child <w:r> elements (direct children for splitting)
        direct_runs = list(p.findall(f"{{{W_NS}}}r"))
        for r_pos, r in enumerate(direct_runs):
            is_highlighted_edit = (r.attrib.pop("data-nonai-highlighted", None) == "1")
            if is_highlighted_edit:
                # Modified runs receive a later revision session RSID
                r_rsid = rsid_pool[(session_cursor + pool_size // 2 + r_pos) % pool_size]
            else:
                r_rsid = rsid_pool[(session_cursor + (r_pos % 3)) % pool_size]

            r.set(f"{{{W_NS}}}rsidR", r_rsid)
            if is_highlighted_edit or (r_pos % 3 == 0):
                r.set(f"{{{W_NS}}}rsidRPr", rsid_pool[(session_cursor + r_pos + 1) % pool_size])
            rsids_assigned += 1

            if is_protected:
                continue

            child_tags = [c.tag for c in r]
            has_complex_elements = any(
                tag not in (f"{{{W_NS}}}rPr", f"{{{W_NS}}}t") for tag in child_tags
            )
            if has_complex_elements:
                continue

            # Fragment long text runs if they contain natural pause points
            t_elem = r.find(f"{{{W_NS}}}t")
            if t_elem is not None and t_elem.text and len(t_elem.text) > 32:
                original_sample_text = t_elem.text
                parts = pause_punctuation.split(t_elem.text)
                if len(parts) > 2:
                    chunks = []
                    cur = ""
                    for part in parts:
                        cur += part
                        if len(cur) >= 14:
                            chunks.append(cur)
                            cur = ""
                    if cur:
                        if chunks:
                            chunks[-1] += cur
                        else:
                            chunks.append(cur)

                    if len(chunks) > 1:
                        t_elem.text = chunks[0]
                        if chunks[0].startswith(" ") or chunks[0].endswith(" "):
                            t_elem.set(XML_SPACE, "preserve")
                        created_sub_rsids = [r_rsid]
                        r_idx = p.index(r)
                        for i, chunk in enumerate(chunks[1:], start=1):
                            new_r = etree.Element(f"{{{W_NS}}}r")
                            new_r_rsid = rsid_pool[(session_cursor + i) % pool_size]
                            created_sub_rsids.append(new_r_rsid)
                            new_r.set(f"{{{W_NS}}}rsidR", new_r_rsid)
                            if is_highlighted_edit:
                                new_r.set(f"{{{W_NS}}}rsidRPr", rsid_pool[(session_cursor + i + 1) % pool_size])
                            rPr = r.find(f"{{{W_NS}}}rPr")
                            if rPr is not None:
                                new_r.append(etree.fromstring(etree.tostring(rPr)))
                            new_t = etree.SubElement(new_r, f"{{{W_NS}}}t")
                            if chunk.startswith(" ") or chunk.endswith(" ") or "  " in chunk:
                                new_t.set(XML_SPACE, "preserve")
                            new_t.text = chunk
                            p.insert(r_idx + i, new_r)
                            runs_split_count += 1
                            rsids_assigned += 1

                        if len(samples) < 5:
                            samples.append({
                                "original": original_sample_text[:60] + "...",
                                "chunks": " │ ".join([f"[{rsid}] {c}" for rsid, c in zip(created_sub_rsids, chunks)])
                            })

        # Ensure any nested <w:r> (e.g. inside <w:hyperlink>) also gets a valid registered RSID
        for nested_r in p.iter(f"{{{W_NS}}}r"):
            nested_r.attrib.pop("data-nonai-highlighted", None)
            if f"{{{W_NS}}}rsidR" not in nested_r.attrib:
                nested_r.set(f"{{{W_NS}}}rsidR", base_session_rsid)
                rsids_assigned += 1

    # Step 3: Assign registered RSIDs to table rows (<w:tr>) and sections (<w:sectPr>)
    for tr_idx, tr in enumerate(doc_root.iter(f"{{{W_NS}}}tr")):
        tr_rsid = rsid_pool[tr_idx % pool_size]
        tr.set(f"{{{W_NS}}}rsidR", tr_rsid)
        tr.set(f"{{{W_NS}}}rsidTr", rsid_pool[(tr_idx + 1) % pool_size])
        rsids_assigned += 2

    for s_idx, sectPr in enumerate(doc_root.iter(f"{{{W_NS}}}sectPr")):
        sect_rsid = rsid_pool[s_idx % pool_size]
        sectPr.set(f"{{{W_NS}}}rsidR", sect_rsid)
        sectPr.set(f"{{{W_NS}}}rsidSect", rsid_pool[(s_idx + 1) % pool_size])
        rsids_assigned += 2

    return p_count, runs_split_count, rsids_assigned, samples


def _collect_all_used_rsids(root: etree._Element) -> Set[str]:
    """Collects every w:rsid* attribute value present anywhere in `root`."""
    used: Set[str] = set()
    for elem in root.iter():
        for attr_name, attr_val in elem.attrib.items():
            if "rsid" in attr_name.lower() and attr_val:
                used.add(attr_val.upper())
    return used


def _update_settings_xml(settings_xml_content: bytes, rsid_pool: List[str]) -> bytes:
    """Inject realistic Word settings and <w:rsids> table into word/settings.xml with ECMA-376 schema compliance."""
    if not settings_xml_content or not settings_xml_content.strip():
        try:
            root = etree.fromstring(DEFAULT_SETTINGS_XML)
        except Exception:
            root = etree.Element(f"{{{W_NS}}}settings", nsmap={"w": W_NS})
    else:
        try:
            root = etree.fromstring(settings_xml_content)
        except Exception:
            root = etree.fromstring(DEFAULT_SETTINGS_XML)

    # Find or create w:rsids without violating ECMA-376 sequence
    rsids_elem = root.find(f"{{{W_NS}}}rsids")
    if rsids_elem is None:
        compat_elem = root.find(f"{{{W_NS}}}compat")
        if compat_elem is not None:
            compat_idx = root.index(compat_elem)
            rsids_elem = etree.Element(f"{{{W_NS}}}rsids")
            root.insert(compat_idx + 1, rsids_elem)
        else:
            rsids_elem = etree.SubElement(root, f"{{{W_NS}}}rsids")
    else:
        rsids_elem.clear()

    # Root RSID
    root_rsid = etree.SubElement(rsids_elem, f"{{{W_NS}}}rsidRoot")
    root_rsid.set(f"{{{W_NS}}}val", rsid_pool[0])

    # All session RSIDs (sorted, uppercase, deduplicated)
    seen = set()
    for rsid in rsid_pool:
        val_up = rsid.upper()
        if val_up not in seen:
            seen.add(val_up)
            elem = etree.SubElement(rsids_elem, f"{{{W_NS}}}rsid")
            elem.set(f"{{{W_NS}}}val", val_up)

    return etree.tostring(root, xml_declaration=True, encoding="utf-8", standalone="yes")


def _update_app_xml(
    app_xml_content: Optional[bytes],
    total_words: int,
    total_characters: int,
    total_paragraphs: int,
    total_minutes: int,
    revision: int
) -> bytes:
    """Rewrite docProps/app.xml with complete genuine Microsoft Office Word properties."""
    root = etree.Element(f"{{{EP_NS}}}Properties", nsmap={"ep": EP_NS})

    pages = max(1, total_characters // 1500 + 1)
    lines = max(1, total_characters // 38 + 1)
    chars_with_spaces = max(1, int(total_characters * 1.15))

    props = [
        ("Template", "Normal.dotm"),
        ("TotalTime", str(total_minutes)),
        ("Pages", str(pages)),
        ("Words", str(max(1, total_words))),
        ("Characters", str(max(1, total_characters))),
        ("Application", "Microsoft Office Word"),
        ("DocSecurity", "0"),
        ("Lines", str(lines)),
        ("Paragraphs", str(max(1, total_paragraphs))),
        ("ScaleCrop", "false"),
        ("Company", ""),
        ("LinksUpToDate", "false"),
        ("CharactersWithSpaces", str(chars_with_spaces)),
        ("SharedDoc", "false"),
        ("HyperlinksChanged", "false"),
        ("AppVersion", "16.0000"),
    ]

    for tag, val in props:
        elem = etree.SubElement(root, f"{{{EP_NS}}}{tag}")
        elem.text = val

    return etree.tostring(root, xml_declaration=True, encoding="utf-8", standalone="yes")


def _update_core_xml(
    core_xml_content: Optional[bytes],
    author_name: str,
    revision: int,
    total_minutes: int
) -> Tuple[bytes, int]:
    """
    Rewrite docProps/core.xml:
    1. EXHAUSTIVELY PURGE <dc:description> (smoking gun for Claude Docs).
    2. Sanitize <dc:title>, <dc:subject>, <cp:keywords>, <cp:category>.
    3. Falsify human author name, coupled revision count, and editing timestamps.
    Returns (sanitized_bytes, claude_signatures_purged).
    """
    purged_count = 0
    if core_xml_content:
        try:
            root = etree.fromstring(core_xml_content)
        except Exception:
            root = etree.Element(f"{{{CP_NS}}}coreProperties", nsmap=NSMAP)
    else:
        root = etree.Element(f"{{{CP_NS}}}coreProperties", nsmap=NSMAP)

    now = datetime.now(timezone.utc)
    created_time = now - timedelta(minutes=total_minutes + random.randint(25, 120))
    modified_time = now - timedelta(minutes=random.randint(2, 12))

    # 1. PURGE <dc:description> completely!
    desc_elem = root.find(f"{{{DC_NS}}}description")
    if desc_elem is not None:
        if desc_elem.text and any(k in desc_elem.text.lower() for k in ["claude", "anthropic", "gpt", "node/"]):
            purged_count += 1
        root.remove(desc_elem)

    # 2. Clear or sanitize suspicious metadata fields
    for tag, ns in [("subject", DC_NS), ("keywords", CP_NS), ("category", CP_NS), ("contentStatus", CP_NS)]:
        elem = root.find(f"{{{ns}}}{tag}")
        if elem is not None:
            root.remove(elem)

    # 3. Sanitize title if needed
    title_elem = root.find(f"{{{DC_NS}}}title")
    if title_elem is not None and title_elem.text:
        cleaned_title = re.sub(r'(claude\s*docs?|anthropic|chatgpt|openai|node/[a-f0-9-]+)', '', title_elem.text, flags=re.IGNORECASE).strip()
        if cleaned_title != title_elem.text:
            purged_count += 1
            title_elem.text = cleaned_title

    def set_or_create_child(parent, ns, tag, val, attrs=None):
        elem = parent.find(f"{{{ns}}}{tag}")
        if elem is None:
            elem = etree.SubElement(parent, f"{{{ns}}}{tag}")
        elem.text = str(val)
        if attrs:
            for k, v in attrs.items():
                elem.set(k, v)

    set_or_create_child(root, DC_NS, "creator", author_name)
    set_or_create_child(root, CP_NS, "lastModifiedBy", author_name)
    set_or_create_child(root, CP_NS, "revision", str(revision))
    set_or_create_child(
        root, DCTERMS_NS, "created",
        created_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        {f"{{{XSI_NS}}}type": "dcterms:W3CDTF"}
    )
    set_or_create_child(
        root, DCTERMS_NS, "modified",
        modified_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        {f"{{{XSI_NS}}}type": "dcterms:W3CDTF"}
    )

    return etree.tostring(root, xml_declaration=True, encoding="utf-8", standalone="yes"), purged_count


def _ensure_content_types(content_types_bytes: bytes, added_parts: List[str]) -> bytes:
    """Register all package parts in [Content_Types].xml."""
    try:
        root = etree.fromstring(content_types_bytes)
    except Exception:
        root = etree.Element(f"{{{CT_NS}}}Types", nsmap={None: CT_NS})

    existing_overrides = {
        (elem.get("PartName") or "").strip().lower()
        for elem in root.findall(f"{{{CT_NS}}}Override")
    }

    part_type_map = {
        "/word/fontTable.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.fontTable+xml",
        "/word/webSettings.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.webSettings+xml",
        "/word/theme/theme1.xml": "application/vnd.openxmlformats-officedocument.theme+xml",
        "/word/settings.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml",
        "/word/styles.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml",
        "/word/document.xml": "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml",
        "/docProps/core.xml": "application/vnd.openxmlformats-package.core-properties+xml",
        "/docProps/app.xml": "application/vnd.openxmlformats-officedocument.extended-properties+xml",
    }

    for part_name, content_type in part_type_map.items():
        if part_name.lower() not in existing_overrides:
            override = etree.SubElement(root, f"{{{CT_NS}}}Override")
            override.set("PartName", part_name)
            override.set("ContentType", content_type)

    for elem in list(root.findall(f"{{{CT_NS}}}Override")):
        pname = elem.get("PartName", "").lower()
        if "customxml" in pname or "docprops/custom.xml" in pname:
            root.remove(elem)

    return etree.tostring(root, xml_declaration=True, encoding="utf-8", standalone="yes")


def _ensure_document_relationships(rels_bytes: bytes) -> bytes:
    """Ensure word/_rels/document.xml.rels links to fontTable, webSettings, theme, settings, and styles."""
    try:
        root = etree.fromstring(rels_bytes)
    except Exception:
        root = etree.Element(f"{{{PR_NS}}}Relationships", nsmap={None: PR_NS})

    existing_targets = set()
    existing_types = set()
    for elem in root.findall(f"{{{PR_NS}}}Relationship"):
        t = (elem.get("Target") or "").strip().lower()
        t = t.replace("\\", "/").lstrip("/")
        if t.startswith("word/"):
            t = t[5:]
        existing_targets.add(t)
        existing_types.add(elem.get("Type"))

    max_id = 0
    for elem in root.findall(f"{{{PR_NS}}}Relationship"):
        r_id = elem.get("Id", "")
        m = re.match(r"rId(\d+)", r_id)
        if m:
            max_id = max(max_id, int(m.group(1)))

    required_rels = [
        ("styles.xml", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles"),
        ("settings.xml", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings"),
        ("webSettings.xml", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/webSettings"),
        ("fontTable.xml", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/fontTable"),
        ("theme/theme1.xml", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme"),
    ]

    for target, rel_type in required_rels:
        norm_target = target.lower()
        if norm_target not in existing_targets and rel_type not in existing_types:
            max_id += 1
            rel_elem = etree.SubElement(root, f"{{{PR_NS}}}Relationship")
            rel_elem.set("Id", f"rId{max_id}")
            rel_elem.set("Type", rel_type)
            rel_elem.set("Target", target)

    return etree.tostring(root, xml_declaration=True, encoding="utf-8", standalone="yes")


def sanitize_docx(
    file_bytes: bytes,
    author_name: str = "Author",
    rsid_session_count: int = 25,
    simulate_typing_speed_wpm: int = 35,
    enable_perturb: bool = True,
    perturb_intensity: float = 0.7,
    highlight_changes: bool = True,
    preserve_punctuation: bool = True
) -> DocxSanitizeResult:
    """
    Sanitize a DOCX file:
    1. EXHAUSTIVELY PURGE all AI provenance metadata (<dc:description> Claude Docs tags, customXml).
    2. Synthesize missing Microsoft Word package files (fontTable.xml, webSettings.xml, theme1.xml).
    3. Falsify complete Microsoft Office Word 16.0000 extended & core properties with coupled revision count.
    4. Strip invisible unicode characters, fullwidth/non-standard spaces, and web CSS ghost shading.
    5. Perform paragraph-level semantic restructuring, transition word neutralization, and citation binding.
    6. Forcibly apply yellow fluorescent highlighter (<w:highlight w:val="yellow"/>) to all modified text spans.
    7. Purge all pre-existing RSIDs and inject character-balanced temporal RSID sessions with 100% settings.xml parity.
    """
    in_zip = zipfile.ZipFile(io.BytesIO(file_bytes), "r")
    out_buffer = io.BytesIO()
    out_zip = zipfile.ZipFile(out_buffer, "w", zipfile.ZIP_DEFLATED)

    xml_files = {name: in_zip.read(name) for name in in_zip.namelist()}

    # Audit initial RSID count
    original_rsids = set()
    if "word/document.xml" in xml_files:
        try:
            init_root = etree.fromstring(xml_files["word/document.xml"])
            original_rsids = _collect_all_used_rsids(init_root)
        except Exception:
            pass

    # 1. Purge customXml and custom.xml artifacts
    claude_purged_count = 0
    to_delete = []
    for fname in xml_files:
        if fname.lower().startswith("customxml/") or fname.lower() == "docprops/custom.xml":
            to_delete.append(fname)
            claude_purged_count += 1
    for fname in to_delete:
        del xml_files[fname]

    # Clean custom relationships from _rels/.rels
    if "_rels/.rels" in xml_files:
        try:
            r_root = etree.fromstring(xml_files["_rels/.rels"])
            for rel in list(r_root.findall(f"{{{PR_NS}}}Relationship")):
                t = rel.get("Target", "").lower()
                if "custom" in t:
                    r_root.remove(rel)
                    claude_purged_count += 1
            xml_files["_rels/.rels"] = etree.tostring(r_root, xml_declaration=True, encoding="utf-8", standalone="yes")
        except Exception:
            pass

    # 2. Synthesize missing genuine Microsoft Word package files
    missing_synthesized = []
    if "word/fontTable.xml" not in xml_files:
        xml_files["word/fontTable.xml"] = DEFAULT_FONTTABLE_XML
        missing_synthesized.append("word/fontTable.xml")

    if "word/webSettings.xml" not in xml_files:
        xml_files["word/webSettings.xml"] = DEFAULT_WEBSETTINGS_XML
        missing_synthesized.append("word/webSettings.xml")

    if "word/theme/theme1.xml" not in xml_files:
        xml_files["word/theme/theme1.xml"] = DEFAULT_THEME1_XML
        missing_synthesized.append("word/theme/theme1.xml")

    # 3. Process word/document.xml (Paragraph-Level Humanization, Yellow Highlighting & RSID Injection)
    unicode_removed = 0
    semantic_replacements = 0
    semantic_reorganized = 0
    highlighted_changes_count = 0
    ghost_styles_removed = 0
    ghost_style_items = []
    p_modified = 0
    runs_split = 0
    total_rsids_injected = 0
    split_samples = []
    total_words = 100
    total_characters = 500
    total_paragraphs = 1

    rsid_pool = _generate_rsid_pool(max(1, rsid_session_count))

    stage1_metrics = {}
    stage2_audit = {}

    if "word/document.xml" in xml_files:
        doc_root = etree.fromstring(xml_files["word/document.xml"])

        # 3A. Strip ghost shading & AI web fonts first (before applying yellow revision highlights)
        ghost_styles_removed, ghost_style_items = _strip_ghost_shading_and_fonts(doc_root)

        # 3B. Clean unicode, apply Stage 1 semantic restructure, Stage 2 citation binding, and Yellow Highlighting
        (
            unicode_removed,
            semantic_replacements,
            semantic_reorganized,
            highlighted_changes_count,
            stage1_metrics,
            stage2_audit,
        ) = _clean_text_nodes_and_perturb(
            doc_root,
            enable_perturb=enable_perturb,
            intensity=perturb_intensity,
            highlight_changes=highlight_changes,
            preserve_punctuation=preserve_punctuation,
        )

        # 3C. Exhaustively purge old RSIDs, fragment runs, and inject balanced session RSIDs
        p_modified, runs_split, total_rsids_injected, split_samples = _fragment_and_inject_rsids(doc_root, rsid_pool)

        # Verify 100% parity between document.xml RSIDs and rsid_pool
        used_in_doc = _collect_all_used_rsids(doc_root)
        for u_rsid in sorted(used_in_doc):
            if u_rsid not in rsid_pool:
                rsid_pool.append(u_rsid)

        # Calculate word and character metrics
        all_text = "".join(doc_root.itertext())
        total_characters = len(all_text)
        total_paragraphs = p_modified
        total_words = len(all_text.split()) if " " in all_text else len(all_text)

        xml_files["word/document.xml"] = etree.tostring(
            doc_root, xml_declaration=True, encoding="utf-8", standalone="yes"
        )

    # Also purge any unregistered w:rsid* attributes in auxiliary word/*.xml files (styles, headers, footers, footnotes)
    for part_name in list(xml_files.keys()):
        low_name = part_name.lower()
        if low_name.startswith("word/") and low_name.endswith(".xml") and low_name not in ("word/document.xml", "word/settings.xml"):
            try:
                aux_root = etree.fromstring(xml_files[part_name])
                _purge_all_rsid_attributes(aux_root)
                xml_files[part_name] = etree.tostring(aux_root, xml_declaration=True, encoding="utf-8", standalone="yes")
            except Exception:
                pass

    # 4. Process word/_rels/document.xml.rels
    rels_content = xml_files.get("word/_rels/document.xml.rels", b"")
    xml_files["word/_rels/document.xml.rels"] = _ensure_document_relationships(rels_content)

    # 5. Process [Content_Types].xml
    ct_content = xml_files.get("[Content_Types].xml", b"")
    xml_files["[Content_Types].xml"] = _ensure_content_types(ct_content, missing_synthesized)

    # 6. Calculate realistic human typing & editing time AND strictly coupled revision count
    # INVARIANT: revision_count (save count in docProps/core.xml) MUST be >= len(rsid_pool) (session count)
    calc_minutes = max(28, int(total_words / max(10, simulate_typing_speed_wpm)) + random.randint(25, 90))
    min_saves = len(rsid_pool) + 5
    revision_count = random.randint(min_saves, min_saves + max(12, len(rsid_pool) // 2))

    # 7. Process word/settings.xml (100% matched with rsid_pool)
    settings_content = xml_files.get("word/settings.xml", b"")
    xml_files["word/settings.xml"] = _update_settings_xml(settings_content, rsid_pool)

    # 8. Process docProps/app.xml
    app_content = xml_files.get("docProps/app.xml")
    xml_files["docProps/app.xml"] = _update_app_xml(
        app_content, total_words, total_characters, total_paragraphs, calc_minutes, revision_count
    )

    # 9. Process docProps/core.xml (Smoking Gun Purge + Coupled Save Count)
    core_content = xml_files.get("docProps/core.xml")
    sanitized_core, c_purged = _update_core_xml(
        core_content, author_name, revision_count, calc_minutes
    )
    xml_files["docProps/core.xml"] = sanitized_core
    claude_purged_count += c_purged

    # Write all sanitized files into the output zip
    for filename, content in xml_files.items():
        out_zip.writestr(filename, content)

    out_zip.close()
    in_zip.close()

    now = datetime.now(timezone.utc)
    created_time = now - timedelta(minutes=calc_minutes + 45)

    metadata_spoof_details = {
        "application": "Microsoft Office Word",
        "app_version": "16.0000",
        "template": "Normal.dotm",
        "total_time_minutes": calc_minutes,
        "revision": revision_count,
        "author": author_name,
        "created_time": created_time.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "modified_time": now.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "missing_parts_synthesized": missing_synthesized,
        "highlighted_changes": highlighted_changes_count,
    }

    return DocxSanitizeResult(
        cleaned_bytes=out_buffer.getvalue(),
        total_rsids_injected=total_rsids_injected,
        paragraphs_modified=p_modified,
        runs_split=runs_split,
        ghost_styles_removed=ghost_styles_removed,
        metadata_spoofed=True,
        unicode_chars_removed=unicode_removed,
        original_rsid_count=len(original_rsids),
        final_rsid_count=len(rsid_pool),
        estimated_human_minutes=calc_minutes,
        rsid_pool=rsid_pool,
        ghost_style_items=ghost_style_items,
        split_samples=split_samples,
        metadata_spoof_details=metadata_spoof_details,
        semantic_replacements=semantic_replacements,
        semantic_reorganized=semantic_reorganized,
        claude_signatures_purged=claude_purged_count,
        missing_parts_synthesized=missing_synthesized,
        stage1_restructure_metrics=stage1_metrics,
        stage2_fact_citation_audit=stage2_audit,
        highlighted_changes=highlighted_changes_count,
    )
