from nonai.core.markdown_cleaner import clean_markdown

def test_markdown_cleaner():
    robotic_md = """# Title\u200B

| Column 1             | Column 2            |
|:---------------------|:--------------------|
| Value 1              | Value 2             |
| Longer string value  | Short               |

- Item 1
  - Subitem 1
  - Subitem 2
"""
    result = clean_markdown(robotic_md)
    assert result.unicode_chars_removed == 1
    assert "\u200B" not in result.cleaned_text
    assert "|:---------------------|" not in result.cleaned_text
    assert "| Column 1 | Column 2 |" in result.cleaned_text
    print("test_markdown_cleaner passed successfully!")

if __name__ == "__main__":
    test_markdown_cleaner()
