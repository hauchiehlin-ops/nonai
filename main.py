"""
NonAI Root Entrypoint for Vercel and ASGI Servers
"""

from nonai.server import app

__all__ = ["app"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8765, reload=True)
