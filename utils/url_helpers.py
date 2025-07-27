"""
URL Helper Functions
Utility functions for generating correct URLs in different environments
"""

import os
from flask import request

def get_base_url():
    """Get the correct base URL for the current environment"""
    
    # Try to get from Replit environment first
    replit_domain = os.getenv('REPLIT_DEV_DOMAIN')
    if replit_domain:
        return f"https://{replit_domain}"
    
    # Try to get from REPLIT_DOMAINS (comma-separated)
    replit_domains = os.getenv('REPLIT_DOMAINS')
    if replit_domains:
        first_domain = replit_domains.split(',')[0].strip()
        return f"https://{first_domain}"
    
    # Fallback to Flask request context if available
    try:
        if request:
            return f"{request.scheme}://{request.host}"
    except RuntimeError:
        # Outside request context
        pass
    
    # Final fallback (for local development)
    return "http://localhost:5000"

def get_survey_public_url(short_id):
    """Generate a complete public URL for a survey"""
    base_url = get_base_url()
    return f"{base_url}/s/{short_id}"

def get_survey_full_url(uuid):
    """Generate a complete URL for a survey using UUID"""
    base_url = get_base_url()
    return f"{base_url}/survey/{uuid}"