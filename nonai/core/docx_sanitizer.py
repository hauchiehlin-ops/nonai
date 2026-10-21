"""
DOCX Sanitizer and RSID Biomimetic Injector
Cleans web CSS/HTML artifacts, spoofes metadata, and injects realistic RSID editing histories.
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

# OpenXML Namespaces
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
CP_NS = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC_NS = "http://purl.org/dc/elements/1.1/"
DCTERMS_NS = "http://purl.org/dc/terms/"
EP_NS = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"

NSMAP = {
    "w": W_NS,
    "cp": CP_NS,
    "dc": DC_NS,
    "dcterms": DCTERMS_NS,
    "ep": EP_NS,
    "xsi": XSI_NS,
}

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


def _generate_rsid_pool(count: int = 30) -> List[str]:
    """Generate a pool of realistic 8-digit hexadecimal RSID strings."""
    pool = set()
    while len(pool) < count:
        # RSIDs are 4-byte hex numbers, e.g. "003A12B4"
        val = random.randint(0x00010000, 0x00FFFFFF)
        pool.add(f"{val:08X}")
    return sorted(list(pool))


def _clean_text_nodes(root: etree._Element) -> int:
    """Find all <w:t> elements and strip invisible unicode characters."""
    total_cleaned = 0
    for t_elem in root.iter(f"{{{W_NS}}}t"):
        if t_elem.text:
            clean_res = clean_unicode(t_elem.text)
            if clean_res.total_removed > 0 or clean_res.normalized_spaces > 0:
                t_elem.text = clean_res.cleaned_text
                total_cleaned += clean_res.total_removed
    return total_cleaned


def _strip_ghost_shading_and_fonts(root: etree._Element) -> int:
    """
    Remove inline shading (<w:shd>) caused by copying from ChatGPT/Claude
    and clean suspicious web fonts.
    """
    removed_count = 0
    # 1. Remove background shading in runs and paragraphs
    for shd in list(root.iter(f"{{{W_NS}}}shd")):
        fill = shd.get(f"{{{W_NS}}}fill", "").upper()
        # Web dark/light chat bubbles usually have specific hex fills like F7F7F8, F9F9F9, 2F2F2F
        if fill and fill not in ("AUTO", "NONE", "FFFFFF"):
            parent = shd.getparent()
            if parent is not None:
                parent.remove(shd)
                removed_count += 1

    # 2. Neutralize AI web fonts (Inter, Söhne, etc.)
    ai_fonts = {"INTER", "SÖHNE", "SOEHNE", "SYSTEM-UI", "ROBOTO", "SEGOE UI"}
    for rFonts in list(root.iter(f"{{{W_NS}}}rFonts")):
        for attr in [f"{{{W_NS}}}ascii", f"{{{W_NS}}}hAnsi", f"{{{W_NS}}}cs"]:
            val = rFonts.get(attr)
            if val and val.upper() in ai_fonts:
                rFonts.attrib.pop(attr, None)
                removed_count += 1
    return removed_count


def _fragment_and_inject_rsids(
    doc_root: etree._Element,
    rsid_pool: List[str]
) -> Tuple[int, int, int]:
    """
    Fragments robotic long runs into natural chunks and injects RSID tags.
    Returns (paragraphs_modified, runs_split, total_rsids_assigned).
    """
    root_rsid = rsid_pool[0]
    p_count = 0
    runs_split_count = 0
    rsids_assigned = 0

    # Punctuation marks used for natural typing pauses
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
                # Check for punctuation to split
                parts = pause_punctuation.split(t_elem.text)
                if len(parts) > 2:
                    # Regroup into 2 or 3 chunks
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
                        # Keep first chunk in current run
                        t_elem.text = chunks[0]
                        # Create subsequent runs
                        r_idx = p.index(r)
                        for i, chunk in enumerate(chunks[1:], start=1):
                            new_r = etree.Element(f"{{{W_NS}}}r")
                            new_r_rsid = random.choice(rsid_pool)
                            new_r.set(f"{{{W_NS}}}rsidR", new_r_rsid)
                            # Copy formatting if present
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

    return p_count, runs_split_count, rsids_assigned


def _update_settings_xml(settings_xml_content: bytes, rsid_pool: List[str]) -> bytes:
    """Inject <w:rsids> table into word/settings.xml."""
    try:
        root = etree.fromstring(settings_xml_content)
    except Exception:
        root = etree.Element(f"{{{W_NS}}}settings", nsmap={"w": W_NS})

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
    total_minutes: int,
    revision: int
) -> bytes:
    """Rewrite docProps/app.xml to look like genuine Microsoft Office Word."""
    if app_xml_content:
        try:
            root = etree.fromstring(app_xml_content)
        except Exception:
            root = etree.Element(f"{{{EP_NS}}}Properties", nsmap={"ep": EP_NS})
    else:
        root = etree.Element(f"{{{EP_NS}}}Properties", nsmap={"ep": EP_NS})

    def set_or_create(tag: str, val: str):
        elem = root.find(f"{{{EP_NS}}}{tag}")
        if elem is None:
            elem = etree.SubElement(root, f"{{{EP_NS}}}{tag}")
        elem.text = str(val)

    set_or_create("Application", "Microsoft Office Word")
    set_or_create("AppVersion", "16.0000")
    set_or_create("TotalTime", str(total_minutes))
    set_or_create("Words", str(max(1, total_words)))
    set_or_create("DocSecurity", "0")

    return etree.tostring(root, xml_declaration=True, encoding="utf-8", standalone="yes")


def _update_core_xml(
    core_xml_content: Optional[bytes],
    author_name: str,
    revision: int,
    total_minutes: int
) -> bytes:
    """Rewrite docProps/core.xml with human editing timestamps and author name."""
    if core_xml_content:
        try:
            root = etree.fromstring(core_xml_content)
        except Exception:
            root = etree.Element(f"{{{CP_NS}}}coreProperties", nsmap=NSMAP)
    else:
        root = etree.Element(f"{{{CP_NS}}}coreProperties", nsmap=NSMAP)

    now = datetime.now(timezone.utc)
    created_time = now - timedelta(minutes=total_minutes + random.randint(15, 60))
    modified_time = now - timedelta(minutes=random.randint(2, 10))

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

    return etree.tostring(root, xml_declaration=True, encoding="utf-8", standalone="yes")


def sanitize_docx(
    file_bytes: bytes,
    author_name: str = "Author",
    rsid_session_count: int = 25,
    simulate_typing_speed_wpm: int = 35
) -> DocxSanitizeResult:
    """
    Sanitize a DOCX file:
    1. Strip invisible unicode from all text nodes.
    2. Remove web CSS/HTML shading artifacts and AI font tags.
    3. Generate and inject human-like RSID session history into settings.xml & document.xml.
    4. Fragment runs to simulate human keystrokes & pauses.
    5. Falsify app.xml and core.xml metadata to match Microsoft Office Word.
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

    # Process word/document.xml
    unicode_removed = 0
    ghost_styles_removed = 0
    p_modified = 0
    runs_split = 0
    total_rsids_injected = 0
    total_words = 100

    rsid_pool = _generate_rsid_pool(rsid_session_count)

    if "word/document.xml" in xml_files:
        doc_root = etree.fromstring(xml_files["word/document.xml"])
        # 1. Clean unicode
        unicode_removed = _clean_text_nodes(doc_root)
        # 2. Strip shading & ghost styles
        ghost_styles_removed = _strip_ghost_shading_and_fonts(doc_root)
        # 3. Fragment and inject RSIDs
        p_modified, runs_split, total_rsids_injected = _fragment_and_inject_rsids(doc_root, rsid_pool)
        
        # Approximate word count
        all_text = "".join(doc_root.itertext())
        total_words = len(all_text.split()) if " " in all_text else len(all_text)

        xml_files["word/document.xml"] = etree.tostring(
            doc_root, xml_declaration=True, encoding="utf-8", standalone="yes"
        )

    # Calculate human editing time (words / wpm + random thinking pauses)
    calc_minutes = max(18, int(total_words / max(10, simulate_typing_speed_wpm)) + random.randint(15, 60))
    revision_count = random.randint(8, 28)

    # Process word/settings.xml
    settings_content = xml_files.get("word/settings.xml", b"")
    xml_files["word/settings.xml"] = _update_settings_xml(settings_content, rsid_pool)

    # Process docProps/app.xml
    app_content = xml_files.get("docProps/app.xml")
    xml_files["docProps/app.xml"] = _update_app_xml(
        app_content, total_words, calc_minutes, revision_count
    )

    # Process docProps/core.xml
    core_content = xml_files.get("docProps/core.xml")
    xml_files["docProps/core.xml"] = _update_core_xml(
        core_content, author_name, revision_count, calc_minutes
    )

    # Write all files back to out_zip
    for filename, content in xml_files.items():
        out_zip.writestr(filename, content)

    out_zip.close()
    in_zip.close()

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
        estimated_human_minutes=calc_minutes
    )
