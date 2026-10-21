import time
from nonai.clipboard.watcher import ClipboardWatcher

def test_clipboard_watcher():
    watcher = ClipboardWatcher(poll_interval=0.1)
    
    # 1. Put dirty text on clipboard
    dirty = "ChatGPT 生成文字\u200B，帶有隱藏字元\u200C。"
    watcher.set_clipboard_text(dirty)
    time.sleep(0.05)
    
    # Run one check
    event = watcher.check_and_clean_once()
    assert event is not None
    assert event.invisible_chars_removed == 2
    
    # Verify clipboard was sanitized
    clean_text = watcher.get_clipboard_text()
    assert "\u200B" not in clean_text
    assert "\u200C" not in clean_text
    assert clean_text == "ChatGPT 生成文字，帶有隱藏字元。"
    print("test_clipboard_watcher passed successfully!")

if __name__ == "__main__":
    test_clipboard_watcher()
