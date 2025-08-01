"""
Standardized response handlers for common operations
Consolidates repetitive response patterns across the application
"""

from flask import jsonify
from typing import Any, Dict, Optional
from utils.common import standardize_success_response, standardize_error_response

def success_json_response(data: Any = None, message: str = "Success", status_code: int = 200):
    """Return standardized JSON success response"""
    return jsonify(standardize_success_response(data, message)), status_code

def error_json_response(error: Exception, context: str = "operation", status_code: int = 500):
    """Return standardized JSON error response"""
    return jsonify(standardize_error_response(error, context)), status_code

def validation_error_response(message: str, status_code: int = 400):
    """Return validation error response"""
    return jsonify({
        'success': False,
        'error': message,
        'type': 'validation_error'
    }), status_code

def not_found_response(resource: str = "Resource"):
    """Return standardized not found response"""
    return jsonify({
        'success': False,
        'error': f'{resource} not found',
        'type': 'not_found'
    }), 404

def unauthorized_response(message: str = "Unauthorized"):
    """Return standardized unauthorized response"""
    return jsonify({
        'success': False,
        'error': message,
        'type': 'unauthorized'
    }), 401