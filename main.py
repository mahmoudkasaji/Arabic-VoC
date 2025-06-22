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
from asgiref.wsgi import WsgiToAsgi

from utils.database import init_db
from api.feedback import router as feedback_router
from api.analytics import router as analytics_router
from api.auth import router as auth_router

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    logger.info("Initializing database...")
    await init_db()

    # Initialize Arabic database features
    try:
        from utils.database_arabic import init_arabic_database
        await init_arabic_database()
        logger.info("Arabic database features initialized")
    except Exception as e:
        logger.warning(f"Arabic database initialization failed: {e}")

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
app.include_router(auth_router)
try:
    from api.surveys import router as surveys_router
    app.include_router(surveys_router)
except ImportError:
    logger.warning("Surveys router not available")

try:
    from api.feedback_collection import router as feedback_collection_router
    app.include_router(feedback_collection_router)
except ImportError:
    logger.warning("Feedback collection router not available")

try:
    from api.analytics_realtime import router as realtime_analytics_router
    app.include_router(realtime_analytics_router)
except ImportError:
    logger.warning("Real-time analytics router not available")

app.include_router(analytics_router)

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
        {"request": request, "title": "إرسال تعليق"}
    )

@app.get("/dashboard/realtime")
async def realtime_dashboard(request: Request):
    """Real-time analytics dashboard page"""
    return templates.TemplateResponse(
        "dashboard_realtime.html",
        {"request": request, "title": "لوحة التحليلات المباشرة"}
    )

@app.get("/surveys")
async def surveys_page(request: Request):
    """Survey management page"""
    return templates.TemplateResponse(
        "surveys.html", 
        {"request": request, "title": "الاستطلاعات"}
    )

@app.get("/survey-builder")
async def survey_builder_page(request: Request):
    """Survey builder page"""
    return templates.TemplateResponse(
        "survey_builder.html",
        {"request": request, "title": "منشئ الاستطلاعات"}
    )

@app.get("/survey-builder")
async def survey_builder_page(request: Request):
    """Interactive survey builder page"""
    return templates.TemplateResponse(
        "survey_builder.html", 
        {"request": request, "title": "منشئ الاستبيان"}
    )

@app.get("/login")
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "title": "تسجيل الدخول"}
    )

@app.get("/register")
async def register_page(request: Request):
    """Registration page"""
    return templates.TemplateResponse(
        "register.html",
        {"request": request, "title": "إنشاء حساب"}
    )

@app.get("/analytics")
async def analytics_page(request: Request):
    """Analytics dashboard page"""
    return templates.TemplateResponse(
        "analytics.html", 
        {"request": request, "title": "لوحة التحليلات"}
    )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Arabic VoC Platform is running"}

# The FastAPI app is ready for ASGI deployment
# No WSGI wrapper needed - use uvicorn workers for full functionality

if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI app directly with uvicorn for full functionality
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=5000,
        reload=False,
        log_level="info"
    )