"""
NonAI Root Entrypoint for Vercel and ASGI Servers
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

from nonai.server import app

__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8765, reload=True)
