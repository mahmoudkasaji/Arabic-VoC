"""
Template filters for survey rendering
"""

import json

def from_json(value):
    """Convert JSON string to Python object"""
    if not value:
        return []
    try:
        return json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []

def register_filters(app):
    """Register custom template filters"""
    app.jinja_env.filters['from_json'] = from_json