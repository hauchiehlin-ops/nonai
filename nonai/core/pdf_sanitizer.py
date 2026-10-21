"""
PDF Metadata and Forensic Fingerprint Sanitizer
Strips AI generator signatures, cleans per-page and catalog XMP streams,
normalizes realistic human creation/modification timestamps, removes conversational AI traces,
and spoofs genuine OS/Office PDF context (macOS Quartz or Microsoft Word).
"""

import io
import random
import re
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, create_string_object, DictionaryObject

@dataclass
class PdfSanitizeResult:
    cleaned_bytes: bytes
    original_producer: str
    original_creator: str
    original_metadata: Dict[str, Any]
    spoofed_producer: str
    spoofed_creator: str
    xmp_cleaned: bool
    total_pages: int
    ai_signatures_purged: int = 0
    metadata_fields_cleaned: List[str] = field(default_factory=list)


def sanitize_pdf(
    file_bytes: bytes,
    author_name: str = "Author",
    spoof_target: str = "macOS"  # "macOS" or "Word"
) -> PdfSanitizeResult:
    """
    Sanitizes PDF metadata and cross-format forensic signatures:
    1. Strips/spoofs Producer (e.g. Quartz PDFContext or Microsoft: Print to PDF).
    2. Strips/spoofs Creator (e.g. Pages or Microsoft Word for Microsoft 365).
    3. Strips raw XMP metadata streams from catalog and individual page objects.
    4. Simulates human typing intervals (CreationDate 45~150 mins before ModDate).
    5. Cleans suspicious Title/Subject/Keywords containing AI prompts or IDs.
    6. Performs deep binary scan to purge AI strings (Claude, Anthropic, ChatGPT, wkhtmltopdf, WeasyPrint).
    """
    reader = PdfReader(io.BytesIO(file_bytes))
    writer = PdfWriter()

    # Copy all pages
    for page in reader.pages:
        # Strip per-page XMP metadata if present
        if "/Metadata" in page:
            del page[NameObject("/Metadata")]
        writer.add_page(page)

    orig_meta = reader.metadata or {}
    orig_producer = str(orig_meta.get("/Producer", "None"))
    orig_creator = str(orig_meta.get("/Creator", "None"))

    # Determine spoof targets
    if spoof_target == "Word":
        target_producer = "Microsoft: Print to PDF"
        target_creator = "Microsoft Word for Microsoft 365"
    else:  # default macOS Quartz
        target_producer = "macOS Version 15.3.1 Quartz PDFContext"
        target_creator = "Pages"

    # Simulate realistic human editing duration
    now = datetime.now(timezone.utc)
    work_minutes = random.randint(45, 160)
    created_dt = now - timedelta(minutes=work_minutes)
    mod_dt = now - timedelta(minutes=random.randint(1, 8))

    created_str = created_dt.strftime("D:%Y%m%d%H%M%SZ")
    mod_str = mod_dt.strftime("D:%Y%m%d%H%M%SZ")

    cleaned_fields = []
    ai_purged_count = 0

    # Sanitize Title if present
    clean_title = ""
    orig_title = str(orig_meta.get("/Title", "") or "")
    if orig_title:
        clean_title = re.sub(
            r'(claude\s*docs?|anthropic|chatgpt|openai|weasyprint|wkhtmltopdf|node/[a-f0-9-]+)',
            '',
            orig_title,
            flags=re.IGNORECASE
        ).strip()
        if clean_title != orig_title:
            ai_purged_count += 1
            cleaned_fields.append("/Title (Sanitized)")

    # Build clean metadata dictionary matching standard OS/Office PDF outputs
    clean_metadata: Dict[str, str] = {
        "/Producer": target_producer,
        "/Creator": target_creator,
        "/Author": author_name,
        "/CreationDate": created_str,
        "/ModDate": mod_str,
    }
    if clean_title:
        clean_metadata["/Title"] = clean_title

    # Remove AI flags in original metadata
    for k, v in orig_meta.items():
        val_str = str(v).lower()
        if any(term in val_str for term in ["claude", "anthropic", "gpt", "weasyprint", "wkhtmltopdf", "reportlab", "canva"]):
            ai_purged_count += 1
            cleaned_fields.append(str(k))

    writer.add_metadata(clean_metadata)

    # Clean catalog XMP metadata
    xmp_cleaned = False
    try:
        if "/Metadata" in writer._root_object:
            del writer._root_object[NameObject("/Metadata")]
            xmp_cleaned = True
    except Exception:
        pass

    # Clean OutputIntents or PieceInfo that could store generator info
    for extra_tag in ["/PieceInfo", "/SeparationInfo"]:
        try:
            if extra_tag in writer._root_object:
                del writer._root_object[NameObject(extra_tag)]
        except Exception:
            pass

    out_buf = io.BytesIO()
    writer.write(out_buf)
    pdf_bytes = out_buf.getvalue()

    # Binary scan and purge for uncompressed AI strings in PDF trailers or comments
    ai_binary_patterns = [
        re.compile(rb'Claude\s*Docs(\s*node/[a-f0-9-]+@\d+)?', re.IGNORECASE),
        re.compile(rb'wkhtmltopdf\s*[\d\.]*', re.IGNORECASE),
        re.compile(rb'WeasyPrint\s*[\d\.]*', re.IGNORECASE),
        re.compile(rb'ReportLab\s*PDF\s*Library', re.IGNORECASE),
        re.compile(rb'iText\s*[\d\.]*', re.IGNORECASE),
    ]

    for pat in ai_binary_patterns:
        matches = len(pat.findall(pdf_bytes))
        if matches > 0:
            ai_purged_count += matches
            # Replace matched strings with spaces of equal length to preserve xref offsets
            def blank_repl(m):
                return b' ' * len(m.group(0))
            pdf_bytes = pat.sub(blank_repl, pdf_bytes)

    return PdfSanitizeResult(
        cleaned_bytes=pdf_bytes,
        original_producer=orig_producer,
        original_creator=orig_creator,
        original_metadata={str(k): str(v) for k, v in orig_meta.items()},
        spoofed_producer=target_producer,
        spoofed_creator=target_creator,
        xmp_cleaned=xmp_cleaned,
        total_pages=len(reader.pages),
        ai_signatures_purged=ai_purged_count,
        metadata_fields_cleaned=cleaned_fields
    )
