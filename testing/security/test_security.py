"""
Security tests for Arabic VoC platform
Testing input validation, sanitization, and rate limiting
"""

import pytest
from utils.security import ArabicSecurityValidator, validate_feedback_input, rate_limiter

class TestArabicSecurityValidator:
    """Test Arabic-specific security validation"""
    
    def setup_method(self):
        """Setup test instance"""
        self.validator = ArabicSecurityValidator()
    
    def test_xss_detection(self):
        """Test XSS pattern detection"""
        xss_inputs = [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>",
            "<iframe src='data:text/html,<script>alert(1)</script>'></iframe>",
            "النص العربي <script>alert('xss')</script> مع النص",
        ]
        
        for xss_input in xss_inputs:
            result = self.validator.validate_arabic_input(xss_input)
            assert len(result["warnings"]) > 0
            assert "XSS" in result["warnings"][0]
            # Verify sanitization
            assert "<script>" not in result["sanitized_text"].lower()
    
    def test_sql_injection_detection(self):
        """Test SQL injection pattern detection"""
        sql_inputs = [
            "'; DROP TABLE feedback; --",
            "1' UNION SELECT * FROM users--",
            "admin'; DELETE FROM feedback WHERE 1=1; --",
            "النص العربي'; DROP TABLE users; --",
        ]
        
        for sql_input in sql_inputs:
            result = self.validator.validate_arabic_input(sql_input)
            assert len(result["warnings"]) > 0
            assert "SQL injection" in result["warnings"][0]
    
    def test_command_injection_detection(self):
        """Test command injection pattern detection"""
        cmd_inputs = [
            "test && rm -rf /",
            "input | cat /etc/passwd",
            "$(rm -rf /)",
            "../../../etc/passwd",
            "النص العربي; ls -la",
        ]
        
        for cmd_input in cmd_inputs:
            result = self.validator.validate_arabic_input(cmd_input)
            assert len(result["warnings"]) > 0
            assert "command injection" in result["warnings"][0]
    
    def test_unicode_safety(self):
        """Test Unicode safety checks"""
        dangerous_unicode = [
            "\u0000Arabic text\u0000",  # Null characters
            "\u202EArabic\u202D",  # RTL/LTR override
            "\uFEFFArabic text\uFEFF",  # BOM characters
            "Normal text\u200E\u200F",  # Directional marks
        ]
        
        for dangerous_text in dangerous_unicode:
            result = self.validator.validate_arabic_input(dangerous_text)
            if result["warnings"]:
                assert any("Unicode" in warning for warning in result["warnings"])
            # Verify dangerous characters are removed
            assert "\u0000" not in result["sanitized_text"]
            assert "\uFEFF" not in result["sanitized_text"]
    
    def test_length_validation(self):
        """Test input length validation"""
        # Test content length limit
        long_content = "أ" * 6000  # Exceeds 5000 limit
        result = self.validator.validate_arabic_input(long_content, "content")
        assert not result["valid"]
        assert "maximum length" in result["errors"][0]
        
        # Test field length limit
        long_field = "أ" * 300  # Exceeds 255 limit
        result = self.validator.validate_arabic_input(long_field, "email")
        assert not result["valid"]
        assert "maximum length" in result["errors"][0]
    
    def test_email_validation(self):
        """Test email validation"""
        valid_emails = [
            "user@example.com",
            "test.email+tag@domain.co.uk",
            "user123@test-domain.com",
        ]
        
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user@domain",
            "user..double.dot@domain.com",
        ]
        
        for email in valid_emails:
            assert self.validator.validate_email(email) == True
        
        for email in invalid_emails:
            assert self.validator.validate_email(email) == False
    
    def test_phone_validation(self):
        """Test phone validation for Arabic countries"""
        valid_phones = [
            "+966501234567",  # Saudi Arabia
            "+971501234567",  # UAE
            "+20101234567",   # Egypt
            "0501234567",     # Local format
            "+1234567890123", # International
        ]
        
        invalid_phones = [
            "123",           # Too short
            "abcd1234567",   # Contains letters
            "+",             # Invalid format
            "00000000000000000", # Too long
        ]
        
        for phone in valid_phones:
            assert self.validator.validate_phone(phone) == True
        
        for phone in invalid_phones:
            assert self.validator.validate_phone(phone) == False
    
    def test_rating_validation(self):
        """Test rating validation"""
        valid_ratings = [1, 2, 3, 4, 5, None]
        invalid_ratings = [0, 6, -1, 10, "5", 3.5]
        
        for rating in valid_ratings:
            assert self.validator.validate_rating(rating) == True
        
        for rating in invalid_ratings:
            assert self.validator.validate_rating(rating) == False

