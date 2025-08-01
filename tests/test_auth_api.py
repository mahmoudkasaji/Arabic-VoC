"""
Authentication API tests for Arabic VoC platform
Testing user registration, login, and profile management with Arabic names
"""

import pytest
import asyncio
from httpx import AsyncClient
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models.auth import User, Organization
# Note: Auth API migrated to Flask routes in routes.py
# from api.auth import router as auth_router
from utils.database_arabic import init_arabic_database, arabic_db_manager

# Note: Test app disabled as Auth API migrated to Flask routes
# Create test app
# test_app = FastAPI()
# test_app.include_router(auth_router)

class TestUserRegistration:
    """Test user registration with Arabic names"""
    
    @pytest.mark.asyncio
    async def test_register_user_with_arabic_names(self):
        """Test registering user with Arabic names"""
        await init_arabic_database()
        
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            user_data = {
                "username": "ahmed_test",
                "email": "ahmed@example.com",
                "password": "SecurePass123!",
                "first_name": "Ahmed",
                "last_name": "Ali",
                "first_name_ar": "أحمد",
                "last_name_ar": "علي",
                "display_name_ar": "أحمد علي المحترم",
                "phone": "+966501234567",
                "language_preference": "ar",
                "timezone": "Asia/Riyadh"
            }
            
            response = await client.post("/api/auth/register", json=user_data)
            
            assert response.status_code == 200
            data = response.json()
            
            # Verify response structure
            assert "access_token" in data
            assert "refresh_token" in data
            assert "user" in data
            assert data["token_type"] == "bearer"
            
            # Verify user data in response
            user_info = data["user"]
            assert user_info["username"] == "ahmed_test"
            assert user_info["email"] == "ahmed@example.com"
            assert user_info["language_preference"] == "ar"
            assert "أحمد علي المحترم" in user_info["display_name"]
    
    @pytest.mark.asyncio
    async def test_register_duplicate_username(self):
        """Test registration with duplicate username"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            user_data = {
                "username": "duplicate_user",
                "email": "unique@example.com",
                "password": "SecurePass123!",
                "first_name_ar": "محمد"
            }
            
            # Register first user
            response1 = await client.post("/api/auth/register", json=user_data)
            assert response1.status_code == 200
            
            # Try to register with same username
            user_data["email"] = "different@example.com"
            response2 = await client.post("/api/auth/register", json=user_data)
            assert response2.status_code == 400
            assert "already exists" in response2.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_register_invalid_arabic_name(self):
        """Test registration with invalid Arabic name"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            user_data = {
                "username": "invalid_arabic",
                "email": "invalid@example.com",
                "password": "SecurePass123!",
                "first_name_ar": "John123",  # Invalid Arabic name
                "last_name_ar": "علي"
            }
            
            response = await client.post("/api/auth/register", json=user_data)
            assert response.status_code == 422
            
            errors = response.json()["detail"]
            error_messages = [error["msg"] for error in errors]
            assert any("Arabic characters" in msg for msg in error_messages)
    
    @pytest.mark.asyncio
    async def test_register_weak_password(self):
        """Test registration with weak password"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            user_data = {
                "username": "weak_pass_user",
                "email": "weak@example.com",
                "password": "123",  # Too weak
                "first_name_ar": "سارة"
            }
            
            response = await client.post("/api/auth/register", json=user_data)
            assert response.status_code == 422
            
            errors = response.json()["detail"]
            error_messages = [error["msg"] for error in errors]
            assert any("Password validation failed" in msg for msg in error_messages)

class TestUserLogin:
    """Test user login functionality"""
    
    async def create_test_user(self):
        """Helper to create test user"""
        async with arabic_db_manager.session_factory() as session:
            from utils.auth import auth_manager
            
            user = User(
                username="test_login_user",
                email="login@example.com",
                password_hash=auth_manager.hash_password("TestPass123!"),
                first_name_ar="محمد",
                last_name_ar="الأحمد",
                language_preference="ar",
                is_verified=True
            )
            
            session.add(user)
            await session.commit()
            return user
    
    @pytest.mark.asyncio
    async def test_login_with_username(self):
        """Test login with username"""
        await init_arabic_database()
        await self.create_test_user()
        
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            login_data = {
                "username_or_email": "test_login_user",
                "password": "TestPass123!",
                "remember_me": False
            }
            
            response = await client.post("/api/auth/login", json=login_data)
            assert response.status_code == 200
            
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data
            assert data["user"]["username"] == "test_login_user"
    
    @pytest.mark.asyncio
    async def test_login_with_email(self):
        """Test login with email"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            login_data = {
                "username_or_email": "login@example.com",
                "password": "TestPass123!",
                "remember_me": True
            }
            
            response = await client.post("/api/auth/login", json=login_data)
            assert response.status_code == 200
            
            data = response.json()
            # Remember me should give longer expiry
            assert data["expires_in"] > 30 * 60  # More than 30 minutes
    
    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            login_data = {
                "username_or_email": "test_login_user",
                "password": "WrongPassword123!",
                "remember_me": False
            }
            
            response = await client.post("/api/auth/login", json=login_data)
            assert response.status_code == 401
            assert "Invalid credentials" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self):
        """Test login with nonexistent user"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            login_data = {
                "username_or_email": "nonexistent_user",
                "password": "TestPass123!",
                "remember_me": False
            }
            
            response = await client.post("/api/auth/login", json=login_data)
            assert response.status_code == 401
            assert "Invalid credentials" in response.json()["detail"]

class TestUserProfile:
    """Test user profile management"""
    
    @pytest.mark.asyncio
    async def test_get_user_profile(self):
        """Test getting current user profile"""
        # This test requires a valid access token
        # For now, we'll test the endpoint structure
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            # Without token, should get 403
            response = await client.get("/api/auth/me")
            assert response.status_code == 403  # No authorization header
    
    @pytest.mark.asyncio
    async def test_refresh_token(self):
        """Test token refresh functionality"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            # Invalid refresh token should fail
            refresh_data = {
                "refresh_token": "invalid_token"
            }
            
            response = await client.post("/api/auth/refresh", json=refresh_data)
            assert response.status_code == 401

