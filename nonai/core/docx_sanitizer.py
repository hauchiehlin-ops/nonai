"""
DOCX Sanitizer and RSID Biomimetic Injector
Cleans web CSS/HTML artifacts, spoofes complete Microsoft Office Word package metadata,
purges all AI provenance tags (e.g. Claude Docs, Anthropic), synthesizes mandatory Word files
(fontTable.xml, webSettings.xml, theme1.xml), and applies deep semantic humanization.
"""

import io
import os
import random
import re
import zipfile
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from lxml import etree

from nonai.core.unicode_cleaner import clean_unicode
from nonai.core.semantic_perturb import perturb_text, PerturbResult
from nonai.core.semantic_restructure import restructure_semantics_and_burstiness, RestructureResult
from nonai.core.fact_citation_auditor import audit_fact_citations, FactCitationAuditResult

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

NSMAP = {
    "w": W_NS,
    "cp": CP_NS,
    "dc": DC_NS,
    "dcterms": DCTERMS_NS,
    "ep": EP_NS,
    "xsi": XSI_NS,
}

# Standard XML content for Microsoft Office Word package files
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


def _generate_rsid_pool(count: int = 30) -> List[str]:
    """Generate a pool of realistic 8-digit hexadecimal RSID strings."""
    pool = set()
    while len(pool) < count:
        val = random.randint(0x00010000, 0x00FFFFFF)
        pool.add(f"{val:08X}")
    return sorted(list(pool))


def _clean_text_nodes_and_perturb(
    root: etree._Element,
    enable_perturb: bool = True,
    intensity: float = 0.7
) -> Tuple[int, int, int, Dict[str, Any], Dict[str, Any]]:
    """
    Find all <w:t> elements:
    1. Strip invisible unicode characters.
    2. If enable_perturb, apply deep semantic restructuring, AI cliché purging, and burstiness reshaping.
    3. Run Stage 2 fact and citation audit across the complete document text.
    Returns (unicode_cleaned, semantic_replacements, semantic_reorganized, stage1_metrics, stage2_audit).
    """
    total_unicode_cleaned = 0
    total_replacements = 0
    total_reorganized = 0
    all_texts = []

    for t_elem in root.iter(f"{{{W_NS}}}t"):
        if t_elem.text:
            # 1. Clean Unicode
            clean_res = clean_unicode(t_elem.text)
            curr_text = clean_res.cleaned_text
            total_unicode_cleaned += clean_res.total_removed

            # 2. Stage 1: Semantic restructure & burstiness
            if enable_perturb and len(curr_text.strip()) > 3:
                # First run semantic restructurer (cliché purge + entity diversity + high-risk residue dissolve + burstiness)
                s_res = restructure_semantics_and_burstiness(
                    curr_text,
                    target_cv=0.70,
                    enable_high_risk_residue_dissolve=True,
                    enable_entity_diversity=True
                )
                curr_text = s_res.cleaned_text
                total_replacements += s_res.metrics.cliches_purged_count + s_res.metrics.entity_diversity_replacements_count
                total_reorganized += (
                    s_res.metrics.rules_of_three_disrupted +
                    s_res.metrics.short_punchy_sentences_created +
                    s_res.metrics.high_risk_residues_dissolved
                )

                # Next run fine-grained perturbations
                p_res = perturb_text(
                    curr_text,
                    intensity=intensity,
                    disrupt_transitions=True,
                    vary_punctuation=True
                )
                curr_text = p_res.perturbed_text
                total_replacements += p_res.replacements_made
                total_reorganized += p_res.sentences_reorganized

            t_elem.text = curr_text
            all_texts.append(curr_text)

    # 3. Stage 2: Audit Fact & Citation Anchoring on full document text
    full_doc_text = "\n".join(all_texts)
    fact_audit = audit_fact_citations(full_doc_text)

    # Convert audit to serializable dict
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
            } for c in fact_audit.unanchored_claims[:20]  # top 20
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

    # Evaluate full document burstiness for Stage 1 metrics
    stage1_metrics_res = restructure_semantics_and_burstiness(
        full_doc_text,
        target_cv=0.70,
        enable_high_risk_residue_dissolve=True,
        enable_entity_diversity=True
    )
    stage1_metrics_dict = {
        "original_cv": stage1_metrics_res.metrics.original_cv,
        "reshaped_cv": stage1_metrics_res.metrics.reshaped_cv,
        "burstiness_boost_percent": stage1_metrics_res.metrics.burstiness_boost_percent,
        "cliches_purged_count": total_replacements,
        "short_punchy_sentences_created": total_reorganized,
        "high_risk_residues_dissolved": stage1_metrics_res.metrics.high_risk_residues_dissolved,
        "entity_diversity_replacements_count": stage1_metrics_res.metrics.entity_diversity_replacements_count,
        "entity_diversity_details": stage1_metrics_res.metrics.entity_diversity_details[:15],
        "cliche_replacements": stage1_metrics_res.metrics.cliche_replacements[:15]
    }

    return total_unicode_cleaned, total_replacements, total_reorganized, stage1_metrics_dict, stage2_audit_dict


