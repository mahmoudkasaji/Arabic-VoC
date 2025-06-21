#!/usr/bin/env python3
"""
Simple server runner for the Arabic Voice of Customer platform
Uses uvicorn to properly serve the FastAPI application
"""

import uvicorn
import logging

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Run the FastAPI application with uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=False,
        log_level="info",
        access_log=True
    )