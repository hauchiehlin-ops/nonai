import io
import zipfile
from lxml import etree
from nonai.core.docx_sanitizer import sanitize_docx
from nonai.core.semantic_perturb import perturb_text

def test_ai_detection_shield():
    # 1. Create a mock DOCX containing Claude Docs signature and lacking Word package files
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        # Minimal document.xml with Claude academic clichés
        doc_xml = b"""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:r><w:t>\xe8\xa8\x88\xe7\x95\xab\xe4\xb8\xbb\xe8\xbb\xb8\xef\xbc\x9a\xe6\x96\xb9\xe6\xb3\x95\xe8\xab\x96\xe6\x9c\xac\xe8\xba\xab\xe5\xb0\xb1\xe6\x98\xaf\xe4\xb8\xbb\xe8\xa7\x92\xe3\x80\x82</w:t></w:r>
    </w:p>
    <w:p>
      <w:r><w:t>\xe5\xad\xb8\xe8\xa1\x93\xe4\xb8\x8a\xef\xbc\x8c\xe6\x8f\x90\xe5\x87\xba\xe7\xa0\x94\xe7\xa9\xb6\xe7\xae\xa1\xe7\xb7\x9a\xe3\x80\x82\xe5\xaf\xa6\xe5\x8b\x99\xe4\xb8\x8a\xef\xbc\x8c\xe6\x8f\x90\xe4\xbe\x9b\xe5\x88\x86\xe7\xbe\xa4\xe5\xb7\xa5\xe5\x85\xb7\xe3\x80\x82\xe7\xa4\xbe\xe6\x9c\x83\xe9\x9d\xa2\xe4\xb8\x8a\xef\xbc\x8c\xe5\xbb\xba\xe7\xab\x8b\xe7\xa0\x94\xe7\xa9\xb6\xe6\x8c\x87\xe5\xbc\x95\xe3\x80\x82</w:t></w:r>
    </w:p>
  </w:body>
</w:document>"""
        z.writestr("word/document.xml", doc_xml)

        # core.xml containing smoking-gun Claude Docs metadata
        core_xml = b"""<?xml version="1.0" encoding="utf-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>Test Plan</dc:title>
  <dc:description>Claude Docs node/c250b5e7-3a9a@61 docx-w7</dc:description>
  <cp:revision>1</cp:revision>
</cp:coreProperties>"""
        z.writestr("docProps/core.xml", core_xml)

        # minimal [Content_Types].xml
        ct_xml = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
</Types>"""
        z.writestr("[Content_Types].xml", ct_xml)

        # minimal rels
        rels_xml = b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
</Relationships>"""
        z.writestr("word/_rels/document.xml.rels", rels_xml)

    # 2. Execute Sanitize
    raw_docx = buf.getvalue()
    res = sanitize_docx(raw_docx, author_name="Dr. Tester", enable_perturb=True, perturb_intensity=0.9)

    # 3. Verify Result
    assert res.claude_signatures_purged >= 1, "Failed to purge Claude Docs signature!"
    assert len(res.missing_parts_synthesized) == 3, f"Expected 3 synthesized parts, got {res.missing_parts_synthesized}"

    with zipfile.ZipFile(io.BytesIO(res.cleaned_bytes), "r") as z:
        names = z.namelist()
        assert "word/fontTable.xml" in names, "fontTable.xml not found in output ZIP!"
        assert "word/webSettings.xml" in names, "webSettings.xml not found in output ZIP!"
        assert "word/theme/theme1.xml" in names, "theme1.xml not found in output ZIP!"

        # Verify core.xml
        core = z.read("docProps/core.xml").decode("utf-8")
        assert "Claude" not in core, "Claude found in core.xml!"
        assert "node/" not in core, "node/ found in core.xml!"
        assert "description" not in core, "description element found in core.xml!"

        # Verify app.xml
        app = z.read("docProps/app.xml").decode("utf-8")
        assert "Microsoft Office Word" in app, "Missing Application!"
        assert "Normal.dotm" in app, "Missing Normal.dotm template!"
        assert "16.0000" in app, "Missing AppVersion 16.0000!"

        # Verify [Content_Types].xml
        ct = z.read("[Content_Types].xml").decode("utf-8")
        assert "fontTable.xml" in ct, "fontTable missing from [Content_Types].xml!"
        assert "webSettings.xml" in ct, "webSettings missing from [Content_Types].xml!"
        assert "theme1.xml" in ct, "theme1 missing from [Content_Types].xml!"

        # Verify word/_rels/document.xml.rels
        rels = z.read("word/_rels/document.xml.rels").decode("utf-8")
        assert "fontTable.xml" in rels, "fontTable missing from document.xml.rels!"
        assert "webSettings.xml" in rels, "webSettings missing from document.xml.rels!"
        assert "theme/theme1.xml" in rels, "theme missing from document.xml.rels!"

        # Verify document.xml semantic perturbation
        doc = z.read("word/document.xml").decode("utf-8")
        assert "方法論本身就是主角" not in doc, "Claude cliché not perturbed in document.xml!"
        assert "學術上，提出研究管線" not in doc, "Academic triple not perturbed in document.xml!"

    print("test_ai_detection_shield passed successfully 100%!")

if __name__ == "__main__":
    test_ai_detection_shield()
