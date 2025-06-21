#!/usr/bin/env python3
"""
Start the Arabic VoC platform with uvicorn for full FastAPI functionality
"""

import uvicorn
import os

if __name__ == "__main__":
    # Configure for Arabic text support
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    
    # Start the FastAPI application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        reload_dirs=[".", "templates", "static"],
        access_log=True
    )