class TestArabicNameValidation:
    """Test Arabic name validation in authentication"""
    
    @pytest.mark.asyncio
    async def test_arabic_name_normalization(self):
        """Test Arabic name normalization during registration"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            user_data = {
                "username": "normalized_user",
                "email": "normalized@example.com",
                "password": "SecurePass123!",
                "first_name_ar": "  مُحَمَّد  ",  # With diacritics and extra spaces
                "last_name_ar": "الأَحْمَد",
                "language_preference": "ar"
            }
            
            response = await client.post("/api/auth/register", json=user_data)
            assert response.status_code == 200
            
            # Verify user was created with normalized names
            async with arabic_db_manager.session_factory() as session:
                result = await session.execute(
                    select(User).where(User.username == "normalized_user")
                )
                user = result.scalar_one_or_none()
                
                assert user is not None
                # Names should be normalized (trimmed spaces)
                assert user.first_name_ar == "مُحَمَّد"
                assert user.last_name_ar == "الأَحْمَد"
                assert user.first_name_ar.strip() == user.first_name_ar
    
    @pytest.mark.asyncio
    async def test_mixed_language_names(self):
        """Test registration with both Arabic and English names"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            user_data = {
                "username": "mixed_names",
                "email": "mixed@example.com",
                "password": "SecurePass123!",
                "first_name": "Ahmed",
                "last_name": "Smith",
                "first_name_ar": "أحمد",
                "last_name_ar": "سميث",
                "language_preference": "ar"
            }
            
            response = await client.post("/api/auth/register", json=user_data)
            assert response.status_code == 200
            
            data = response.json()
            user_info = data["user"]
            
            # Should use Arabic names for display (language preference is Arabic)
            assert "أحمد" in user_info["full_name"] or "أحمد" in user_info["display_name"]

