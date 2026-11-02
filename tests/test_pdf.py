import io
from pypdf import PdfWriter, PdfReader
from nonai.core.pdf_sanitizer import sanitize_pdf

def create_mock_pdf(producer: str = "Microsoft® Word for Microsoft 365", creator: str = "Microsoft® Word for Microsoft 365") -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    meta = {"/Author": "Someone"}
    if producer is not None:
        meta["/Producer"] = producer
    if creator is not None:
        meta["/Creator"] = creator
    writer.add_metadata(meta)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()

def test_pdf_preserves_original_producer_and_creator():
    orig_producer = "iText 7.2.5 (AGPL-version)"
    orig_creator = "Microsoft® Word for Microsoft 365"
    mock_bytes = create_mock_pdf(orig_producer, orig_creator)

    # spoof_target is ignored; original values must survive byte-for-byte
    for target in ("macOS", "Word"):
        result = sanitize_pdf(mock_bytes, author_name="Alex Wang", spoof_target=target)
        assert result.original_producer == orig_producer
        assert result.original_creator == orig_creator
        assert result.spoofed_producer == orig_producer
        assert result.spoofed_creator == orig_creator

        meta = PdfReader(io.BytesIO(result.cleaned_bytes)).metadata
        assert meta["/Producer"] == orig_producer
        assert meta["/Creator"] == orig_creator
        assert meta["/Author"] == "Alex Wang"
        assert "Quartz" not in str(meta.get("/Producer"))

def test_pdf_does_not_invent_missing_creator():
    mock_bytes = create_mock_pdf(producer="LibreOffice 7.6", creator=None)
    result = sanitize_pdf(mock_bytes)
    meta = PdfReader(io.BytesIO(result.cleaned_bytes)).metadata
    assert meta["/Producer"] == "LibreOffice 7.6"
    assert "/Creator" not in meta

def test_pdf_preserves_original_dates():
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.add_metadata({
        "/Producer": "Microsoft® Word for Microsoft 365",
        "/CreationDate": "D:20260115083012+08'00'",
        "/ModDate": "D:20260120171545+08'00'",
    })
    buf = io.BytesIO()
    writer.write(buf)

    result = sanitize_pdf(buf.getvalue())
    meta = PdfReader(io.BytesIO(result.cleaned_bytes)).metadata
    assert meta["/CreationDate"] == "D:20260115083012+08'00'"
    assert meta["/ModDate"] == "D:20260120171545+08'00'"

def test_pdf_does_not_invent_missing_dates():
    result = sanitize_pdf(create_mock_pdf())
    meta = PdfReader(io.BytesIO(result.cleaned_bytes)).metadata
    assert "/CreationDate" not in meta
    assert "/ModDate" not in meta

if __name__ == "__main__":
    test_pdf_preserves_original_producer_and_creator()
    test_pdf_does_not_invent_missing_creator()
    test_pdf_preserves_original_dates()
    test_pdf_does_not_invent_missing_dates()
    print("PDF tests passed")
