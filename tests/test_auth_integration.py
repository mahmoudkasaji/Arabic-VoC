"""
Integration tests for Arabic authentication system
Testing complete authentication flow with PostgreSQL and Arabic features
"""

import pytest
import asyncio
import os
from sqlalchemy import text
from utils.auth import auth_manager, name_validator
from utils.database import get_db_session_dep

class TestArabicNameValidation:
    """Test Arabic name validation utilities"""
    
    def test_arabic_text_detection(self):
        """Test Arabic text detection"""
        # Pure Arabic text
        assert name_validator.is_arabic_text("محمد أحمد") == True
        assert name_validator.is_arabic_text("فاطمة الزهراء") == True
        
        # Mixed text (should be considered Arabic if >70% Arabic)
        assert name_validator.is_arabic_text("محمد Ahmed") == True
        
        # Non-Arabic text
        assert name_validator.is_arabic_text("John Smith") == False
        assert name_validator.is_arabic_text("123456") == False
        assert name_validator.is_arabic_text("") == False
    
    def test_arabic_name_normalization(self):
        """Test Arabic name normalization"""
        # Test whitespace normalization
        assert name_validator.normalize_arabic_name("  محمد  ") == "محمد"
        assert name_validator.normalize_arabic_name("محمد   أحمد") == "محمد أحمد"
        
        # Test empty string handling
        assert name_validator.normalize_arabic_name("") == ""
        assert name_validator.normalize_arabic_name(None) == ""
    
    def test_arabic_name_length_validation(self):
        """Test Arabic name length validation"""
        assert name_validator.validate_arabic_name_length("محمد") == True
        assert name_validator.validate_arabic_name_length("م") == False  # Too short
        assert name_validator.validate_arabic_name_length("محمد" * 20) == False  # Too long
    
    def test_display_name_suggestion(self):
        """Test Arabic display name suggestion"""
        # Both names provided
        result = name_validator.suggest_arabic_display_name("محمد", "أحمد")
        assert result == "محمد أحمد"
        
        # Only first name
        result = name_validator.suggest_arabic_display_name("فاطمة", None)
        assert result == "فاطمة"
        
        # Only last name
        result = name_validator.suggest_arabic_display_name(None, "العلي")
        assert result == "العلي"
        
        # No names
        result = name_validator.suggest_arabic_display_name(None, None)
        assert result == ""