def _strip_ghost_shading_and_fonts(root: etree._Element) -> Tuple[int, List[str]]:
    """
    Remove inline shading (<w:shd>) caused by copying from ChatGPT/Claude
    and clean suspicious web fonts.
    """
    removed_count = 0
    items = []
    # 1. Remove background shading in runs and paragraphs
    for shd in list(root.iter(f"{{{W_NS}}}shd")):
        fill = shd.get(f"{{{W_NS}}}fill", "").upper()
        if fill and fill not in ("AUTO", "NONE", "FFFFFF"):
            parent = shd.getparent()
            if parent is not None:
                parent.remove(shd)
                removed_count += 1
                items.append(f'<w:shd w:fill="{fill}"/> (對話框背景 HEX 色碼)')

    # 2. Neutralize AI web fonts (Inter, Söhne, etc.)
    ai_fonts = {"INTER", "SÖHNE", "SOEHNE", "SYSTEM-UI", "ROBOTO", "SEGOE UI"}
    for rFonts in list(root.iter(f"{{{W_NS}}}rFonts")):
        for attr in [f"{{{W_NS}}}ascii", f"{{{W_NS}}}hAnsi", f"{{{W_NS}}}cs"]:
            val = rFonts.get(attr)
            if val and val.upper() in ai_fonts:
                rFonts.attrib.pop(attr, None)
                removed_count += 1
                items.append(f'<w:rFonts {attr}="{val}"/> (AI 網頁預設字體)')
    return removed_count, items


def _fragment_and_inject_rsids(
    doc_root: etree._Element,
    rsid_pool: List[str]
) -> Tuple[int, int, int, List[Dict[str, str]]]:
    """
    Fragments robotic long runs into natural chunks and injects RSID tags.
    Returns (paragraphs_modified, runs_split, total_rsids_assigned, split_samples).
    """
    p_count = 0
    runs_split_count = 0
    rsids_assigned = 0
    samples: List[Dict[str, str]] = []

    pause_punctuation = re.compile(r'([，。、；：！？,\.\?!;:])')

    for p in doc_root.iter(f"{{{W_NS}}}p"):
        p_count += 1
        p_rsid = random.choice(rsid_pool)
        p.set(f"{{{W_NS}}}rsidR", p_rsid)
        p.set(f"{{{W_NS}}}rsidRDefault", p_rsid)
        if random.random() < 0.4:
            p.set(f"{{{W_NS}}}rsidP", random.choice(rsid_pool))
        rsids_assigned += 1

        # Process child runs
        runs = list(p.findall(f"{{{W_NS}}}r"))
        for r in runs:
            r_rsid = random.choice(rsid_pool)
            r.set(f"{{{W_NS}}}rsidR", r_rsid)
            if random.random() < 0.25:
                r.set(f"{{{W_NS}}}rsidRPr", random.choice(rsid_pool))
            rsids_assigned += 1

            # Fragment long text runs if they contain natural pause points
            t_elem = r.find(f"{{{W_NS}}}t")
            if t_elem is not None and t_elem.text and len(t_elem.text) > 35:
                original_sample_text = t_elem.text
                parts = pause_punctuation.split(t_elem.text)
                if len(parts) > 2:
                    chunks = []
                    cur = ""
                    for part in parts:
                        cur += part
                        if len(cur) >= 15:
                            chunks.append(cur)
                            cur = ""
                    if cur:
                        if chunks:
                            chunks[-1] += cur
                        else:
                            chunks.append(cur)

                    if len(chunks) > 1:
                        t_elem.text = chunks[0]
                        created_sub_rsids = [r_rsid]
                        r_idx = p.index(r)
                        for i, chunk in enumerate(chunks[1:], start=1):
                            new_r = etree.Element(f"{{{W_NS}}}r")
                            new_r_rsid = random.choice(rsid_pool)
                            created_sub_rsids.append(new_r_rsid)
                            new_r.set(f"{{{W_NS}}}rsidR", new_r_rsid)
                            rPr = r.find(f"{{{W_NS}}}rPr")
                            if rPr is not None:
                                new_r.append(etree.fromstring(etree.tostring(rPr)))
                            new_t = etree.SubElement(new_r, f"{{{W_NS}}}t")
                            if chunk.startswith(" ") or chunk.endswith(" "):
                                new_t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
                            new_t.text = chunk
                            p.insert(r_idx + i, new_r)
                            runs_split_count += 1
                            rsids_assigned += 1

                        if len(samples) < 5:
                            samples.append({
                                "original": original_sample_text[:60] + "...",
                                "chunks": " │ ".join([f"[{rsid}] {c}" for rsid, c in zip(created_sub_rsids, chunks)])
                            })

    return p_count, runs_split_count, rsids_assigned, samples


