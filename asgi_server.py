#!/usr/bin/env python3
"""
ASGI server configuration for Arabic Voice of Customer platform
Properly handles FastAPI with uvicorn workers
"""

import os
import subprocess
import sys

def start_asgi_server():
    """Start FastAPI application with proper ASGI configuration"""
    cmd = [
        sys.executable, "-m", "gunicorn",
        "main:app",
        "--worker-class", "uvicorn.workers.UvicornWorker",
        "--bind", "0.0.0.0:5000",
        "--workers", "1",
        "--timeout", "120",
        "--log-level", "info",
        "--access-logfile", "-"
    ]
    
    print("Starting Arabic VoC platform with ASGI server...")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        process = subprocess.Popen(cmd, cwd="/home/runner/workspace")
        process.wait()
    except KeyboardInterrupt:
        print("Server stopped")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    start_asgi_server()