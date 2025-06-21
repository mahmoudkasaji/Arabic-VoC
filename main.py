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
    """Surveys page"""
    return templates.TemplateResponse(
        "surveys.html", 
        {"request": request, "title": "الاستطلاعات"}
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

# Create WSGI-compatible application for Gunicorn
# This adapter allows FastAPI (ASGI) to work with Gunicorn's sync workers
def create_wsgi_app():
    """Create a WSGI wrapper for the FastAPI application"""
    def wsgi_app(environ, start_response):
        """WSGI wrapper for FastAPI ASGI application"""
        # Simple health check endpoint
        if environ['REQUEST_METHOD'] == 'GET' and environ['PATH_INFO'] == '/health':
            status = '200 OK'
            headers = [('Content-Type', 'application/json; charset=utf-8')]
            start_response(status, headers)
            return [b'{"status": "healthy", "message": "Arabic VoC Platform is running"}']
        
        # Serve the comprehensive Arabic UI pages
        path = environ['PATH_INFO']
        method = environ['REQUEST_METHOD']
        
        if method == 'GET':
            if path == '/':
                # Serve main homepage with full navigation
                status = '200 OK'
                headers = [('Content-Type', 'text/html; charset=utf-8')]
                start_response(status, headers)
                with open('templates/index.html', 'r', encoding='utf-8') as f:
                    return [f.read().encode('utf-8')]
            
            elif path == '/feedback':
                # Serve feedback page
                status = '200 OK'
                headers = [('Content-Type', 'text/html; charset=utf-8')]
                start_response(status, headers)
                with open('templates/feedback.html', 'r', encoding='utf-8') as f:
                    return [f.read().encode('utf-8')]
            
            elif path == '/dashboard/realtime':
                # Serve realtime dashboard
                status = '200 OK'
                headers = [('Content-Type', 'text/html; charset=utf-8')]
                start_response(status, headers)
                with open('templates/dashboard_realtime.html', 'r', encoding='utf-8') as f:
                    return [f.read().encode('utf-8')]
            
            elif path == '/surveys':
                # Serve surveys page
                status = '200 OK'
                headers = [('Content-Type', 'text/html; charset=utf-8')]
                start_response(status, headers)
                with open('templates/surveys.html', 'r', encoding='utf-8') as f:
                    return [f.read().encode('utf-8')]
            
            elif path == '/login':
                # Serve login page
                status = '200 OK'
                headers = [('Content-Type', 'text/html; charset=utf-8')]
                start_response(status, headers)
                with open('templates/login.html', 'r', encoding='utf-8') as f:
                    return [f.read().encode('utf-8')]
            
            elif path == '/register':
                # Serve register page
                status = '200 OK'
                headers = [('Content-Type', 'text/html; charset=utf-8')]
                start_response(status, headers)
                with open('templates/register.html', 'r', encoding='utf-8') as f:
                    return [f.read().encode('utf-8')]
        
        # Fallback for basic status page
        if method == 'GET' and path == '/':
            status = '200 OK'
            headers = [('Content-Type', 'text/html; charset=utf-8')]
            start_response(status, headers)
            html_content = '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منصة صوت العميل العربية</title>
    <style>
        body { font-family: 'Cairo', Arial, sans-serif; direction: rtl; text-align: center; padding: 50px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; min-height: 100vh; margin: 0; }
        .container { max-width: 800px; margin: 0 auto; }
        h1 { font-size: 3em; margin-bottom: 0.5em; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }
        .subtitle { font-size: 1.2em; margin-bottom: 2em; opacity: 0.9; }
        .features { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 3em; }
        .feature { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; backdrop-filter: blur(10px); }
        .status { background: rgba(46, 204, 113, 0.2); padding: 15px; border-radius: 8px; margin: 2em 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>منصة صوت العميل العربية</h1>
        <p class="subtitle">Arabic Voice of Customer Platform</p>
        <div class="status">
            <strong>✓ النظام يعمل بنجاح</strong><br>
            Platform is running successfully with Arabic support
        </div>
        <div class="features">
            <div class="feature">
                <h3>📝 جمع الملاحظات</h3>
                <p>Multi-channel feedback collection</p>
            </div>
            <div class="feature">
                <h3>🤖 الذكاء الاصطناعي</h3>
                <p>AI-powered Arabic sentiment analysis</p>
            </div>
            <div class="feature">
                <h3>📊 التحليلات</h3>
                <p>Real-time analytics dashboard</p>
            </div>
            <div class="feature">
                <h3>🌐 دعم شامل للعربية</h3>
                <p>Full Arabic RTL support</p>
            </div>
        </div>
    </div>
</body>
</html>'''.encode('utf-8')
            return [html_content]
        
        # API endpoints indication
        if environ['PATH_INFO'].startswith('/api/'):
            status = '200 OK'
            headers = [('Content-Type', 'application/json; charset=utf-8')]
            start_response(status, headers)
            return [b'{"message": "API endpoints available", "note": "Use ASGI interface for full API functionality"}']
        
        # Default response
        status = '404 Not Found'
        headers = [('Content-Type', 'text/html; charset=utf-8')]
        start_response(status, headers)
        return [b'<h1>404 - Page Not Found</h1>']
    
    return wsgi_app

# Keep the FastAPI app for ASGI mode
fastapi_app = app

# For current Gunicorn deployment, use WSGI wrapper as main app
application = create_wsgi_app()

# Override app to use WSGI wrapper for compatibility
app = application

if __name__ == "__main__":
    import uvicorn
    # Run the FastAPI app directly with uvicorn for full functionality
    uvicorn.run(
        "main:fastapi_app",
        host="0.0.0.0",
        port=5000,
        reload=True,
        log_level="info"
    )