class TestAuthenticationSecurity:
    """Test authentication security features"""
    
    @pytest.mark.asyncio
    async def test_password_hashing(self):
        """Test that passwords are properly hashed"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            user_data = {
                "username": "hash_test_user",
                "email": "hash@example.com",
                "password": "MySecretPassword123!",
                "first_name_ar": "هاشم"
            }
            
            response = await client.post("/api/auth/register", json=user_data)
            assert response.status_code == 200
            
            # Check that password is hashed in database
            async with arabic_db_manager.session_factory() as session:
                result = await session.execute(
                    select(User).where(User.username == "hash_test_user")
                )
                user = result.scalar_one_or_none()
                
                assert user is not None
                assert user.password_hash != "MySecretPassword123!"
                assert len(user.password_hash) > 50  # Hashed passwords are long
                assert user.password_hash.startswith("$2b$")  # bcrypt format
    
    @pytest.mark.asyncio
    async def test_failed_login_attempts(self):
        """Test failed login attempt tracking"""
        await init_arabic_database()
        await self.create_test_user_for_security()
        
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            login_data = {
                "username_or_email": "security_test_user",
                "password": "WrongPassword",
                "remember_me": False
            }
            
            # Make multiple failed login attempts
            for i in range(3):
                response = await client.post("/api/auth/login", json=login_data)
                assert response.status_code == 401
            
            # Check that failed attempts are tracked
            async with arabic_db_manager.session_factory() as session:
                result = await session.execute(
                    select(User).where(User.username == "security_test_user")
                )
                user = result.scalar_one_or_none()
                
                assert user is not None
                assert user.failed_login_attempts >= 3
    
    async def create_test_user_for_security(self):
        """Helper to create user for security tests"""
        async with arabic_db_manager.session_factory() as session:
            from utils.auth import auth_manager
            
            user = User(
                username="security_test_user",
                email="security@example.com",
                password_hash=auth_manager.hash_password("CorrectPass123!"),
                first_name_ar="أمان",
                is_verified=True
            )
            
            session.add(user)
            await session.commit()
            return user

class TestAuthenticationIntegration:
    """Test authentication integration with Arabic features"""
    
    @pytest.mark.asyncio
    async def test_register_and_arabic_search(self):
        """Test registering user and searching by Arabic name"""
        await init_arabic_database()
        
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            # Register user with unique Arabic name
            user_data = {
                "username": "search_test_user",
                "email": "search@example.com",
                "password": "SecurePass123!",
                "first_name_ar": "زياد",
                "last_name_ar": "المنصوري",
                "language_preference": "ar"
            }
            
            response = await client.post("/api/auth/register", json=user_data)
            assert response.status_code == 200
            
            # Search for user by Arabic name
            async with arabic_db_manager.session_factory() as session:
                from utils.database_arabic import arabic_db_manager
                
                search_results = await arabic_db_manager.search_arabic_content(
                    query="زياد",
                    table="users",
                    fields=["first_name_ar", "last_name_ar"]
                )
                
                assert len(search_results) >= 1
                found_user = search_results[0]
                assert "زياد" in found_user.get("first_name_ar", "")
    
    @pytest.mark.asyncio
    async def test_login_with_arabic_characters_in_username(self):
        """Test login with username containing Arabic characters"""
        async with AsyncClient(app=test_app, base_url="http://test") as client:
            # Register user with Arabic characters in username
            user_data = {
                "username": "user_عربي",
                "email": "arabic_user@example.com",
                "password": "SecurePass123!",
                "first_name_ar": "عبدالله",
                "language_preference": "ar"
            }
            
            response = await client.post("/api/auth/register", json=user_data)
            assert response.status_code == 200
            
            # Login with Arabic username
            login_data = {
                "username_or_email": "user_عربي",
                "password": "SecurePass123!",
                "remember_me": False
            }
            
            response = await client.post("/api/auth/login", json=login_data)
            assert response.status_code == 200
            
            data = response.json()
            assert data["user"]["username"] == "user_عربي"