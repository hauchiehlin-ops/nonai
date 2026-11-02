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


def test_docx_rsid_parity_revision_coupling_and_yellow_highlight():
    """
    Verifies the 6 forensic upgrades + mandatory yellow highlight (<w:highlight w:val="yellow"/>):
    1. Zero unregistered RSIDs between word/document.xml and word/settings.xml (#1).
    2. cp:revision in docProps/core.xml is strictly greater than total RSIDs (#2).
    3. No single RSID dominates >20% of paragraphs or characters (#9).
    4. Multi-run split sentences in <w:p> are restructured and highlighted with <w:highlight w:val="yellow"/>.
    5. Standalone transitions (首先, 其次, 最後, 此外) and non-standard spaces (\u2003, \u3000) are eliminated (#3, #5-#8).
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>""")

        # Build 40 paragraphs with pre-existing unregistered RSIDs (e.g. 00DEAD01..00DEAD40)
        # and dominant single-paste RSID 00PASTE1 on w:rsidP / w:rsidRPr
        p_xml_list = []
        # Paragraph 1: Split across 3 <w:r> runs with '首先，本研究旨在...進而...以期達到...之效益'
        p_xml_list.append("""
        <w:p w:rsidR="00PASTE1" w:rsidP="00PASTE1" w:rsidRPr="00DEAD01">
          <w:r w:rsidR="00DEAD02"><w:t>首先，本研究</w:t></w:r>
          <w:r w:rsidR="00DEAD03"><w:t>旨在建立高齡照護評估模型，進而探討</w:t></w:r>
          <w:r w:rsidR="00DEAD04"><w:t>臨床落差\u2003，以期達到顯著提升照護品質之效益。</w:t></w:r>
        </w:p>
        """)
        # Paragraph 2: '其次，...' with unanchored claim
        p_xml_list.append("""
        <w:p w:rsidR="00PASTE1" w:rsidP="00PASTE1" w:rsidRPr="00DEAD05">
          <w:r><w:t>其次，研究顯示系統導入後滿意度顯著提升了 35.8%。此結果與近期實證相符 (Chen et al., 2024)。</w:t></w:r>
        </w:p>
        """)
        # Paragraph 3: '最後，...' and '此外，...'
        p_xml_list.append("""
        <w:p w:rsidR="00PASTE1" w:rsidP="00PASTE1" w:rsidRPr="00DEAD06">
          <w:r><w:t>最後，我們彙整了所有訪談紀錄\u3000。此外，本研究者與研究所團隊也針對大學生進行了系統性分析。</w:t></w:r>
        </w:p>
        """)
        # Add 37 more paragraphs with dominant 00PASTE1 and distinct 00DEADxx RSIDs
        for idx in range(7, 44):
            p_xml_list.append(f"""
            <w:p w:rsidR="00PASTE1" w:rsidP="00PASTE1" w:rsidRPr="00DEAD{idx:02d}">
              <w:r w:rsidRPr="00DEAD{idx:02d}"><w:t>這是第 {idx} 段常規背景敘述文字，保持原本的實驗設計紀錄與觀察描述。</w:t></w:r>
            </w:p>
            """)

        doc_xml_str = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {"".join(p_xml_list)}
    <w:sectPr w:rsidR="00DEAD99" w:rsidSect="00DEAD98"/>
  </w:body>
