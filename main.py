
"""
Arabic Voice of Customer Platform - Main Application
Optimized for performance and clarity
"""

import asyncio
import logging
from functools import lru_cache
from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
import os
import time

# Configure logging for better debugging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app with optimized configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'arabic-voc-platform-2024')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file upload

# Enable CORS for API endpoints
CORS(app, origins=['*'])

# Performance monitoring middleware
@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    if hasattr(request, 'start_time'):
        duration = time.time() - request.start_time
        if duration > 2.0:  # Log slow requests
            logger.warning(f"Slow request: {request.endpoint} took {duration:.2f}s")
    return response

# Cache frequently used data
@lru_cache(maxsize=100)
def get_cached_dashboard_data():
    """Cache dashboard data for better performance"""
    try:
        from utils.dashboard_demo_data import get_dashboard_metrics
        return get_dashboard_metrics()
    except Exception as e:
        logger.error(f"Dashboard data error: {e}")
        return {"error": "Data temporarily unavailable"}

# Import API routes
from api.feedback import feedback_bp
from api.analytics import analytics_bp
from api.surveys import surveys_bp
from api.executive_dashboard import executive_bp

# Register API blueprints
app.register_blueprint(feedback_bp, url_prefix='/api/feedback')
app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
app.register_blueprint(surveys_bp, url_prefix='/api/surveys')
app.register_blueprint(executive_bp, url_prefix='/api/executive')

# Main routes
@app.route('/')
def index():
    """Homepage with performance optimization"""
    try:
        # Get cached data instead of fresh DB query
        dashboard_data = get_cached_dashboard_data()
        return render_template('index.html', 
                             dashboard_data=dashboard_data,
                             page_load_time=time.time())
    except Exception as e:
        logger.error(f"Homepage error: {e}")
        return render_template('index.html', 
                             dashboard_data={"error": "Loading..."},
                             page_load_time=time.time())

@app.route('/health')
def health_check():
    """Simple health check for monitoring"""
    return jsonify({
        "status": "healthy",
        "timestamp": time.time(),
        "version": "2.0.0"
    })

@app.route('/surveys')
def surveys():
    """Survey management page"""
    return render_template('surveys.html')

@app.route('/analytics')
def analytics():
    """Analytics dashboard"""
    return render_template('analytics_arabic.html')

@app.route('/executive')
def executive_dashboard():
    """Executive dashboard with cached data"""
    try:
        dashboard_data = get_cached_dashboard_data()
        return render_template('executive_dashboard.html', 
                             data=dashboard_data)
    except Exception as e:
        logger.error(f"Executive dashboard error: {e}")
        return render_template('executive_dashboard.html', 
                             data={"error": "Data loading..."})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "الصفحة غير موجودة", "code": 404}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return jsonify({"error": "خطأ داخلي في الخادم", "code": 500}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Arabic VoC Platform on port {port}")
    logger.info(f"Debug mode: {debug_mode}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode,
        threaded=True  # Enable threading for better performance
    )
