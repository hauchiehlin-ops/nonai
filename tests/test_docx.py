import io
import zipfile
from lxml import etree
from nonai.core.docx_sanitizer import sanitize_docx, W_NS, EP_NS

def create_mock_ai_docx() -> bytes:
    """Create a minimal raw docx representing an AI export without RSIDs."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        # [Content_Types].xml
        z.writestr("[Content_Types].xml", b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>""")

        # word/document.xml with ghost background shading and zero-width spaces
        z.writestr("word/document.xml", b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr>
        <w:shd w:fill="F7F7F8"/>
      </w:pPr>
      <w:r>
        <w:rPr>
          <w:rFonts w:ascii="Inter"/>
          <w:shd w:fill="F7F7F8"/>
        </w:rPr>
        <w:t>\xe2\x80\x8b\xe2\x80\x8c\xe4\xba\xba\xe5\xb7\xa5\xe6\x99\xba\xe6\x85\xa7\xe7\x94\x9f\xe6\x88\x90\xe7\x9a\x84\xe5\x85\xa7\xe5\xae\xb9\xef\xbc\x8c\xe5\xb8\xb8\xe5\xb8\xb8\xe5\xb8\xb6\xe6\x9c\x89\xe6\x98\x8e\xe9\xa1\xaf\xe7\x9a\x84\xe6\xa9\x9f\xe5\x99\xa8\xe7\x89\xb9\xe5\xbe\xb5\xe3\x80\x82</w:t>
      </w:r>
    </w:p>
  </w:body>
</w:document>""")

        # docProps/app.xml indicating python-docx or 0 editing time
        z.writestr("docProps/app.xml", b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">
  <Application>python-docx</Application>
  <TotalTime>0</TotalTime>
</Properties>""")

    return buf.getvalue()

def test_docx_sanitization():
    mock_bytes = create_mock_ai_docx()
    result = sanitize_docx(mock_bytes, author_name="Alex Wang", rsid_session_count=20)

    assert result.original_rsid_count == 0
    assert result.final_rsid_count == 20
    assert result.total_rsids_injected > 0
    assert result.ghost_styles_removed > 0
    assert result.unicode_chars_removed > 0
    assert result.estimated_human_minutes >= 18

    # Verify output zip validity
    out_zip = zipfile.ZipFile(io.BytesIO(result.cleaned_bytes), "r")
    assert "word/settings.xml" in out_zip.namelist()
    assert "word/document.xml" in out_zip.namelist()
    assert "docProps/app.xml" in out_zip.namelist()

    # Verify settings.xml has rsids
    settings_root = etree.fromstring(out_zip.read("word/settings.xml"))
    rsid_elems = list(settings_root.iter(f"{{{W_NS}}}rsid"))
    assert len(rsid_elems) == 20

    # Verify app.xml spoofed
    app_root = etree.fromstring(out_zip.read("docProps/app.xml"))
    app_name = app_root.find(f"{{{EP_NS}}}Application").text
    assert app_name == "Microsoft Office Word"

    # Verify document.xml has no F7F7F8 shading
    doc_xml_str = out_zip.read("word/document.xml").decode("utf-8")
    assert "F7F7F8" not in doc_xml_str
    assert "\u200B" not in doc_xml_str
    assert "w:rsidR=" in doc_xml_str

    print("test_docx_sanitization passed successfully!")

if __name__ == "__main__":
    test_docx_sanitization()
