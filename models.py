
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from main import Base

class User(Base):
    """User model for Replit Auth integration"""
    __tablename__ = "users"
    
    id = Column(String(100), primary_key=True)  # Replit user ID
    email = Column(String(255), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    profile_image_url = Column(String(500), nullable=True)
    
    # Audit fields
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)
    
    def __repr__(self):
        return f"<User(id='{self.id}', email='{self.email}')>"
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return self.id

class OAuth(Base):
    """OAuth token storage for Replit Auth"""
    __tablename__ = "oauth_tokens"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), ForeignKey("users.id"), nullable=False)
    browser_session_key = Column(String(255), nullable=False)
    provider = Column(String(50), nullable=False)
    token = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    user = relationship("User")

class Feedback(Base):
    """Feedback model for storing user feedback"""
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True)
    content = Column(Text, nullable=False)
    rating = Column(Integer, nullable=True)
    name = Column(String(200), nullable=True)
    user_id = Column(String(100), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    user = relationship("User")
