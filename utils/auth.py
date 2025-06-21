"""
Authentication utilities for Arabic VoC platform
JWT token management, password hashing, and Arabic name validation
"""

import os
import jwt
import bcrypt
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import secrets
import logging

logger = logging.getLogger(__name__)

# JWT Configuration
JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", secrets.token_urlsafe(32))
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 30

security = HTTPBearer()

class ArabicAuthManager:
    """Authentication manager with Arabic name support"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    @staticmethod
    def validate_arabic_name(name: str) -> bool:
        """Validate Arabic name format"""
        if not name or len(name.strip()) == 0:
            return False
        
        # Arabic characters range (basic Arabic block)
        arabic_pattern = r'^[\u0621-\u064A\u0660-\u0669\s]+$'
        
        # Allow Arabic characters, Arabic numbers, and spaces
        return bool(re.match(arabic_pattern, name.strip()))
    
    @staticmethod
    def validate_username(username: str) -> bool:
        """Validate username format"""
        if not username or len(username) < 3 or len(username) > 50:
            return False
        
        # Allow alphanumeric, underscore, hyphen, and Arabic characters
        pattern = r'^[\w\u0621-\u064A-]+$'
        return bool(re.match(pattern, username))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        if not email:
            return False
        
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_password_strength(password: str) -> Dict[str, Any]:
        """Validate password strength and return detailed feedback"""
        if not password:
            return {"valid": False, "errors": ["Password is required"]}
        
        errors = []
        score = 0
        
        # Length check
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        else:
            score += 1
        
        # Uppercase letter
        if not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        else:
            score += 1
        
        # Lowercase letter
        if not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        else:
            score += 1
        
        # Digit
        if not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        else:
            score += 1
        
        # Special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("Password must contain at least one special character")
        else:
            score += 1
        
        # Common password check
        common_passwords = ["password", "123456", "qwerty", "admin", "user"]
        if password.lower() in common_passwords:
            errors.append("Password is too common")
            score -= 1
        
        strength_levels = ["Very Weak", "Weak", "Fair", "Good", "Strong"]
        strength = strength_levels[min(score, 4)]
        
        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "score": score,
            "strength": strength
        }
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        
        try:
            encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create access token"
            )
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        try:
            encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating refresh token: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not create refresh token"
            )
    
    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            
            # Check token type
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected {token_type}",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            # Check expiration
            exp_timestamp = payload.get("exp")
            if exp_timestamp and datetime.utcnow() > datetime.fromtimestamp(exp_timestamp):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token has expired",
                    headers={"WWW-Authenticate": "Bearer"}
                )
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"}
            )
        except jwt.JWTError as e:
            logger.error(f"JWT verification error: {e}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
    
    @staticmethod
    def extract_user_data_for_token(user) -> Dict[str, Any]:
        """Extract user data for JWT token payload"""
        return {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "organization_id": user.organization_id,
            "language_preference": user.language_preference,
            "full_name": user.full_name,
            "display_name": user.display_name
        }

class ArabicNameValidator:
    """Specialized validator for Arabic names and text"""
    
    @staticmethod
    def is_arabic_text(text: str) -> bool:
        """Check if text contains Arabic characters"""
        if not text:
            return False
        
        arabic_chars = 0
        total_chars = len([c for c in text if c.isalpha()])
        
        for char in text:
            if '\u0621' <= char <= '\u064A' or '\u0660' <= char <= '\u0669':
                arabic_chars += 1
        
        # Consider text Arabic if more than 70% of alphabetic characters are Arabic
        return total_chars > 0 and (arabic_chars / total_chars) > 0.7
    
    @staticmethod
    def normalize_arabic_name(name: str) -> str:
        """Normalize Arabic name for consistent storage"""
        if not name:
            return ""
        
        # Remove extra whitespace
        normalized = ' '.join(name.split())
        
        # Remove diacritics (optional, based on requirements)
        diacritics = '\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652'
        for diacritic in diacritics:
            normalized = normalized.replace(diacritic, '')
        
        return normalized.strip()
    
    @staticmethod
    def validate_arabic_name_length(name: str) -> bool:
        """Validate Arabic name length (considering Arabic character width)"""
        if not name:
            return False
        
        # Arabic names typically range from 2-50 characters
        clean_name = name.strip()
        return 2 <= len(clean_name) <= 50
    
    @staticmethod
    def suggest_arabic_display_name(first_name_ar: str, last_name_ar: str) -> str:
        """Suggest a display name based on Arabic names"""
        if not first_name_ar and not last_name_ar:
            return ""
        
        if first_name_ar and last_name_ar:
            return f"{first_name_ar} {last_name_ar}"
        
        return first_name_ar or last_name_ar

# Global authentication manager
auth_manager = ArabicAuthManager()
name_validator = ArabicNameValidator()

def generate_api_key() -> str:
    """Generate secure API key for integrations"""
    return f"avoc_{secrets.token_urlsafe(32)}"

def validate_api_key(api_key: str) -> bool:
    """Validate API key format"""
    return api_key and api_key.startswith("avoc_") and len(api_key) > 10