</w:document>"""
        z.writestr("word/document.xml", doc_xml_str.encode("utf-8"))

    res = sanitize_docx(buf.getvalue(), author_name="Prof. Lin", rsid_session_count=20)
    out_zip = zipfile.ZipFile(io.BytesIO(res.cleaned_bytes), "r")

    doc_root = etree.fromstring(out_zip.read("word/document.xml"))
    settings_root = etree.fromstring(out_zip.read("word/settings.xml"))
    core_root = etree.fromstring(out_zip.read("docProps/core.xml"))

    # 1. Verify ZERO unregistered RSIDs in word/document.xml
    registered_rsids = {
        el.get(f"{{{W_NS}}}val").upper()
        for el in settings_root.iter(f"{{{W_NS}}}rsid")
        if el.get(f"{{{W_NS}}}val")
    }
    doc_rsids = set()
    for el in doc_root.iter():
        for k, v in el.attrib.items():
            if "rsid" in k.lower():
                doc_rsids.add(v.upper())

    unregistered = doc_rsids - registered_rsids
    assert len(unregistered) == 0, f"Found unregistered RSIDs in document.xml: {unregistered}"
    assert "00PASTE1" not in doc_rsids, "Old dominant RSID 00PASTE1 was not purged!"

    # 2. Verify cp:revision > len(registered_rsids)
    cp_ns = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
    rev_text = core_root.find(f"{{{cp_ns}}}revision").text
    rev_val = int(rev_text)
    assert rev_val > len(registered_rsids), f"Revision ({rev_val}) must be > RSID count ({len(registered_rsids)})!"

    # 3. Verify no single RSID dominates > 20% of paragraphs
    p_rsid_counts = {}
    all_ps = list(doc_root.iter(f"{{{W_NS}}}p"))
    for p in all_ps:
        r_val = p.get(f"{{{W_NS}}}rsidR")
        p_rsid_counts[r_val] = p_rsid_counts.get(r_val, 0) + 1
    max_share = max(p_rsid_counts.values()) / len(all_ps)
    assert max_share <= 0.20, f"Single RSID still dominates {max_share:.1%} of paragraphs!"

    # 4. Verify yellow highlight (<w:highlight w:val="yellow"/>) is present on modified spans
    highlights = list(doc_root.iter(f"{{{W_NS}}}highlight"))
    assert len(highlights) > 0, "Expected <w:highlight w:val='yellow'/> on modified runs!"
    assert all(h.get(f"{{{W_NS}}}val") == "yellow" for h in highlights)
    assert res.highlighted_changes > 0

    # 5. Verify full text has no standalone 首先， / 其次， / 最後， / 此外，, no \u2003/\u3000, and no broken collocations
    full_text = "".join(doc_root.itertext())
    assert "首先，" not in full_text
    assert "其次，" not in full_text
    assert "最後，" not in full_text
    assert "此外，" not in full_text
    assert "\u2003" not in full_text
    assert "\u3000" not in full_text
    assert "研究者" in full_text, "Compound word '研究者' was corrupted!"
    assert "研究所" in full_text, "Compound word '研究所' was corrupted!"
    assert "大學生" in full_text, "Compound word '大學生' was corrupted!"
    assert "系統性" in full_text, "Compound word '系統性' was corrupted!"

    print("test_docx_rsid_parity_revision_coupling_and_yellow_highlight passed successfully!")


def test_docx_preserve_all_punctuations_and_highlight_replacements():
    """
    STRICT USER CONSTRAINT TEST:
    'AI訊號的修正，若需更動文檔內容，必須保留既有的標點符號，僅需替換文字敘述並hightline'
    Verifies that:
    1. Every punctuation mark in the document is 100% preserved (exact type and order: ，;、?!:。).
    2. Modified text spans are highlighted with <w:highlight w:val="yellow"/>.
    3. Unmodified spans and punctuation remain clean without corruption.
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", b"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>""")
        # Paragraph with distinct punctuations: ，, 、, ；, ！, ？, ：, 。
        orig_para_text = "首先，這項研究旨在探討教育模式、其次；文獻指出其具有重要意義！深入探討至關重要？最後：我們將全面提升學習效益。"
        doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:r><w:t>{orig_para_text}</w:t></w:r>
    </w:p>
  </w:body>
</w:document>"""
        z.writestr("word/document.xml", doc_xml.encode("utf-8"))

    res = sanitize_docx(buf.getvalue(), author_name="Researcher", preserve_punctuation=True, highlight_changes=True)
    out_zip = zipfile.ZipFile(io.BytesIO(res.cleaned_bytes), "r")
    cleaned_root = etree.fromstring(out_zip.read("word/document.xml"))

    cleaned_text = "".join(cleaned_root.itertext())

    # 1. Verify text modification took place
    assert "這項研究旨在" not in cleaned_text
    assert "深入探討" not in cleaned_text
    assert "全面提升" not in cleaned_text
    assert "具有重要意義" not in cleaned_text

    # 2. Extract punctuation sequences from original and cleaned text
    from nonai.core.semantic_restructure import extract_punctuation_sequence
    orig_puncs = extract_punctuation_sequence(orig_para_text)
    cleaned_puncs = extract_punctuation_sequence(cleaned_text)

    # STRICT ASSERTION: Punctuation sequence must be 100% IDENTICAL
    assert orig_puncs == cleaned_puncs, f"Punctuation altered! Expected {orig_puncs}, but got {cleaned_puncs}"

    # 3. Verify yellow highlight (<w:highlight w:val="yellow"/>) on modified text spans
    highlights = list(cleaned_root.iter(f"{{{W_NS}}}highlight"))
    assert len(highlights) > 0, "No highlights found on modified text!"
    assert all(h.get(f"{{{W_NS}}}val") == "yellow" for h in highlights)

    # 4. Verify runs with highlights contain the newly substituted text
    highlighted_runs = [
        r for r in cleaned_root.iter(f"{{{W_NS}}}r")
        if r.find(f"{{{W_NS}}}rPr") is not None and r.find(f"{{{W_NS}}}rPr").find(f"{{{W_NS}}}highlight") is not None
    ]
    highlighted_texts = "".join("".join(r.itertext()) for r in highlighted_runs)
    assert len(highlighted_texts) > 0

    print("test_docx_preserve_all_punctuations_and_highlight_replacements passed successfully 100%!")


if __name__ == "__main__":
    test_docx_sanitization()
    test_docx_windows_word_compatibility()
    test_docx_table_and_gantt_shading_preserved()
    test_docx_rsid_parity_revision_coupling_and_yellow_highlight()
    test_docx_preserve_all_punctuations_and_highlight_replacements()
