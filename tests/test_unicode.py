from nonai.core.unicode_cleaner import clean_unicode, inspect_unicode_anomalies

def test_unicode_cleaner():
    # Construct a string with hidden zero-width spaces and non-breaking spaces
    # "\u200B" (ZWSP), "\u200C" (ZWNJ), "\uFEFF" (BOM), "\u00A0" (NBSP)
    dirty_text = "這是一段\u200B帶有\u200C零寬度\uFEFF字元的\u00A0測試文本。"
    
    findings = inspect_unicode_anomalies(dirty_text)
    assert len(findings) == 4, f"Expected 4 anomalies, got {len(findings)}"
    
    result = clean_unicode(dirty_text)
    assert result.total_removed == 3
    assert result.normalized_spaces == 1
    assert "\u200B" not in result.cleaned_text
    assert "\u200C" not in result.cleaned_text
    assert "\uFEFF" not in result.cleaned_text
    assert "\u00A0" not in result.cleaned_text
    assert result.cleaned_text == "這是一段帶有零寬度字元的 測試文本。"
    print("test_unicode_cleaner passed successfully!")

if __name__ == "__main__":
    test_unicode_cleaner()
