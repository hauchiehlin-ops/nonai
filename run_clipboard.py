"""
NonAI Clipboard Watcher Daemon (Scheme C)
Standalone background runner for intercepting clipboard copy actions.
"""

import sys
from nonai.cli import main

if __name__ == "__main__":
    # Simulate nonai watch
    sys.argv = ["cli.py", "watch"] + sys.argv[1:]
    main()
