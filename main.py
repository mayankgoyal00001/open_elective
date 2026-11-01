"""
Root Entrypoint for Cloud Deployment Platforms (Render, Railway, Heroku)
Delegates to backend/main.py
"""
import os
import sys
from pathlib import Path

# Add backend directory to sys.path so app imports resolve seamlessly
backend_dir = Path(__file__).resolve().parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import the FastAPI application from backend.main
from backend.main import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
