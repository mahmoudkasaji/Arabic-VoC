#!/usr/bin/env python3
"""
ASGI application starter for Arabic Voice of Customer platform
"""

import asyncio
import uvicorn
from main import app

async def main():
    """Start the FastAPI application with proper ASGI server"""
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=5000,
        log_level="info",
        access_log=True,
        loop="asyncio"
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())