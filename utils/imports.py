"""
Simplified import utilities to reduce code duplication
"""

def safe_import_replit_auth():
    """Safely import Replit Auth with fallback"""
    try:
        from replit_auth import require_login, make_replit_blueprint
        return require_login, make_replit_blueprint
    except ImportError:
        # Fallback decorator if Replit Auth is not available
        def require_login(f):
            return f
        def make_replit_blueprint():
            return None
        return require_login, None

def get_template_helpers():
    """Get template helper functions"""
    try:
        from utils.template_helpers import get_success_message, get_error_message
        return get_success_message, get_error_message
    except ImportError:
        def get_success_message(key):
            return "Operation completed successfully"
        def get_error_message(key):
            return "An error occurred"
        return get_success_message, get_error_message