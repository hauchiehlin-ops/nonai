"""
NonAI Web API Server
FastAPI backend providing file processing, text sanitization, and clipboard watcher control.
"""

import base64
import io
import json
import os
import uuid
import tempfile
from urllib.parse import quote
from typing import Optional
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from nonai.core.unicode_cleaner import clean_unicode, inspect_unicode_anomalies
from nonai.core.docx_sanitizer import sanitize_docx
from nonai.core.pdf_sanitizer import sanitize_pdf
from nonai.core.markdown_cleaner import clean_markdown
from nonai.core.semantic_perturb import perturb_text
from nonai.core.detector_audit import audit_text_fingerprints
from nonai.clipboard.watcher import ClipboardWatcher, ClipboardEvent

app = FastAPI(title="NonAI - AI Fingerprint Removal Platform")

# Version metadata
VERSION_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "version.json")
try:
    with open(VERSION_FILE, "r", encoding="utf-8") as vf:
        VERSION_DATA = json.load(vf)
except Exception:
    VERSION_DATA = {"version": "1.1.0", "release_date": "2026-10-21", "bump_level": "minor"}

# In-memory storage for processed downloadable files
DOWNLOAD_CACHE = {}

# Global clipboard watcher instance - Default to active state
watcher_instance = ClipboardWatcher(poll_interval=0.5, enable_perturbation=True)
try:
    watcher_instance.start()
except Exception:
    pass

class CleanTextRequest(BaseModel):
    text: str
    enable_perturb: bool = True
    perturb_intensity: float = 0.65
    de_perfectionize_md: bool = True

class ToggleWatcherRequest(BaseModel):
    active: bool
    enable_perturb: bool = True

@app.get("/api/version")
async def api_get_version():
    return VERSION_DATA

@app.post("/api/clean-text")
async def api_clean_text(req: CleanTextRequest):
    text = req.text
    if not text:
        return {"cleaned_text": "", "audit": None, "unicode_stats": None}

    # 1. Inspect original text
    anomalies_before = inspect_unicode_anomalies(text)
    audit_before = audit_text_fingerprints(text)

    # 2. Clean unicode
    u_res = clean_unicode(text)
    cleaned = u_res.cleaned_text

    # 3. Markdown de-perfection if requested
    md_res = None
    if req.de_perfectionize_md:
        md_res = clean_markdown(cleaned, strip_unicode=False)
        cleaned = md_res.cleaned_text

    # 4. Optional perturbation
    p_res = None
    if req.enable_perturb:
        p_res = perturb_text(cleaned, intensity=req.perturb_intensity)
        cleaned = p_res.perturbed_text

    audit_after = audit_text_fingerprints(cleaned)

    return {
        "cleaned_text": cleaned,
        "original_length": len(text),
        "cleaned_length": len(cleaned),
        "anomalies_before": anomalies_before,
        "unicode_stats": {
            "total_removed": u_res.total_removed,
            "normalized_spaces": u_res.normalized_spaces,
            "char_counts": u_res.char_counts,
        },
        "markdown_stats": {
            "tables_adjusted": md_res.tables_de_perfectionized if md_res else 0,
            "lists_varied": md_res.lists_varied if md_res else 0,
        } if md_res else None,
        "perturb_stats": {
            "replacements_made": p_res.replacements_made if p_res else 0,
            "reorganized": p_res.sentences_reorganized if p_res else 0,
            "disruption_rate": p_res.estimated_ngram_disruption_rate if p_res else 0,
        } if p_res else None,
        "audit_before": {
            "risk_score": audit_before.overall_risk_score,
            "risk_level": audit_before.risk_level,
            "recommendations": audit_before.recommendations,
        },
        "audit_after": {
            "risk_score": audit_after.overall_risk_score,
            "risk_level": audit_after.risk_level,
        }
    }

