"""
NonAI Clipboard Watcher Daemon (Scheme C)
Standalone background runner for intercepting clipboard copy actions.
"""

import os
import sys

# Auto-detect and switch to local virtual environment (.venv) if available
if sys.prefix == sys.base_prefix:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_python = (
        os.path.join(script_dir, ".venv", "Scripts", "python.exe")
        if sys.platform == "win32"
        else os.path.join(script_dir, ".venv", "bin", "python3")
    )
    if os.path.exists(venv_python):
        os.execv(venv_python, [venv_python] + sys.argv)

from nonai.cli import main

if __name__ == "__main__":
    # Simulate nonai watch
    sys.argv = ["cli.py", "watch"] + sys.argv[1:]
    main()
