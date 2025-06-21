
"""
FastAPI Arabic-first Voice of Customer Platform
Main application entry point with proper Arabic support and CORS configuration
"""

from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from datetime import datetime
import os
import logging

# Import database and models
from utils.database import get_db_session
from models_unified import Base
from sqlalchemy.ext.asyncio import create_async_engine

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Database setup
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")

# Create async engine for database operations
engine = create_async_engine(DATABASE_URL, echo=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

# Create FastAPI app
app = FastAPI(
    title="Arabic Voice of Customer Platform",
    description="Real-time feedback analysis platform with Arabic language support",
    version="1.0.0",
    lifespan=lifespan
)

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Simple user management
class User:
    def __init__(self, id: str, email: str = None, first_name: str = None):
        self.id = id
        self.email = email
        self.first_name = first_name
        self.is_authenticated = True

def get_current_user() -> User:
    """Get current user - returns None for anonymous access"""
    return None

@app.get("/")
async def root(request: Request, user: User = Depends(get_current_user)):
    """Main page with Arabic RTL layout"""
    if user and user.is_authenticated:
        return templates.TemplateResponse("feedback.html", {"request": request, "user": user})
    else:
        return templates.TemplateResponse("landing.html", {"request": request, "user": None})

@app.get("/feedback")
async def feedback_page(request: Request, user: User = Depends(get_current_user)):
    """Feedback submission page"""
    return templates.TemplateResponse("feedback.html", {"request": request, "user": user})

@app.get("/dashboard/realtime")
async def realtime_dashboard(request: Request, user: User = Depends(get_current_user)):
    """Real-time analytics dashboard page"""
    return templates.TemplateResponse("dashboard_realtime.html", {"request": request, "user": user})

@app.get("/surveys")
async def surveys_page(request: Request, user: User = Depends(get_current_user)):
    """Surveys page"""
    return templates.TemplateResponse("surveys.html", {"request": request, "user": user})

@app.get("/login")
async def login_page(request: Request):
    """Login page redirect"""
    return RedirectResponse(url="/")

@app.get("/register")
async def register_page(request: Request):
    """Registration page redirect"""
    return RedirectResponse(url="/")

@app.get("/analytics")
async def analytics_page(request: Request, user: User = Depends(get_current_user)):
    """Analytics dashboard page"""
    return templates.TemplateResponse("analytics.html", {"request": request, "user": user})

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

def create_wsgi_app():
    """Create a WSGI wrapper for the FastAPI application"""
    def wsgi_app(environ, start_response):
        """WSGI wrapper for FastAPI ASGI application"""
        from asgiref.wsgi import WsgiToAsgi
        asgi_app = WsgiToAsgi(app)
        return asgi_app(environ, start_response)
    return wsgi_app
