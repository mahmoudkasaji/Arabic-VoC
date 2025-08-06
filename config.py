"""
Environment-specific configuration for Arabic Voice of Customer Platform
Supports test, staging, and production environments
"""

import os
from datetime import timedelta

class BaseConfig:
    """Base configuration with common settings"""
    
    # Application settings
    APP_NAME = "Voice of Customer Platform"
    VERSION = "1.0.0"
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Database settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
    
    # Arabic processing settings
    ARABIC_LOCALE = "ar_SA.UTF-8"
    DEFAULT_LANGUAGE = "ar"
    RTL_SUPPORT = True
    
    # OpenAI settings
    OPENAI_MODEL = "gpt-4o"
    OPENAI_MAX_TOKENS = 2000
    OPENAI_TEMPERATURE = 0.3
    OPENAI_TIMEOUT = 30
    
    # Security settings
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Pagination defaults
    DEFAULT_PAGE_SIZE = 10
    MAX_PAGE_SIZE = 100

class DevelopmentConfig(BaseConfig):
    """Development environment configuration"""
    
    ENVIRONMENT = "development"
    DEBUG = True
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", 
        "sqlite:///arabic_voc_dev.db"
    )
    
    # Logging
    LOG_LEVEL = "DEBUG"
    
    # OpenAI (use lower limits for dev)
    OPENAI_MAX_RETRIES = 2
    
    # Rate limiting (more permissive for dev)
    RATE_LIMIT_ENABLED = False
    
    # CORS (permissive for dev)
    CORS_ORIGINS = ["*"]

class TestConfig(BaseConfig):
    """Test environment configuration"""
    
    ENVIRONMENT = "test"
    DEBUG = False
    TESTING = True
    
    # Database (in-memory for fast tests)
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "TEST_DATABASE_URL",
        "sqlite:///:memory:"
    )
    
    # Disable external API calls in tests
    OPENAI_API_KEY = "test-key"
    OPENAI_MOCK_RESPONSES = True
    
    # Logging
    LOG_LEVEL = "WARNING"
    
    # Security (relaxed for testing)
    SECRET_KEY = "test-secret-key"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    
    # Rate limiting disabled for tests
    RATE_LIMIT_ENABLED = False
    
    # CORS
    CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]

class StagingConfig(BaseConfig):
    """Staging environment configuration"""
    
    ENVIRONMENT = "staging"
    DEBUG = False
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get("STAGING_DATABASE_URL")
    SQLALCHEMY_ENGINE_OPTIONS = {
        **BaseConfig.SQLALCHEMY_ENGINE_OPTIONS,
        "pool_size": 10,
        "max_overflow": 20,
    }
    
    # Security
    SECRET_KEY = os.environ.get("STAGING_SECRET_KEY")
    
    # OpenAI
    OPENAI_API_KEY = os.environ.get("STAGING_OPENAI_API_KEY")
    OPENAI_MAX_RETRIES = 3
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Rate limiting (moderate for staging)
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_REQUESTS_PER_MINUTE = 200
    RATE_LIMIT_REQUESTS_PER_HOUR = 2000
    
    # CORS (specific staging domains)
    CORS_ORIGINS = [
        "https://staging-arabic-voc.replit.app",
        "https://staging.your-domain.com"
    ]

class ProductionConfig(BaseConfig):
    """Production environment configuration"""
    
    ENVIRONMENT = "production"
    DEBUG = False
    TESTING = False
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_ENGINE_OPTIONS = {
        **BaseConfig.SQLALCHEMY_ENGINE_OPTIONS,
        "pool_size": 20,
        "max_overflow": 30,
        "pool_timeout": 30,
    }
    
    # Security
    SECRET_KEY = os.environ.get("SECRET_KEY")
    
    # OpenAI
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    OPENAI_MAX_RETRIES = 3
    
    # Logging
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Rate limiting (strict for production)
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_REQUESTS_PER_MINUTE = 100
    RATE_LIMIT_REQUESTS_PER_HOUR = 1000
    RATE_LIMIT_BURST = 20
    
    # CORS (production domains only)
    CORS_ORIGINS = [
        "https://arabic-voc.replit.app",
        "https://your-domain.com",
        "https://www.your-domain.com"
    ]
    
    # Performance optimizations
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year
    
    @classmethod
    def validate_required_vars(cls):
        """Validate that all required environment variables are set"""
        required_vars = [
            "SECRET_KEY",
            "DATABASE_URL", 
            "OPENAI_API_KEY"
        ]
        
        missing = [var for var in required_vars if not os.environ.get(var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

# Configuration mapping
config_map = {
    "development": DevelopmentConfig,
    "test": TestConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
}

def get_config():
    """Get configuration based on FLASK_ENV environment variable"""
    env = os.environ.get("FLASK_ENV", "development")
    return config_map.get(env, DevelopmentConfig)