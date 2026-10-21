"""
System Clipboard Watcher (Scheme C)
Background daemon that intercepts clipboard copy events, strips zero-width
characters and ghost web formatting in real-time.
"""

import subprocess
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, List, Optional
from nonai.core.unicode_cleaner import clean_unicode
from nonai.core.semantic_perturb import perturb_text

@dataclass
class ClipboardEvent:
    timestamp: str
    original_length: int
    cleaned_length: int
    invisible_chars_removed: int
    spaces_normalized: int
    snippet: str
    status: str  # "cleaned", "untouched", "error"


class ClipboardWatcher:
    def __init__(
        self,
        poll_interval: float = 0.5,
        enable_perturbation: bool = False,
        perturb_intensity: float = 0.3,
        on_event_callback: Optional[Callable[[ClipboardEvent], None]] = None
    ):
        self.poll_interval = poll_interval
        self.enable_perturbation = enable_perturbation
        self.perturb_intensity = perturb_intensity
        self.on_event_callback = on_event_callback
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._last_content = ""
        self._events: List[ClipboardEvent] = []
        self._lock = threading.Lock()

    def get_clipboard_text(self) -> str:
        """Read plain text from macOS clipboard using pbpaste."""
        try:
            result = subprocess.run(
                ["pbpaste"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            return result.stdout
        except Exception:
            return ""

    def set_clipboard_text(self, text: str) -> bool:
        """Write clean plain text to macOS clipboard using pbcopy, wiping rich formats."""
        try:
            subprocess.run(
                ["pbcopy"],
                input=text,
                text=True,
                check=True
            )
            return True
        except Exception:
            return False

    def check_and_clean_once(self) -> Optional[ClipboardEvent]:
        """Perform a single check on clipboard content."""
        current_text = self.get_clipboard_text()
        if not current_text or current_text == self._last_content:
            return None

        # Content changed from external copy action
        # 1. Clean unicode
        u_res = clean_unicode(current_text)
        cleaned = u_res.cleaned_text

        # 2. Optional perturbation
        if self.enable_perturbation and u_res.has_anomalies:
            p_res = perturb_text(cleaned, intensity=self.perturb_intensity)
            cleaned = p_res.perturbed_text

        event = None
        now_str = datetime.now().strftime("%H:%M:%S")

        if u_res.has_anomalies or self.enable_perturbation:
            # Overwrite clipboard with clean text (this also strips HTML/RTF representations)
            self._last_content = cleaned
            self.set_clipboard_text(cleaned)

            snippet = (cleaned[:45] + "...") if len(cleaned) > 45 else cleaned
            event = ClipboardEvent(
                timestamp=now_str,
                original_length=len(current_text),
                cleaned_length=len(cleaned),
                invisible_chars_removed=u_res.total_removed,
                spaces_normalized=u_res.normalized_spaces,
                snippet=snippet.replace("\n", " "),
                status="cleaned"
            )
        else:
            self._last_content = current_text

        if event:
            with self._lock:
                self._events.append(event)
                if len(self._events) > 50:
                    self._events.pop(0)
            if self.on_event_callback:
                self.on_event_callback(event)

        return event

    def _loop(self):
        # Initialize last content to current clipboard so we don't trigger on start
        self._last_content = self.get_clipboard_text()
        while self._running:
            try:
                self.check_and_clean_once()
            except Exception:
                pass
            time.sleep(self.poll_interval)

    def start(self):
        """Start the background watcher thread."""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Stop the watcher thread."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None

    @property
    def is_running(self) -> bool:
        return self._running

    def get_recent_events(self) -> List[ClipboardEvent]:
        with self._lock:
            return list(self._events)
