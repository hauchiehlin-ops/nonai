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

def test_docx_windows_word_compatibility():
    """Verify that docx with existing complex settings, relationships, and mentions of Claude remains well-formed and valid."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
</Types>""")
        z.writestr("word/settings.xml", b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:settings xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:defaultTabStop w:val="720"/>
  <w:characterSpacingControl w:val="doNotCompress"/>
  <w:compat>
    <w:compatSetting w:name="compatibilityMode" w:uri="http://schemas.microsoft.com/office/word" w:val="15"/>
  </w:compat>
</w:settings>""")
        z.writestr("word/_rels/document.xml.rels", b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
</Relationships>""")
        z.writestr("word/document.xml", b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:r>
        <w:t>In 1948, Claude Shannon published his seminal paper on information theory.</w:t>
      </w:r>
    </w:p>
  </w:body>
</w:document>""")

    res = sanitize_docx(buf.getvalue(), author_name="Researcher", rsid_session_count=10)
    out_zip = zipfile.ZipFile(io.BytesIO(res.cleaned_bytes), "r")

    # All XML files must parse without any XMLSyntaxError
    for fname in out_zip.namelist():
        if fname.endswith(".xml") or fname.endswith(".rels"):
            content = out_zip.read(fname)
            etree.fromstring(content)

    # Verify relationships do not contain duplicated types
    rels_content = out_zip.read("word/_rels/document.xml.rels")
    r_root = etree.fromstring(rels_content)
    types_found = [el.get("Type") for el in r_root]
    assert len(types_found) == len(set(types_found)), "Duplicate relationship types detected!"

    print("test_docx_windows_word_compatibility passed successfully!")


def test_docx_table_and_gantt_shading_preserved():
    """Verify that table cell background shading (Gantt chart progress bars), milestones, and symbols are preserved."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>""")
        # Document containing:
        # 1. Normal body paragraph with AI ghost shading F7F7F8 (MUST be stripped)
        # 2. Table Gantt chart with cell shading FFD2B8 and D4EFDF (MUST be preserved)
        # 3. Milestone row with diamond symbol ◆ and exact date (MUST be preserved)
        doc_xml = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:shd w:fill="F7F7F8"/></w:pPr>
      <w:r>
        <w:rPr><w:shd w:fill="F7F7F8"/></w:rPr>
        <w:t>\xe9\x80\x99\xe6\x98\xaf\xe5\x85\xb7\xe6\x9c\x89 AI \xe8\x83\x8c\xe6\x99\xaf\xe5\xba\x95\xe8\x89\xb2\xe7\x9a\x84\xe6\xae\xb5\xe8\x90\xbd\xe3\x80\x82</w:t>
      </w:r>
    </w:p>
    <w:tbl>
      <w:tblPr>
        <w:tblW w:w="5000" w:type="dxa"/>
      </w:tblPr>
      <w:tr>
        <w:tc>
          <w:tcPr>
            <w:shd w:fill="FFD2B8"/>
          </w:tcPr>
          <w:p>
            <w:r><w:t>\xe4\xb8\x80 1a: \xe8\xa8\xaa\xe8\xab\x87\xe5\xa4\xa7\xe7\xb6\xb1\xe5\x89\x8d\xe5\xb0\x8e (N = 6)</w:t></w:r>
          </w:p>
        </w:tc>
        <w:tc>
          <w:tcPr>
            <w:shd w:fill="D4EFDF"/>
          </w:tcPr>
          <w:p>
            <w:r><w:t>\xe9\x80\xb2\xe5\xba\xa6\xe8\x89\xb2\xe5\xa1\x8a</w:t></w:r>
          </w:p>
        </w:tc>
      </w:tr>
      <w:tr>
        <w:tc>
          <w:p>
            <w:r><w:t>\xe9\x87\x8c\xe7\xa8\x8b\xe7\xa2\x91\xef\xbc\x9a\xe7\xac\xac\xe4\xb8\x80\xe9\x9a\x8e\xe6\xae\xb5\xe5\x83\xb9\xe5\x80\xbc\xe9\x8f\x88\xe8\x88\x87\xe9\x87\x8f\xe8\xa1\xa8\xe5\xae\x8c\xe6\x88\x90 (2028.03.31)</w:t></w:r>
          </w:p>
        </w:tc>
        <w:tc>
          <w:p>
            <w:r><w:t>\xe2\x97\x86</w:t></w:r>
          </w:p>
        </w:tc>
      </w:tr>
    </w:tbl>
  </w:body>
</w:document>"""
        z.writestr("word/document.xml", doc_xml)

    res = sanitize_docx(buf.getvalue(), author_name="Researcher", enable_perturb=True)
    out_zip = zipfile.ZipFile(io.BytesIO(res.cleaned_bytes), "r")
    cleaned_doc_xml = out_zip.read("word/document.xml").decode("utf-8")

    # 1. Body ghost shading MUST be stripped
    assert "F7F7F8" not in cleaned_doc_xml, "AI ghost shading F7F7F8 was not stripped!"

    # 2. Table cell shading (Gantt chart progress bars) MUST be preserved!
    assert "FFD2B8" in cleaned_doc_xml, "Table cell shading FFD2B8 was incorrectly removed!"
    assert "D4EFDF" in cleaned_doc_xml, "Table cell shading D4EFDF was incorrectly removed!"

    # 3. Milestone symbol ◆ and text MUST be preserved intact inside table
    assert "◆" in cleaned_doc_xml, "Milestone symbol ◆ was removed or corrupted!"
    assert "里程碑：第一階段價值鏈與量表完成 (2028.03.31)" in cleaned_doc_xml, "Milestone text was corrupted!"

    print("test_docx_table_and_gantt_shading_preserved passed successfully!")


if __name__ == "__main__":
    test_docx_sanitization()
    test_docx_windows_word_compatibility()
    test_docx_table_and_gantt_shading_preserved()
