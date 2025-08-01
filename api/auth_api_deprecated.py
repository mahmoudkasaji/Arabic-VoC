"""
Authentication API endpoints for Arabic VoC platform
Handles user registration, login, and profile management with Arabic name support
"""

import logging
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field, validator
from typing import Optional

from models.auth import User, Organization, RefreshToken, UserSession
from utils.database_arabic import get_arabic_db_session
from utils.auth import auth_manager, name_validator
from utils.security import rate_limiter, log_security_event

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["authentication"])
security = HTTPBearer()

# Pydantic models for API requests/responses
class UserRegister(BaseModel):
    """User registration model with Arabic name support"""
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: str = Field(..., description="Email address")
    password: str = Field(..., min_length=8, description="Password")
    
    # Optional names in English
    first_name: Optional[str] = Field(None, max_length=100, description="First name in English")
    last_name: Optional[str] = Field(None, max_length=100, description="Last name in English")
    
    # Arabic names
    first_name_ar: Optional[str] = Field(None, description="First name in Arabic")
    last_name_ar: Optional[str] = Field(None, description="Last name in Arabic")
    display_name_ar: Optional[str] = Field(None, description="Preferred Arabic display name")
    
    # Optional profile information
    phone: Optional[str] = Field(None, max_length=20, description="Phone number")
    language_preference: str = Field("ar", description="Preferred language (ar/en)")
    timezone: str = Field("Asia/Riyadh", description="User timezone")
    
    @validator('username')
    def validate_username(cls, v):
        if not auth_manager.validate_username(v):
            raise ValueError('Username must be 3-50 characters and contain only letters, numbers, underscore, or hyphen')
        return v
    
    @validator('email')
    def validate_email(cls, v):
        if not auth_manager.validate_email(v):
            raise ValueError('Invalid email format')
        return v
    
    @validator('password')
    def validate_password(cls, v):
        validation = auth_manager.validate_password_strength(v)
        if not validation["valid"]:
            raise ValueError(f'Password validation failed: {", ".join(validation["errors"])}')
        return v
    
    @validator('first_name_ar')
    def validate_first_name_ar(cls, v):
        if v and not name_validator.validate_arabic_name_length(v):
            raise ValueError('Arabic first name must be 2-50 characters')
        if v and not name_validator.is_arabic_text(v):
            raise ValueError('First name must contain Arabic characters')
        return name_validator.normalize_arabic_name(v) if v else v
    
    @validator('last_name_ar')
    def validate_last_name_ar(cls, v):
        if v and not name_validator.validate_arabic_name_length(v):
            raise ValueError('Arabic last name must be 2-50 characters')
        if v and not name_validator.is_arabic_text(v):
            raise ValueError('Last name must contain Arabic characters')
        return name_validator.normalize_arabic_name(v) if v else v

class UserLogin(BaseModel):
    """User login model"""
    username_or_email: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")
    remember_me: bool = Field(False, description="Remember login for longer period")

class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict

class UserProfile(BaseModel):
    """User profile response model"""
    id: int
    username: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    first_name_ar: Optional[str]
    last_name_ar: Optional[str]
    display_name_ar: Optional[str]
    full_name: str
    display_name: str
    phone: Optional[str]
    language_preference: str
    timezone: str
    role: str
    is_active: bool
    is_verified: bool
    organization: Optional[dict]
    created_at: datetime
    last_login: Optional[datetime]

class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str

# Authentication dependency
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_arabic_db_session)
) -> User:
    """Get current authenticated user"""
    try:
        token = credentials.credentials
        payload = auth_manager.verify_token(token, "access")
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get user from database
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        if not user.can_login():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User account is inactive or locked"
            )
        
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )

