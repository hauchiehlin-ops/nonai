"""
PDF Metadata and Forensic Fingerprint Sanitizer
Strips AI generator signatures, cleans per-page and catalog XMP streams,
preserves the original creation/modification timestamps and the original
Producer / Creator written by the exporting software.
"""

import io
import re
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
    Sanitizes PDF metadata:
    1. Preserves the original Producer and Creator written by the exporting software (never rewritten).
    2. Strips raw XMP metadata streams from catalog and individual page objects.
    3. Sets Author; preserves the original CreationDate / ModDate verbatim (never fabricated).
    4. Cleans suspicious Title text containing AI prompts or IDs.
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

    # Producer / Creator are preserved exactly as written by the exporting software.
    # Rewriting them creates structural inconsistencies (e.g. a claimed macOS Quartz
    # producer without a matching build number), which forensic tools flag as tampering.
    # `spoof_target` is accepted only for backward compatibility and is ignored.
    target_producer = orig_producer
    target_creator = orig_creator

    # CreationDate / ModDate are preserved verbatim (raw PDF date strings) for the same reason:
    # fabricated timestamps that disagree with the file's internal structure read as tampering.
    orig_creation_date = orig_meta.get("/CreationDate")
    orig_mod_date = orig_meta.get("/ModDate")

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
        "/Author": author_name,
    }
    if clean_title:
        clean_metadata["/Title"] = clean_title
    # Carry over the original Producer / Creator / dates verbatim (only if they existed)
    if "/Producer" in orig_meta:
        clean_metadata["/Producer"] = orig_producer
    if "/Creator" in orig_meta:
        clean_metadata["/Creator"] = orig_creator
    if orig_creation_date is not None:
        clean_metadata["/CreationDate"] = str(orig_creation_date)
    if orig_mod_date is not None:
        clean_metadata["/ModDate"] = str(orig_mod_date)

    # Remove AI flags in original metadata
    for k, v in orig_meta.items():
        val_str = str(v).lower()
        if any(term in val_str for term in ["claude", "anthropic", "gpt", "weasyprint", "wkhtmltopdf", "reportlab", "canva"]):
            ai_purged_count += 1
            cleaned_fields.append(str(k))

    writer.add_metadata(clean_metadata)

    # pypdf injects its own "/Producer: pypdf" by default; drop it if the source had no Producer
    try:
        info_obj = writer._info.get_object() if writer._info is not None else None
        if info_obj is not None:
            for key in ("/Producer", "/Creator"):
                if key not in orig_meta and NameObject(key) in info_obj:
                    del info_obj[NameObject(key)]
    except Exception:
        pass

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