@app.post("/api/clean-file")
async def api_clean_file(
    file: UploadFile = File(...),
    author: str = Form("Author"),
    rsid_count: int = Form(25),
    pdf_spoof: str = Form("macOS"),
    enable_perturb: bool = Form(True),
    perturb_intensity: float = Form(0.7)
):
    filename = file.filename or "document"
    ext = os.path.splitext(filename)[1].lower()
    content = await file.read()

    file_id = str(uuid.uuid4())
    cleaned_filename = f"{os.path.splitext(filename)[0]}_clean{ext}"

    if ext == ".docx":
        docx_res = sanitize_docx(
            content,
            author_name=author,
            rsid_session_count=rsid_count,
            enable_perturb=enable_perturb,
            perturb_intensity=perturb_intensity
        )
        mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        file_b64 = base64.b64encode(docx_res.cleaned_bytes).decode("ascii")

        DOWNLOAD_CACHE[file_id] = {
            "bytes": docx_res.cleaned_bytes,
            "filename": cleaned_filename,
            "mime": mime
        }
        return {
            "file_id": file_id,
            "filename": cleaned_filename,
            "file_type": "docx",
            "file_b64": file_b64,
            "mime": mime,
            "stats": {
                "rsid_injected": docx_res.final_rsid_count,
                "original_rsids": docx_res.original_rsid_count,
                "runs_split": docx_res.runs_split,
                "ghost_styles_removed": docx_res.ghost_styles_removed,
                "unicode_removed": docx_res.unicode_chars_removed,
                "human_editing_minutes": docx_res.estimated_human_minutes,
                "application_spoofed": "Microsoft Office Word 16.0000",
                "semantic_replacements": docx_res.semantic_replacements,
                "semantic_reorganized": docx_res.semantic_reorganized,
                "claude_signatures_purged": docx_res.claude_signatures_purged,
                "missing_parts_synthesized": docx_res.missing_parts_synthesized
            },
            "details": {
                "rsid_pool": docx_res.rsid_pool,
                "ghost_style_items": docx_res.ghost_style_items,
                "split_samples": docx_res.split_samples,
                "metadata_spoof_details": docx_res.metadata_spoof_details,
                "paragraphs_modified": docx_res.paragraphs_modified,
                "runs_split": docx_res.runs_split,
                "estimated_human_minutes": docx_res.estimated_human_minutes,
                "unicode_removed": docx_res.unicode_chars_removed,
                "semantic_replacements": docx_res.semantic_replacements,
                "semantic_reorganized": docx_res.semantic_reorganized,
                "claude_signatures_purged": docx_res.claude_signatures_purged,
                "missing_parts_synthesized": docx_res.missing_parts_synthesized
            }
        }

    elif ext == ".pdf":
        pdf_res = sanitize_pdf(
            content,
            author_name=author,
            spoof_target=pdf_spoof
        )
        mime = "application/pdf"
        file_b64 = base64.b64encode(pdf_res.cleaned_bytes).decode("ascii")

        DOWNLOAD_CACHE[file_id] = {
            "bytes": pdf_res.cleaned_bytes,
            "filename": cleaned_filename,
            "mime": mime
        }
        return {
            "file_id": file_id,
            "filename": cleaned_filename,
            "file_type": "pdf",
            "file_b64": file_b64,
            "mime": mime,
            "stats": {
                "original_producer": pdf_res.original_producer,
                "original_creator": pdf_res.original_creator,
                "spoofed_producer": pdf_res.spoofed_producer,
                "spoofed_creator": pdf_res.spoofed_creator,
                "xmp_cleaned": pdf_res.xmp_cleaned,
                "pages": pdf_res.total_pages,
                "ai_signatures_purged": pdf_res.ai_signatures_purged
            },
            "details": {
                "original_producer": pdf_res.original_producer,
                "original_creator": pdf_res.original_creator,
                "spoofed_producer": pdf_res.spoofed_producer,
                "spoofed_creator": pdf_res.spoofed_creator,
                "xmp_cleaned": pdf_res.xmp_cleaned,
                "pages": pdf_res.total_pages,
                "ai_signatures_purged": pdf_res.ai_signatures_purged,
                "metadata_fields_cleaned": pdf_res.metadata_fields_cleaned,
                "original_metadata": pdf_res.original_metadata
            }
        }

    elif ext in (".md", ".markdown"):
        text = content.decode("utf-8", errors="ignore")
        md_res = clean_markdown(
            text,
            enable_perturb=enable_perturb,
            perturb_intensity=perturb_intensity
        )
        final_text = md_res.cleaned_text

        cleaned_bytes = final_text.encode("utf-8")
        mime = "text/markdown"
        file_b64 = base64.b64encode(cleaned_bytes).decode("ascii")

        DOWNLOAD_CACHE[file_id] = {
            "bytes": cleaned_bytes,
            "filename": cleaned_filename,
            "mime": mime
        }
        return {
            "file_id": file_id,
            "filename": cleaned_filename,
            "file_type": "markdown",
            "file_b64": file_b64,
            "mime": mime,
            "stats": {
                "unicode_removed": md_res.unicode_chars_removed,
                "tables_de_perfectionized": md_res.tables_de_perfectionized,
                "lists_varied": md_res.lists_varied,
                "ai_bookends_removed": md_res.ai_bookends_removed,
                "semantic_replacements": md_res.semantic_replacements,
                "semantic_reorganized": md_res.semantic_reorganized
            },
            "details": {
                "unicode_removed": md_res.unicode_chars_removed,
                "tables_de_perfectionized": md_res.tables_de_perfectionized,
                "lists_varied": md_res.lists_varied,
                "ai_bookends_removed": md_res.ai_bookends_removed,
                "semantic_replacements": md_res.semantic_replacements,
                "semantic_reorganized": md_res.semantic_reorganized
            }
        }

    else:
        # Fallback TXT
        text = content.decode("utf-8", errors="ignore")
        u_res = clean_unicode(text)
        final_text = u_res.cleaned_text
        p_replacements = 0
        p_reorganized = 0
        if enable_perturb:
            p_res = perturb_text(final_text, intensity=perturb_intensity)
            final_text = p_res.perturbed_text
            p_replacements = p_res.replacements_made
            p_reorganized = p_res.sentences_reorganized

        cleaned_bytes = final_text.encode("utf-8")
        mime = "text/plain"
        file_b64 = base64.b64encode(cleaned_bytes).decode("ascii")

        DOWNLOAD_CACHE[file_id] = {
            "bytes": cleaned_bytes,
            "filename": cleaned_filename,
            "mime": mime
        }
        return {
            "file_id": file_id,
            "filename": cleaned_filename,
            "file_type": "text",
            "file_b64": file_b64,
            "mime": mime,
            "stats": {
                "unicode_removed": u_res.total_removed,
                "spaces_normalized": u_res.normalized_spaces,
                "semantic_replacements": p_replacements,
                "semantic_reorganized": p_reorganized
            },
            "details": {
                "unicode_removed": u_res.total_removed,
                "spaces_normalized": u_res.normalized_spaces,
                "char_counts": u_res.char_counts,
                "semantic_replacements": p_replacements,
                "semantic_reorganized": p_reorganized
            }
        }

