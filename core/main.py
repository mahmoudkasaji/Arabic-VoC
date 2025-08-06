
"""
Arabic Voice of Customer Platform - Main Application Entry Point
Imports the main Flask app from app.py for WSGI compatibility
"""

from .app import app

# Import all routes and ensure database tables are created
with app.app_context():
    from .app import db
    db.create_all()

# All routes are defined in app.py

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"Starting Arabic VoC Platform on port {port}")
    print(f"Debug mode: {debug_mode}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug_mode,
        threaded=True
    )
