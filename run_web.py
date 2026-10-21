"""
NonAI Web Application Launcher
Starts the FastAPI server on port 8765.
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

try:
    import uvicorn
    from nonai.server import app
except ModuleNotFoundError as err:
    print(f"⚠️ 偵測到環境中缺少必要套件: {err.name}")
    print("📦 正在嘗試建立虛擬環境並安裝 requirements.txt...")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    venv_dir = os.path.join(script_dir, ".venv")
    try:
        import subprocess
        if not os.path.exists(venv_dir):
            subprocess.check_call([sys.executable, "-m", "venv", venv_dir])
        venv_python = (
            os.path.join(venv_dir, "Scripts", "python.exe")
            if sys.platform == "win32"
            else os.path.join(venv_dir, "bin", "python3")
        )
        req_file = os.path.join(script_dir, "requirements.txt")
        subprocess.check_call([venv_python, "-m", "pip", "install", "-r", req_file])
        print("✅ 依賴套件安裝成功！正在啟動 Web 服務...")
        os.execv(venv_python, [venv_python] + sys.argv)
    except Exception as e:
        print(f"❌ 自動安裝失敗: {e}")
        print("💡 請手動執行以下指令安裝依賴套件：")
        print(f"   cd {script_dir} && source .venv/bin/activate && pip install -r requirements.txt")
        sys.exit(1)

def main():
    port = 8765
    print(f"🚀 NonAI Web 工作台啟動中...")
    print(f"🌐 請在瀏覽器中開啟: http://127.0.0.1:{port}")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")

if __name__ == "__main__":
    main()
