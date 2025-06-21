"""
FastAPI Arabic-first Voice of Customer Platform
Main application entry point with proper Arabic support and CORS configuration
"""

import os
import logging
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from utils.database import init_db
from api.feedback import router as feedback_router
from api.analytics import router as analytics_router

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    logger.info("Initializing database...")
    await init_db()
    logger.info("Database initialized successfully")
    yield

# Initialize FastAPI app with Arabic locale support
app = FastAPI(
    title="Arabic Voice of Customer Platform",
    description="Multi-channel feedback processing platform with Arabic-first design",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for Arabic domains and RTL support
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5000",
        "https://*.replit.dev",
        "https://*.replit.app",
        # Arabic domain patterns
        "https://*.sa",
        "https://*.ae",
        "https://*.eg",
        "https://*.ma",
        "https://*.jo",
        "https://*.lb",
        "https://*.sy",
        "https://*.iq",
        "https://*.ye",
        "https://*.om",
        "https://*.qa",
        "https://*.kw",
        "https://*.bh"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*", "Content-Language", "Accept-Language"],
)

# Mount static files with UTF-8 support
app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure Jinja2 templates with Arabic support
templates = Jinja2Templates(directory="templates")

# Include API routers
app.include_router(feedback_router, prefix="/api/feedback", tags=["feedback"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])

@app.get("/")
async def root(request: Request):
    """Main page with Arabic RTL layout"""
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request,
            "lang": "ar",
            "dir": "rtl"
        }
    )

@app.get("/feedback")
async def feedback_page(request: Request):
    """Feedback submission page"""
    return templates.TemplateResponse(
        "feedback.html",
        {
            "request": request,
            "lang": "ar",
            "dir": "rtl"
        }
    )

@app.get("/analytics")
async def analytics_page(request: Request):
    """Analytics dashboard page"""
    return templates.TemplateResponse(
        "analytics.html",
        {
            "request": request,
            "lang": "ar",
            "dir": "rtl"
        }
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Arabic VoC Platform is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="debug"
    )