@app.get("/api/download/{file_id}")
async def api_download(file_id: str):
    if file_id not in DOWNLOAD_CACHE:
        raise HTTPException(status_code=404, detail="檔案已過期或不存在")
    item = DOWNLOAD_CACHE[file_id]
    encoded_fn = quote(item["filename"])
    return StreamingResponse(
        io.BytesIO(item["bytes"]),
        media_type=item["mime"],
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{encoded_fn}",
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
    )

@app.get("/api/clipboard/status")
async def api_clipboard_status():
    events = watcher_instance.get_recent_events()
    return {
        "active": watcher_instance.is_running,
        "total_intercepted": len(events),
        "events": [
            {
                "timestamp": e.timestamp,
                "removed_chars": e.invisible_chars_removed,
                "spaces_norm": e.spaces_normalized,
                "snippet": e.snippet,
                "status": e.status
            }
            for e in reversed(events)
        ]
    }

@app.post("/api/clipboard/toggle")
async def api_clipboard_toggle(req: ToggleWatcherRequest):
    watcher_instance.enable_perturbation = req.enable_perturb
    if req.active:
        if not watcher_instance.is_running:
            watcher_instance.start()
    else:
        if watcher_instance.is_running:
            watcher_instance.stop()
    return {"active": watcher_instance.is_running}

# Mount static frontend
web_dir = os.path.join(os.path.dirname(__file__), "web")
public_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "public")
target_dir = public_dir if os.path.exists(public_dir) else web_dir

if os.path.exists(target_dir):
    app.mount("/", StaticFiles(directory=target_dir, html=True), name="web")
