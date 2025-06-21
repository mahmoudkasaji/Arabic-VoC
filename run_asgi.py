#!/usr/bin/env python3
"""
Standalone ASGI server for Arabic Voice of Customer platform
Bypasses workflow conflicts by running uvicorn directly
"""

import subprocess
import sys
import time
import os

def kill_conflicting_processes():
    """Kill any conflicting server processes"""
    try:
        subprocess.run(["pkill", "-f", "gunicorn"], capture_output=True)
        subprocess.run(["pkill", "-f", "uvicorn"], capture_output=True)
        time.sleep(2)
    except:
        pass

def start_asgi_server():
    """Start FastAPI with proper ASGI server"""
    kill_conflicting_processes()
    
    # Use the minimal server that works
    cmd = [
        sys.executable,
        "-c",
        """
import uvicorn
from minimal_server import app

if __name__ == '__main__':
    uvicorn.run(
        app,
        host='0.0.0.0',
        port=5000,
        log_level='info',
        access_log=True
    )
        """
    ]
    
    print("Starting Arabic VoC Platform with ASGI server...")
    
    # Run in background
    process = subprocess.Popen(cmd, cwd="/home/runner/workspace")
    return process

if __name__ == "__main__":
    try:
        server_process = start_asgi_server()
        print(f"Server started with PID: {server_process.pid}")
        print("Arabic Voice of Customer Platform should be available at http://localhost:5000")
        
        # Keep the script running
        server_process.wait()
    except KeyboardInterrupt:
        print("Shutting down server...")
    except Exception as e:
        print(f"Error: {e}")