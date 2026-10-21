import io
from pypdf import PdfWriter, PdfReader
from nonai.core.pdf_sanitizer import sanitize_pdf

def create_mock_ai_pdf() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    writer.add_metadata({
        "/Producer": "python-pdf-lib 1.0.0",
        "/Creator": "ChatGPT Export Service",
        "/Author": "OpenAI Bot"
    })
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()

def test_pdf_sanitization():
    mock_bytes = create_mock_ai_pdf()
    result = sanitize_pdf(mock_bytes, author_name="Alex Wang", spoof_target="macOS")

    assert result.original_producer == "python-pdf-lib 1.0.0"
    assert result.original_creator == "ChatGPT Export Service"
    assert result.spoofed_producer == "macOS Version 15.3.1 Quartz PDFContext"
    assert result.spoofed_creator == "Pages"

    # Read back sanitized pdf
    reader = PdfReader(io.BytesIO(result.cleaned_bytes))
    meta = reader.metadata
    assert meta["/Producer"] == "macOS Version 15.3.1 Quartz PDFContext"
    assert meta["/Creator"] == "Pages"
    assert meta["/Author"] == "Alex Wang"
    print("test_pdf_sanitization passed successfully!")

if __name__ == "__main__":
    test_pdf_sanitization()
