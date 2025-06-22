"""
Main entry point for Arabic Voice of Customer Platform
Unified application startup with proper configuration
"""

import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

from app.config import get_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class Base(DeclarativeBase):
    pass

# Initialize extensions
db = SQLAlchemy(model_class=Base)

def create_app():
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    config = get_config()
    app.config.from_object(config)
    
    # Configure for proxy (needed for Replit)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    
    # Initialize database
    db.init_app(app)
    
    # Register blueprints
    register_blueprints(app)
    
    # Create tables
    with app.app_context():
        # Import models to ensure tables are created
        from app.models import feedback, analytics, auth
        db.create_all()
        logger.info("Database tables created successfully")
    
    return app

def register_blueprints(app):
    """Register all application blueprints"""
    from app.api.feedback import bp as feedback_bp
    from app.api.analytics import bp as analytics_bp
    from app.api.auth import bp as auth_bp
    from app.web.routes import bp as web_bp
    
    app.register_blueprint(feedback_bp, url_prefix='/api')
    app.register_blueprint(analytics_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')
    app.register_blueprint(web_bp)

# Create application instance
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=app.config.get('DEBUG', False))