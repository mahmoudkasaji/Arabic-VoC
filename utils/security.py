"""
Security utilities for Arabic VoC platform
Input validation and sanitization with Arabic support
"""

import re
import html
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

class ArabicSecurityValidator:
    """Security validation for Arabic text inputs"""
    
    def __init__(self):
        # Dangerous patterns to detect
        self.xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe[^>]*>.*?</iframe>',
            r'<object[^>]*>.*?</object>',
            r'<embed[^>]*>.*?</embed>',
        ]
        
        # SQL injection patterns
        self.sql_patterns = [
            r'(\bDROP\b|\bDELETE\b|\bINSERT\b|\bUPDATE\b|\bSELECT\b).*?\b(TABLE|FROM|INTO|SET)\b',
            r';\s*--',
            r'\bUNION\b.*?\bSELECT\b',
            r'\'.*?;.*?--',
        ]
        
        # Command injection patterns
        self.command_patterns = [
            r'[;&|`$(){}\[\]]',
            r'\.\./.*',
            r'\/etc\/passwd',
            r'\/bin\/(sh|bash|cmd)',
        ]
        
        # Template injection patterns
        self.template_patterns = [
            r'\{\{.*?\}\}',
            r'\$\{.*?\}',
            r'<%.*?%>',
        ]
        
        # Maximum allowed lengths
        self.max_content_length = 5000
        self.max_field_length = 255
    
    def validate_arabic_input(self, text: str, field_name: str = "content") -> Dict[str, any]:
        """
        Comprehensive validation of Arabic text input
        Returns validation result with sanitized text
        """
        result = {
            "valid": True,
            "sanitized_text": text,
            "warnings": [],
            "errors": []
        }
        
        if not text or not isinstance(text, str):
            result["valid"] = False
            result["errors"].append(f"{field_name} must be a non-empty string")
            return result
        
        # Length validation
        max_length = self.max_content_length if field_name == "content" else self.max_field_length
        if len(text) > max_length:
            result["valid"] = False
            result["errors"].append(f"{field_name} exceeds maximum length of {max_length} characters")
            return result
        
        # Security pattern detection
        security_issues = self._detect_security_patterns(text)
        if security_issues:
            result["warnings"].extend(security_issues)
        
        # Unicode safety check
        unicode_issues = self._check_unicode_safety(text)
        if unicode_issues:
            result["warnings"].extend(unicode_issues)
        
        # Sanitize the text
        result["sanitized_text"] = self._sanitize_text(text)
        
        return result
    
    def _detect_security_patterns(self, text: str) -> List[str]:
        """Detect potentially dangerous patterns in text"""
        issues = []
        text_lower = text.lower()
        
        # XSS detection
        for pattern in self.xss_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE | re.DOTALL):
                issues.append("Potential XSS pattern detected")
                break
        
        # SQL injection detection
        for pattern in self.sql_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                issues.append("Potential SQL injection pattern detected")
                break
        
        # Command injection detection
        for pattern in self.command_patterns:
            if re.search(pattern, text):
                issues.append("Potential command injection pattern detected")
                break
        
        # Template injection detection
        for pattern in self.template_patterns:
            if re.search(pattern, text):
                issues.append("Potential template injection pattern detected")
                break
        
        return issues
    
    def _check_unicode_safety(self, text: str) -> List[str]:
        """Check for Unicode-based security issues"""
        issues = []
        
        # Check for dangerous Unicode characters
        dangerous_chars = [
            '\u0000',  # Null character
            '\u200E',  # Left-to-right mark
            '\u200F',  # Right-to-left mark
            '\u202A',  # Left-to-right embedding
            '\u202B',  # Right-to-left embedding
            '\u202C',  # Pop directional formatting
            '\u202D',  # Left-to-right override
            '\u202E',  # Right-to-left override
            '\uFEFF',  # Byte order mark
        ]
        
        for char in dangerous_chars:
            if char in text:
                issues.append(f"Dangerous Unicode character detected: U+{ord(char):04X}")
        
        # Check for excessive control characters
        control_char_count = sum(1 for char in text if ord(char) < 32 and char not in '\t\n\r')
        if control_char_count > 5:
            issues.append("Excessive control characters detected")
        
        return issues
    
    def _sanitize_text(self, text: str) -> str:
        """Sanitize text while preserving Arabic characters"""
        # HTML escape to prevent XSS
        sanitized = html.escape(text)
        
        # Remove dangerous Unicode characters
        dangerous_chars = ['\u0000', '\uFEFF', '\u202A', '\u202B', '\u202D', '\u202E']
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        # Normalize whitespace but preserve Arabic spacing
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        
        # Remove any remaining control characters except tab, newline, carriage return
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\t\n\r')
        
        return sanitized
    
    def validate_email(self, email: str) -> bool:
        """Validate email address format"""
        if not email:
            return True  # Email is optional
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(email_pattern, email))
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format (supports Arabic countries)"""
        if not phone:
            return True  # Phone is optional
        
        # Allow international format and common Arabic country formats
        phone_pattern = r'^(\+?[1-9]\d{1,14}|0\d{8,10})$'
        cleaned_phone = re.sub(r'[\s\-\(\)]', '', phone)
        return bool(re.match(phone_pattern, cleaned_phone))
    
    def validate_rating(self, rating: Optional[int]) -> bool:
        """Validate rating value"""
        if rating is None:
            return True
        return isinstance(rating, int) and 1 <= rating <= 5

class RateLimiter:
    """Simple rate limiting for API endpoints"""
    
    def __init__(self, max_requests: int = 100, window_minutes: int = 60):
        self.max_requests = max_requests
        self.window_minutes = window_minutes
        self.requests = {}  # IP -> list of timestamps
    
    def is_allowed(self, client_ip: str) -> Tuple[bool, int]:
        """
        Check if request is allowed for client IP
        Returns (allowed, remaining_requests)
        """
        import time
        current_time = time.time()
        window_start = current_time - (self.window_minutes * 60)
        
        if client_ip not in self.requests:
            self.requests[client_ip] = []
        
        # Remove old requests outside the window
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip] 
            if req_time > window_start
        ]
        
        # Check if under limit
        current_count = len(self.requests[client_ip])
        if current_count >= self.max_requests:
            return False, 0
        
        # Add current request
        self.requests[client_ip].append(current_time)
        return True, self.max_requests - current_count - 1
    
    def cleanup_old_entries(self):
        """Clean up old entries to prevent memory leaks"""
        import time
        current_time = time.time()
        window_start = current_time - (self.window_minutes * 60)
        
        for client_ip in list(self.requests.keys()):
            self.requests[client_ip] = [
                req_time for req_time in self.requests[client_ip] 
                if req_time > window_start
            ]
            
            # Remove empty entries
            if not self.requests[client_ip]:
                del self.requests[client_ip]

def validate_feedback_input(content: str, channel: str, customer_email: Optional[str] = None, 
                          customer_phone: Optional[str] = None, rating: Optional[int] = None) -> Dict[str, any]:
    """
    Comprehensive validation for feedback input
    """
    validator = ArabicSecurityValidator()
    
    # Validate content
    content_result = validator.validate_arabic_input(content, "content")
    if not content_result["valid"]:
        return content_result
    
    # Validate channel
    valid_channels = ["email", "phone", "website", "mobile_app", "social_media", 
                     "whatsapp", "sms", "in_person", "survey", "chatbot"]
    if channel not in valid_channels:
        content_result["valid"] = False
        content_result["errors"].append(f"Invalid channel. Must be one of: {', '.join(valid_channels)}")
        return content_result
    
    # Validate optional fields
    if customer_email and not validator.validate_email(customer_email):
        content_result["warnings"].append("Invalid email format")
    
    if customer_phone and not validator.validate_phone(customer_phone):
        content_result["warnings"].append("Invalid phone format")
    
    if not validator.validate_rating(rating):
        content_result["valid"] = False
        content_result["errors"].append("Rating must be between 1 and 5")
    
    return content_result

# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=100, window_minutes=60)

def log_security_event(event_type: str, client_ip: str, details: str):
    """Log security events for monitoring"""
    logger.warning(f"Security Event: {event_type} from {client_ip} - {details}")