#!/usr/bin/env python3
"""
Direct uvicorn server for Arabic Voice of Customer platform
"""

import uvicorn
import logging
import signal
import sys

def signal_handler(sig, frame):
    print('Server shutting down...')
    sys.exit(0)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logging.basicConfig(level=logging.INFO)
    print("Starting Arabic Voice of Customer platform...")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=False,
        log_level="info",
        access_log=True,
        workers=1
    )