def _update_settings_xml(settings_xml_content: bytes, rsid_pool: List[str]) -> bytes:
    """Inject realistic Word settings and <w:rsids> table into word/settings.xml."""
    try:
        root = etree.fromstring(settings_xml_content)
    except Exception:
        root = etree.Element(f"{{{W_NS}}}settings", nsmap={"w": W_NS})

    # Standard Word settings
    def ensure_setting(tag: str, attrs: Dict[str, str]):
        elem = root.find(f"{{{W_NS}}}{tag}")
        if elem is None:
            elem = etree.SubElement(root, f"{{{W_NS}}}{tag}")
        for k, v in attrs.items():
            elem.set(f"{{{W_NS}}}{k}", v)

    ensure_setting("defaultTabStop", {"val": "720"})
    ensure_setting("characterSpacingControl", {"val": "doNotCompress"})

    compat = root.find(f"{{{W_NS}}}compat")
    if compat is None:
        compat = etree.SubElement(root, f"{{{W_NS}}}compat")
        etree.SubElement(compat, f"{{{W_NS}}}compatSetting", {
            f"{{{W_NS}}}name": "compatibilityMode",
            f"{{{W_NS}}}uri": "http://schemas.microsoft.com/office/word",
            f"{{{W_NS}}}val": "15"
        })

    # Find or create w:rsids
    rsids_elem = root.find(f"{{{W_NS}}}rsids")
    if rsids_elem is None:
        rsids_elem = etree.SubElement(root, f"{{{W_NS}}}rsids")
    else:
        rsids_elem.clear()

    # Root RSID
    root_rsid = etree.SubElement(rsids_elem, f"{{{W_NS}}}rsidRoot")
    root_rsid.set(f"{{{W_NS}}}val", rsid_pool[0])

    # All session RSIDs
    for rsid in rsid_pool:
        elem = etree.SubElement(rsids_elem, f"{{{W_NS}}}rsid")
        elem.set(f"{{{W_NS}}}val", rsid)

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
    3. Falsify human author name and editing timestamps.
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

    existing_overrides = {elem.get("PartName") for elem in root.findall(f"{{{CT_NS}}}Override")}

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

    # Ensure required overrides
    for part_name, content_type in part_type_map.items():
        if part_name not in existing_overrides:
            override = etree.SubElement(root, f"{{{CT_NS}}}Override")
            override.set("PartName", part_name)
            override.set("ContentType", content_type)

    # Remove deleted customXml or custom.xml overrides
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

    existing_targets = {elem.get("Target") for elem in root.findall(f"{{{PR_NS}}}Relationship")}
    
    # Find maximum existing rId index
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
        if target not in existing_targets:
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
    perturb_intensity: float = 0.7
) -> DocxSanitizeResult:
    """
    Sanitize a DOCX file:
    1. EXHAUSTIVELY PURGE all AI provenance metadata (<dc:description> Claude Docs tags, customXml).
    2. Synthesize missing Microsoft Word package files (fontTable.xml, webSettings.xml, theme1.xml).
    3. Falsify complete Microsoft Office Word 16.0000 extended & core properties.
    4. Strip invisible unicode characters and web CSS ghost shading.
    5. Perform deep semantic perturbation & academic de-patterning to defeat transformer classifiers.
    6. Inject realistic human RSID revision history and keystroke run fragmentation.
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
            for elem in init_root.iter():
                for attr_name, attr_val in elem.attrib.items():
                    if "rsid" in attr_name.lower():
                        original_rsids.add(attr_val)
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

    # 3. Process word/document.xml (Text Humanization & RSID Injection)
    unicode_removed = 0
    semantic_replacements = 0
    semantic_reorganized = 0
    ghost_styles_removed = 0
    ghost_style_items = []
    p_modified = 0
    runs_split = 0
    total_rsids_injected = 0
    split_samples = []
    total_words = 100
    total_characters = 500
    total_paragraphs = 1

    rsid_pool = _generate_rsid_pool(rsid_session_count)

    stage1_metrics = {}
    stage2_audit = {}

    if "word/document.xml" in xml_files:
        doc_root = etree.fromstring(xml_files["word/document.xml"])

        # 3A. Clean unicode, apply Stage 1 semantic restructure & Stage 2 fact-citation audit
        unicode_removed, semantic_replacements, semantic_reorganized, stage1_metrics, stage2_audit = _clean_text_nodes_and_perturb(
            doc_root,
            enable_perturb=enable_perturb,
            intensity=perturb_intensity
        )

        # 3B. Strip shading & ghost styles
        ghost_styles_removed, ghost_style_items = _strip_ghost_shading_and_fonts(doc_root)

        # 3C. Fragment runs and inject RSIDs
        p_modified, runs_split, total_rsids_injected, split_samples = _fragment_and_inject_rsids(doc_root, rsid_pool)

        # Calculate word and character metrics
        all_text = "".join(doc_root.itertext())
        total_characters = len(all_text)
        total_paragraphs = p_modified
        total_words = len(all_text.split()) if " " in all_text else len(all_text)

        xml_files["word/document.xml"] = etree.tostring(
            doc_root, xml_declaration=True, encoding="utf-8", standalone="yes"
        )

    # 4. Process word/_rels/document.xml.rels
    rels_content = xml_files.get("word/_rels/document.xml.rels", b"")
    xml_files["word/_rels/document.xml.rels"] = _ensure_document_relationships(rels_content)

    # 5. Process [Content_Types].xml
    ct_content = xml_files.get("[Content_Types].xml", b"")
    xml_files["[Content_Types].xml"] = _ensure_content_types(ct_content, missing_synthesized)

    # Calculate realistic human typing & editing time
    calc_minutes = max(28, int(total_words / max(10, simulate_typing_speed_wpm)) + random.randint(25, 90))
    revision_count = random.randint(14, 38)

    # 6. Process word/settings.xml
    settings_content = xml_files.get("word/settings.xml", b"")
    xml_files["word/settings.xml"] = _update_settings_xml(settings_content, rsid_pool)

    # 7. Process docProps/app.xml
    app_content = xml_files.get("docProps/app.xml")
    xml_files["docProps/app.xml"] = _update_app_xml(
        app_content, total_words, total_characters, total_paragraphs, calc_minutes, revision_count
    )

    # 8. Process docProps/core.xml (Smoking Gun Purge)
    core_content = xml_files.get("docProps/core.xml")
    sanitized_core, c_purged = _update_core_xml(
        core_content, author_name, revision_count, calc_minutes
    )
    xml_files["docProps/core.xml"] = sanitized_core
    claude_purged_count += c_purged

    # 9. Global AI String Purge across all text/XML parts
    ai_patterns = [
        re.compile(rb'Claude\s*Docs(\s*node/[a-f0-9-]+@\d+\s*docx-w\d+)?', re.IGNORECASE),
        re.compile(rb'Claude', re.IGNORECASE),
        re.compile(rb'Anthropic', re.IGNORECASE),
        re.compile(rb'python-docx', re.IGNORECASE),
        re.compile(rb'docx-w\d+', re.IGNORECASE),
    ]

    for fname, content in list(xml_files.items()):
        if fname.endswith(".xml") or fname.endswith(".rels"):
            original_len = len(content)
            for pat in ai_patterns:
                content = pat.sub(b'', content)
            if len(content) != original_len:
                claude_purged_count += 1
                xml_files[fname] = content

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
        "missing_parts_synthesized": missing_synthesized
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
        stage2_fact_citation_audit=stage2_audit
    )
