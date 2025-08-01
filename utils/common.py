"""
Common utilities consolidating functionality from multiple files
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def standardize_error_response(error: Exception, context: str = "operation") -> Dict[str, Any]:
    """Standardize error responses across the application"""
    logger.error(f"Error in {context}: {error}")
    return {
        'success': False,
        'error': str(error),
        'context': context,
        'timestamp': datetime.utcnow().isoformat()
    }

def standardize_success_response(data: Any = None, message: str = "Success") -> Dict[str, Any]:
    """Standardize success responses across the application"""
    response = {
        'success': True,
        'message': message,
        'timestamp': datetime.utcnow().isoformat()
    }
    if data is not None:
        response['data'] = data
    return response

def validate_required_fields(data: Dict[str, Any], required_fields: list) -> Optional[str]:
    """Validate required fields in request data"""
    missing_fields = [field for field in required_fields if not data.get(field)]
    if missing_fields:
        return f"Missing required fields: {', '.join(missing_fields)}"
    return None

def safe_get_attribute(obj, attr: str, default=None):
    """Safely get attribute from object with default fallback"""
    try:
        return getattr(obj, attr, default)
    except AttributeError:
        return default

def format_arabic_text(text: str) -> str:
    """Simple Arabic text formatting utility"""
    if not text:
        return ""
    
    # Basic cleanup
    text = text.strip()
    
    # Remove extra spaces
    import re
    text = re.sub(r'\s+', ' ', text)
    
    return text