class TestFeedbackValidation:
    """Test comprehensive feedback validation"""
    
    def test_valid_feedback(self):
        """Test valid feedback input"""
        result = validate_feedback_input(
            content="الخدمة ممتازة جداً",
            channel="website",
            customer_email="user@example.com",
            rating=5
        )
        
        assert result["valid"] == True
        assert len(result["errors"]) == 0
        assert result["sanitized_text"] == "الخدمة ممتازة جداً"
    
    def test_invalid_channel(self):
        """Test invalid channel validation"""
        result = validate_feedback_input(
            content="اختبار",
            channel="invalid_channel"
        )
        
        assert result["valid"] == False
        assert "Invalid channel" in result["errors"][0]
    
    def test_invalid_email_warning(self):
        """Test invalid email generates warning"""
        result = validate_feedback_input(
            content="اختبار",
            channel="website",
            customer_email="invalid-email"
        )
        
        assert result["valid"] == True  # Should be valid with warning
        assert any("email" in warning.lower() for warning in result["warnings"])
    
    def test_malicious_content_sanitization(self):
        """Test malicious content is sanitized"""
        result = validate_feedback_input(
            content="اختبار <script>alert('xss')</script>",
            channel="website"
        )
        
        assert result["valid"] == True
        assert "<script>" not in result["sanitized_text"]
        assert "اختبار" in result["sanitized_text"]

class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limit_allows_normal_requests(self):
        """Test normal request volume is allowed"""
        client_ip = "192.168.1.1"
        
        # Should allow initial requests
        for i in range(10):
            allowed, remaining = rate_limiter.is_allowed(client_ip)
            assert allowed == True
            assert remaining >= 0
    
    def test_rate_limit_blocks_excessive_requests(self):
        """Test excessive requests are blocked"""
        client_ip = "192.168.1.2"
        
        # Make maximum allowed requests
        for i in range(100):
            allowed, remaining = rate_limiter.is_allowed(client_ip)
            if not allowed:
                break
        
        # Next request should be blocked
        allowed, remaining = rate_limiter.is_allowed(client_ip)
        assert allowed == False
        assert remaining == 0
    
    def test_rate_limit_per_ip(self):
        """Test rate limiting is per IP address"""
        client_ip1 = "192.168.1.3"
        client_ip2 = "192.168.1.4"
        
        # Exhaust limit for IP1
        for i in range(100):
            rate_limiter.is_allowed(client_ip1)
        
        # IP1 should be blocked
        allowed1, _ = rate_limiter.is_allowed(client_ip1)
        assert allowed1 == False
        
        # IP2 should still be allowed
        allowed2, _ = rate_limiter.is_allowed(client_ip2)
        assert allowed2 == True
    
    def test_rate_limit_cleanup(self):
        """Test old entries are cleaned up"""
        client_ip = "192.168.1.5"
        
        # Add some requests
        for i in range(10):
            rate_limiter.is_allowed(client_ip)
        
        # Check cleanup doesn't crash
        rate_limiter.cleanup_old_entries()
        
        # Should still be able to make requests
        allowed, _ = rate_limiter.is_allowed(client_ip)
        assert allowed == True

class TestSecurityIntegration:
    """Test security integration with Arabic processing"""
    
    def test_arabic_text_with_security_patterns(self):
        """Test Arabic text mixed with security patterns"""
        mixed_texts = [
            "الخدمة جيدة <script>alert('test')</script>",
            "المنتج ممتاز'; DROP TABLE users; --",
            "النص العربي $(rm -rf /)",
            "اختبار {{7*7}} العربية",
        ]
        
        validator = ArabicSecurityValidator()
        
        for text in mixed_texts:
            result = validator.validate_arabic_input(text)
            
            # Should detect security issues
            assert len(result["warnings"]) > 0
            
            # Should preserve Arabic content
            arabic_chars = [c for c in text if '\u0600' <= c <= '\u06FF']
            sanitized_arabic_chars = [c for c in result["sanitized_text"] if '\u0600' <= c <= '\u06FF']
            assert len(sanitized_arabic_chars) > 0
    
    def test_performance_with_security_validation(self):
        """Test security validation performance"""
        import time
        
        validator = ArabicSecurityValidator()
        large_text = "النص العربي الطويل جداً " * 1000
        
        start_time = time.time()
        result = validator.validate_arabic_input(large_text)
        end_time = time.time()
        
        # Should complete within reasonable time
        assert (end_time - start_time) < 3.0
        assert result["valid"] == True
    
    def test_memory_safety_with_large_inputs(self):
        """Test memory safety with large inputs"""
        import sys
        
        validator = ArabicSecurityValidator()
        
        # Test with various large inputs
        test_sizes = [1000, 5000, 10000]
        
        for size in test_sizes:
            large_text = "أ" * size
            
            try:
                result = validator.validate_arabic_input(large_text)
                
                if size <= 5000:  # Within limits
                    assert result["valid"] == True
                else:  # Exceeds limits
                    assert result["valid"] == False
                    
            except MemoryError:
                # Acceptable for very large inputs
                assert size >= 10000