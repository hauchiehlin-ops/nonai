"""
PDF Metadata and Fingerprint Sanitizer
Strips AI generator signatures, cleans XMP streams, and spoofs standard OS/Office PDF context.
"""

import io
from datetime import datetime, timezone
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, create_string_object

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


def sanitize_pdf(
    file_bytes: bytes,
    author_name: str = "Author",
    spoof_target: str = "macOS"  # "macOS" or "Word"
) -> PdfSanitizeResult:
    """
    Sanitizes PDF metadata:
    - Strips/spoofs Producer (e.g. Quartz PDFContext or Microsoft Word)
    - Strips/spoofs Creator
    - Strips raw XMP metadata streams that contain library names
    - Normalizes creation/modification timestamps
    """
    reader = PdfReader(io.BytesIO(file_bytes))
    writer = PdfWriter()

    # Copy all pages
    for page in reader.pages:
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

    now_str = datetime.now(timezone.utc).strftime("D:%Y%m%d%H%M%SZ")

    # Set clean metadata dictionary
    clean_metadata = {
        "/Producer": target_producer,
        "/Creator": target_creator,
        "/Author": author_name,
        "/CreationDate": now_str,
        "/ModDate": now_str,
    }

    writer.add_metadata(clean_metadata)

    # Clean XMP metadata if present in root catalog
    xmp_cleaned = False
    try:
        if "/Metadata" in writer._root_object:
            del writer._root_object[NameObject("/Metadata")]
            xmp_cleaned = True
    except Exception:
        pass

    out_buf = io.BytesIO()
    writer.write(out_buf)

    return PdfSanitizeResult(
        cleaned_bytes=out_buf.getvalue(),
        original_producer=orig_producer,
        original_creator=orig_creator,
        original_metadata={str(k): str(v) for k, v in orig_meta.items()},
        spoofed_producer=target_producer,
        spoofed_creator=target_creator,
        xmp_cleaned=xmp_cleaned,
        total_pages=len(reader.pages)
    )
