#!/usr/bin/env python3
"""
Uvicorn startup script for Arabic Voice of Customer FastAPI platform
Configured specifically for Replit environment with proper Arabic text encoding
"""

import uvicorn
import os
import logging
import sys

def setup_environment():
    """Configure environment for Arabic text processing"""
    # Ensure UTF-8 encoding for Arabic text
    os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    os.environ.setdefault('LC_ALL', 'C.UTF-8')
    os.environ.setdefault('LANG', 'C.UTF-8')
    
    # Configure logging for Arabic text
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def start_server():
    """Start FastAPI app with uvicorn for Replit"""
    setup_environment()
    
    # Replit-specific configuration
    host = "0.0.0.0"  # Required for Replit external access
    port = 8000  # Use different port to avoid Gunicorn conflicts
    
    print(f"Starting Arabic Voice of Customer Platform on {host}:{port}")
    print("FastAPI app with Arabic RTL support and OpenAI integration")
    
    # Start uvicorn with optimal settings for Replit
    uvicorn.run(
        "main:app",  # FastAPI app instance
        host=host,
        port=port,
        reload=False,  # Disable reload in production
        log_level="info",
        access_log=True,
        workers=1,  # Single worker for Replit
        loop="asyncio",
        http="httptools",
        lifespan="on"
    )

if __name__ == "__main__":
    try:
        start_server()
    except KeyboardInterrupt:
        print("\nServer shutdown requested")
    except Exception as e:
        print(f"Server startup error: {e}")
        sys.exit(1)