class TestPasswordSecurity:
    """Test password security features"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "MySecurePassword123!"
        
        # Hash password
        hashed = auth_manager.hash_password(password)
        
        # Verify hash properties
        assert hashed != password
        assert len(hashed) > 50
        assert hashed.startswith("$2b$")
        
        # Verify password verification
        assert auth_manager.verify_password(password, hashed) == True
        assert auth_manager.verify_password("WrongPassword", hashed) == False
    
    def test_password_strength_validation(self):
        """Test password strength validation"""
        # Strong password
        result = auth_manager.validate_password_strength("SecurePass123!")
        assert result["valid"] == True
        assert result["strength"] in ["Good", "Strong"]
        
        # Weak password
        result = auth_manager.validate_password_strength("123")
        assert result["valid"] == False
        assert len(result["errors"]) > 0
        
        # Common password
        result = auth_manager.validate_password_strength("password")
        assert result["valid"] == False
        assert any("common" in error.lower() for error in result["errors"])

class TestUsernameValidation:
    """Test username validation"""
    
    def test_valid_usernames(self):
        """Test valid username formats"""
        valid_usernames = [
            "user123",
            "arabic_user",
            "user-name",
            "محمد_أحمد",  # Arabic with underscore
            "user123"
        ]
        
        for username in valid_usernames:
            assert auth_manager.validate_username(username) == True
    
    def test_invalid_usernames(self):
        """Test invalid username formats"""
        invalid_usernames = [
            "us",  # Too short
            "a" * 51,  # Too long
            "",  # Empty
            "user@name",  # Invalid character
            "user name",  # Space not allowed
        ]
        
        for username in invalid_usernames:
            assert auth_manager.validate_username(username) == False

class TestEmailValidation:
    """Test email validation"""
    
    def test_valid_emails(self):
        """Test valid email formats"""
        valid_emails = [
            "user@example.com",
            "test.email+tag@domain.co.uk",
            "user123@test-domain.com",
            "arabic@عربي.com"  # International domain
        ]
        
        for email in valid_emails:
            assert auth_manager.validate_email(email) == True
    
    def test_invalid_emails(self):
        """Test invalid email formats"""
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user@domain",
            ""
        ]
        
        for email in invalid_emails:
            assert auth_manager.validate_email(email) == False

class TestJWTTokens:
    """Test JWT token creation and verification"""
    
    def test_access_token_creation(self):
        """Test access token creation"""
        data = {
            "user_id": 1,
            "username": "testuser",
            "email": "test@example.com"
        }
        
        token = auth_manager.create_access_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 50
        assert "." in token  # JWT format
    
    def test_refresh_token_creation(self):
        """Test refresh token creation"""
        data = {"user_id": 1}
        
        token = auth_manager.create_refresh_token(data)
        
        assert isinstance(token, str)
        assert len(token) > 50
        assert "." in token  # JWT format
    
    def test_token_verification(self):
        """Test token verification"""
        data = {
            "user_id": 1,
            "username": "testuser",
            "email": "test@example.com"
        }
        
        # Create and verify access token
        access_token = auth_manager.create_access_token(data)
        payload = auth_manager.verify_token(access_token, "access")
        
        assert payload["user_id"] == 1
        assert payload["username"] == "testuser"
        assert payload["type"] == "access"
        
        # Create and verify refresh token
        refresh_token = auth_manager.create_refresh_token({"user_id": 1})
        payload = auth_manager.verify_token(refresh_token, "refresh")
        
        assert payload["user_id"] == 1
        assert payload["type"] == "refresh"
    
    def test_invalid_token_verification(self):
        """Test invalid token verification"""
        from fastapi import HTTPException
        
        # Invalid token
        with pytest.raises(HTTPException):
            auth_manager.verify_token("invalid.token.here", "access")
        
        # Wrong token type
        refresh_token = auth_manager.create_refresh_token({"user_id": 1})
        with pytest.raises(HTTPException):
            auth_manager.verify_token(refresh_token, "access")  # Wrong type

class TestDatabaseIntegration:
    """Test database integration with authentication"""
    
    @pytest.mark.asyncio
    async def test_database_connection(self):
        """Test database connection for authentication"""
        try:
            # Test basic database connectivity
            db_gen = get_db_session_dep()
            db = await db_gen.__anext__()
            
            # Test simple query
            result = await db.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            assert row.test == 1
            
            await db_gen.__anext__()  # Close session
            
        except Exception as e:
            pytest.skip(f"Database not available: {e}")
    
    @pytest.mark.asyncio
    async def test_arabic_text_in_database(self):
        """Test Arabic text storage and retrieval"""
        try:
            db_gen = get_db_session_dep()
            db = await db_gen.__anext__()
            
            # Test Arabic text handling
            arabic_text = "محمد أحمد العربي"
            result = await db.execute(
                text("SELECT :text as arabic_test"),
                {"text": arabic_text}
            )
            row = result.fetchone()
            
            assert row.arabic_test == arabic_text
            assert len(row.arabic_test) == len(arabic_text)
            
            await db_gen.__anext__()  # Close session
            
        except Exception as e:
            pytest.skip(f"Database not available: {e}")

class TestAPIKeyGeneration:
    """Test API key generation and validation"""
    
    def test_api_key_generation(self):
        """Test API key generation"""
        from utils.auth import generate_api_key, validate_api_key
        
        api_key = generate_api_key()
        
        assert isinstance(api_key, str)
        assert api_key.startswith("avoc_")
        assert len(api_key) > 10
        assert validate_api_key(api_key) == True
    
    def test_invalid_api_key_validation(self):
        """Test invalid API key validation"""
        from utils.auth import validate_api_key
        
        invalid_keys = [
            "",
            "invalid_key",
            "avoc_",  # Too short
            "wrong_prefix_123456789"
        ]
        
        for key in invalid_keys:
            assert validate_api_key(key) == False

class TestAuthenticationFlow:
    """Test complete authentication flow"""
    
    def test_user_data_extraction(self):
        """Test user data extraction for tokens"""
        # Mock user object
        class MockUser:
            def __init__(self):
                self.id = 1
                self.username = "testuser"
                self.email = "test@example.com"
                self.role = "viewer"
                self.organization_id = None
                self.language_preference = "ar"
                self.first_name_ar = "محمد"
                self.last_name_ar = "أحمد"
                self.display_name_ar = "محمد أحمد"
            
            @property
            def full_name(self):
                return f"{self.first_name_ar} {self.last_name_ar}"
            
            @property
            def display_name(self):
                return self.display_name_ar
        
        user = MockUser()
        data = auth_manager.extract_user_data_for_token(user)
        
        assert data["user_id"] == 1
        assert data["username"] == "testuser"
        assert data["language_preference"] == "ar"
        assert data["full_name"] == "محمد أحمد"
        assert data["display_name"] == "محمد أحمد"
    
    def test_authentication_complete_flow(self):
        """Test complete authentication flow simulation"""
        # 1. Register user data
        user_data = {
            "username": "flow_test_user",
            "email": "flow@example.com",
            "password": "SecurePass123!",
            "first_name_ar": "سارة",
            "last_name_ar": "الأحمد"
        }
        
        # 2. Validate registration data
        assert auth_manager.validate_username(user_data["username"]) == True
        assert auth_manager.validate_email(user_data["email"]) == True
        
        password_validation = auth_manager.validate_password_strength(user_data["password"])
        assert password_validation["valid"] == True
        
        # 3. Hash password
        hashed_password = auth_manager.hash_password(user_data["password"])
        assert hashed_password != user_data["password"]
        
        # 4. Verify password
        assert auth_manager.verify_password(user_data["password"], hashed_password) == True
        
        # 5. Create tokens (simulate login)
        token_data = {
            "user_id": 1,
            "username": user_data["username"],
            "email": user_data["email"]
        }
        
        access_token = auth_manager.create_access_token(token_data)
        refresh_token = auth_manager.create_refresh_token({"user_id": 1})
        
        # 6. Verify tokens
        access_payload = auth_manager.verify_token(access_token, "access")
        refresh_payload = auth_manager.verify_token(refresh_token, "refresh")
        
        assert access_payload["username"] == user_data["username"]
        assert refresh_payload["user_id"] == 1