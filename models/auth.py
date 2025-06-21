"""
Authentication models for Arabic VoC platform
User, Organization, and authentication-related models with Arabic support
"""

from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import hashlib
import secrets

Base = declarative_base()

class UserRole(str, enum.Enum):
    """User roles in the system"""
    ADMIN = "admin"
    MANAGER = "manager"
    ANALYST = "analyst"
    VIEWER = "viewer"

class User(Base):
    """
    User model with comprehensive Arabic name support
    Supports both English and Arabic names with proper encoding
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication fields
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    role = Column(String(20), default=UserRole.VIEWER, nullable=False)
    
    # Arabic name support
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    first_name_ar = Column(Text, nullable=True, comment="Arabic first name with full UTF-8 support")
    last_name_ar = Column(Text, nullable=True, comment="Arabic last name with full UTF-8 support")
    display_name_ar = Column(Text, nullable=True, comment="Preferred Arabic display name")
    
    # Profile information
    phone = Column(String(20), nullable=True)
    language_preference = Column(String(10), default="ar", nullable=False)
    timezone = Column(String(50), default="Asia/Riyadh", nullable=False)
    
    # Organization relationship
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=True)
    organization = relationship("Organization", back_populates="users")
    
    # Audit fields
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0, nullable=False)
    
    # Security fields
    failed_login_attempts = Column(Integer, default=0, nullable=False)
    locked_until = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    @property
    def full_name(self) -> str:
        """Get full name in preferred language"""
        if self.language_preference == "ar" and self.first_name_ar and self.last_name_ar:
            return f"{self.first_name_ar} {self.last_name_ar}"
        elif self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    @property
    def display_name(self) -> str:
        """Get display name in preferred language"""
        if self.display_name_ar and self.language_preference == "ar":
            return self.display_name_ar
        return self.full_name
    
    def is_locked(self) -> bool:
        """Check if user account is locked"""
        if self.locked_until:
            return datetime.utcnow() < self.locked_until
        return False
    
    def can_login(self) -> bool:
        """Check if user can login"""
        return self.is_active and self.is_verified and not self.is_locked()

class Organization(Base):
    """
    Organization model with Arabic support
    Supports bilingual organization information
    """
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic information
    name = Column(String(200), nullable=False)
    name_ar = Column(Text, nullable=True, comment="Arabic organization name")
    description = Column(Text, nullable=True)
    description_ar = Column(Text, nullable=True, comment="Arabic organization description")
    
    # Contact information
    email = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    website = Column(String(255), nullable=True)
    
    # Address with Arabic support
    address = Column(Text, nullable=True)
    address_ar = Column(Text, nullable=True, comment="Arabic address")
    city = Column(String(100), nullable=True)
    city_ar = Column(String(100), nullable=True, comment="Arabic city name")
    country = Column(String(100), nullable=True)
    country_ar = Column(String(100), nullable=True, comment="Arabic country name")
    
    # Settings
    default_language = Column(String(10), default="ar", nullable=False)
    timezone = Column(String(50), default="Asia/Riyadh", nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Subscription and limits
    plan_type = Column(String(50), default="basic", nullable=False)
    max_users = Column(Integer, default=10, nullable=False)
    max_surveys = Column(Integer, default=100, nullable=False)
    max_responses_per_month = Column(Integer, default=1000, nullable=False)
    
    # Audit fields
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    users = relationship("User", back_populates="organization")
    surveys = relationship("Survey", back_populates="organization")
    
    def __repr__(self):
        return f"<Organization(id={self.id}, name='{self.name}')>"
    
    @property
    def display_name(self) -> str:
        """Get organization name in default language"""
        if self.default_language == "ar" and self.name_ar:
            return self.name_ar
        return self.name

class RefreshToken(Base):
    """
    Refresh token model for JWT authentication
    """
    __tablename__ = "refresh_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<RefreshToken(id={self.id}, user_id={self.user_id})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired"""
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Check if token is valid"""
        return not self.is_revoked and not self.is_expired
    
    @classmethod
    def generate_token(cls) -> str:
        """Generate a secure random token"""
        return secrets.token_urlsafe(32)

class UserSession(Base):
    """
    User session tracking for security and analytics
    """
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)  # Support IPv6
    user_agent = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    last_activity = Column(DateTime, default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<UserSession(id={self.id}, user_id={self.user_id})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.utcnow()

# Import Survey and related models
from models.survey import Survey