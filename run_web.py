"""
NonAI Web Application Launcher
Starts the FastAPI server on port 8765.
"""

import sys
import uvicorn
from nonai.server import app

def main():
    port = 8765
    print(f"🚀 NonAI Web 工作台啟動中...")
    print(f"🌐 請在瀏覽器中開啟: http://127.0.0.1:{port}")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")

if __name__ == "__main__":
    main()