@router.post("/register", response_model=TokenResponse)
async def register_user(
    user_data: UserRegister,
    request: Request,
    db: AsyncSession = Depends(get_arabic_db_session)
):
    """Register new user with Arabic name support"""
    client_ip = request.client.host
    
    # Check rate limiting
    allowed, remaining = rate_limiter.is_allowed(client_ip)
    if not allowed:
        log_security_event("RATE_LIMIT_EXCEEDED", client_ip, "User registration")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many registration attempts"
        )
    
    try:
        # Check if username exists
        result = await db.execute(select(User).where(User.username == user_data.username))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already exists"
            )
        
        # Check if email exists
        result = await db.execute(select(User).where(User.email == user_data.email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Generate display name if not provided
        display_name_ar = user_data.display_name_ar
        if not display_name_ar and (user_data.first_name_ar or user_data.last_name_ar):
            display_name_ar = name_validator.suggest_arabic_display_name(
                user_data.first_name_ar, user_data.last_name_ar
            )
        
        # Create new user
        hashed_password = auth_manager.hash_password(user_data.password)
        
        new_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            first_name_ar=user_data.first_name_ar,
            last_name_ar=user_data.last_name_ar,
            display_name_ar=display_name_ar,
            phone=user_data.phone,
            language_preference=user_data.language_preference,
            timezone=user_data.timezone,
            is_verified=True  # Auto-verify for now
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        # Create tokens
        user_data_for_token = auth_manager.extract_user_data_for_token(new_user)
        access_token = auth_manager.create_access_token(user_data_for_token)
        refresh_token = auth_manager.create_refresh_token({"user_id": new_user.id})
        
        # Store refresh token
        db_refresh_token = RefreshToken(
            token=refresh_token,
            user_id=new_user.id,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        db.add(db_refresh_token)
        await db.commit()
        
        # Update login stats
        new_user.last_login = datetime.utcnow()
        new_user.login_count += 1
        await db.commit()
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=30 * 60,  # 30 minutes
            user=user_data_for_token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=TokenResponse)
async def login_user(
    login_data: UserLogin,
    request: Request,
    db: AsyncSession = Depends(get_arabic_db_session)
):
    """Login user with username or email"""
    client_ip = request.client.host
    
    try:
        # Find user by username or email
        result = await db.execute(
            select(User).where(
                (User.username == login_data.username_or_email) |
                (User.email == login_data.username_or_email)
            )
        )
        user = result.scalar_one_or_none()
        
        if not user:
            log_security_event("INVALID_LOGIN", client_ip, f"User not found: {login_data.username_or_email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Check if account is locked
        if user.is_locked():
            log_security_event("LOCKED_ACCOUNT_LOGIN", client_ip, f"User: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is temporarily locked"
            )
        
        # Verify password
        if not auth_manager.verify_password(login_data.password, user.password_hash):
            # Increment failed attempts
            user.failed_login_attempts += 1
            
            # Lock account after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=30)
                log_security_event("ACCOUNT_LOCKED", client_ip, f"User: {user.username}")
            
            await db.commit()
            
            log_security_event("INVALID_PASSWORD", client_ip, f"User: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
        
        # Check if user can login
        if not user.can_login():
            log_security_event("INACTIVE_USER_LOGIN", client_ip, f"User: {user.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is inactive"
            )
        
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        user.login_count += 1
        
        # Create tokens
        user_data_for_token = auth_manager.extract_user_data_for_token(user)
        
        # Longer expiry if remember_me is True
        access_token_expire = timedelta(hours=24) if login_data.remember_me else None
        access_token = auth_manager.create_access_token(user_data_for_token, access_token_expire)
        refresh_token = auth_manager.create_refresh_token({"user_id": user.id})
        
        # Store refresh token
        db_refresh_token = RefreshToken(
            token=refresh_token,
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        db.add(db_refresh_token)
        
        # Create session record
        session_token = RefreshToken.generate_token()
        user_session = UserSession(
            user_id=user.id,
            session_token=session_token,
            ip_address=client_ip,
            user_agent=request.headers.get("user-agent"),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        db.add(user_session)
        
        await db.commit()
        
        expires_in = (24 * 60 * 60) if login_data.remember_me else (30 * 60)
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
            user=user_data_for_token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_arabic_db_session)
):
    """Get current user profile"""
    try:
        # Load organization if exists
        organization_data = None
        if current_user.organization:
            organization_data = {
                "id": current_user.organization.id,
                "name": current_user.organization.name,
                "name_ar": current_user.organization.name_ar,
                "display_name": current_user.organization.display_name
            }
        
        return UserProfile(
            id=current_user.id,
            username=current_user.username,
            email=current_user.email,
            first_name=current_user.first_name,
            last_name=current_user.last_name,
            first_name_ar=current_user.first_name_ar,
            last_name_ar=current_user.last_name_ar,
            display_name_ar=current_user.display_name_ar,
            full_name=current_user.full_name,
            display_name=current_user.display_name,
            phone=current_user.phone,
            language_preference=current_user.language_preference,
            timezone=current_user.timezone,
            role=current_user.role,
            is_active=current_user.is_active,
            is_verified=current_user.is_verified,
            organization=organization_data,
            created_at=current_user.created_at,
            last_login=current_user.last_login
        )
        
    except Exception as e:
        logger.error(f"Error getting user profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve user profile"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh_request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_arabic_db_session)
):
    """Refresh access token using refresh token"""
    try:
        # Verify refresh token
        payload = auth_manager.verify_token(refresh_request.refresh_token, "refresh")
        user_id = payload.get("user_id")
        
        # Check if refresh token exists in database
        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token == refresh_request.refresh_token,
                RefreshToken.user_id == user_id
            )
        )
        db_token = result.scalar_one_or_none()
        
        if not db_token or not db_token.is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )
        
        # Get user
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user or not user.can_login():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new access token
        user_data_for_token = auth_manager.extract_user_data_for_token(user)
        new_access_token = auth_manager.create_access_token(user_data_for_token)
        
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_request.refresh_token,
            expires_in=30 * 60,
            user=user_data_for_token
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not refresh token"
        )

@router.post("/logout")
async def logout_user(
    refresh_request: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_arabic_db_session)
):
    """Logout user and revoke refresh token"""
    try:
        # Revoke refresh token
        result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.token == refresh_request.refresh_token,
                RefreshToken.user_id == current_user.id
            )
        )
        db_token = result.scalar_one_or_none()
        
        if db_token:
            db_token.is_revoked = True
            await db.commit()
        
        return {"message": "Successfully logged out"}
        
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )