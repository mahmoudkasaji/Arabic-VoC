"""
Production deployment configuration for Arabic VoC platform
Optimized settings for enterprise deployment
"""

import os
from datetime import timedelta

class ProductionConfig:
    """Production-ready configuration"""
    
    # Application settings
    APP_NAME = "Arabic Voice of Customer Platform"
    VERSION = "1.0.0"
    ENVIRONMENT = "production"
    DEBUG = False
    
    # Security settings
    SECRET_KEY = os.environ.get("SECRET_KEY")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # Database settings
    DATABASE_URL = os.environ.get("DATABASE_URL")
    DATABASE_POOL_SIZE = 20
    DATABASE_MAX_OVERFLOW = 30
    DATABASE_POOL_TIMEOUT = 30
    DATABASE_POOL_RECYCLE = 300
    DATABASE_POOL_PRE_PING = True
    
    # Redis settings (for caching and sessions)
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    CACHE_TTL = 300  # 5 minutes
    SESSION_TTL = 3600  # 1 hour
    
    # OpenAI settings
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    OPENAI_MODEL = "gpt-4o"
    OPENAI_MAX_TOKENS = 2000
    OPENAI_TEMPERATURE = 0.3
    OPENAI_TIMEOUT = 30
    OPENAI_MAX_RETRIES = 3
    
    # API rate limiting
    RATE_LIMIT_ENABLED = True
    RATE_LIMIT_REQUESTS_PER_MINUTE = 100
    RATE_LIMIT_REQUESTS_PER_HOUR = 1000
    RATE_LIMIT_BURST = 20
    
    # Logging configuration
    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = "/var/log/arabic_voc/app.log"
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5
    
    # Performance settings
    WORKER_PROCESSES = 4
    WORKER_THREADS = 2
    WORKER_TIMEOUT = 120
    KEEPALIVE = 2
    MAX_REQUESTS = 1000
    MAX_REQUESTS_JITTER = 100
    
    # Arabic processing settings
    ARABIC_PROCESSING_TIMEOUT = 30
    BATCH_PROCESSING_SIZE = 50
    MAX_TEXT_LENGTH = 10000
    ENABLE_DIALECT_DETECTION = True
    ENABLE_CULTURAL_ANALYSIS = True
    
    # WebSocket settings
    WEBSOCKET_PING_INTERVAL = 20
    WEBSOCKET_PING_TIMEOUT = 10
    WEBSOCKET_CLOSE_TIMEOUT = 10
    MAX_WEBSOCKET_CONNECTIONS = 1000
    
    # File upload settings
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS = {'txt', 'csv', 'xlsx', 'pdf'}
    UPLOAD_FOLDER = "/var/uploads/arabic_voc"
    
    # Monitoring and health checks
    HEALTH_CHECK_INTERVAL = 30
    METRICS_RETENTION_DAYS = 30
    ALERT_THRESHOLDS = {
        "cpu_usage": 80,
        "memory_usage": 85,
        "response_time": 2.0,
        "error_rate": 5.0
    }
    
    # CORS settings
    CORS_ORIGINS = [
        "https://arabic-voc.replit.app",
        "https://*.replit.app",
        "https://localhost:3000"
    ]
    CORS_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_HEADERS = ["Content-Type", "Authorization", "X-Requested-With"]
    
    # Arabic-specific settings
    DEFAULT_LANGUAGE = "ar"
    SUPPORTED_LANGUAGES = ["ar", "en"]
    RTL_ENABLED = True
    ARABIC_FONTS = ["Amiri", "Cairo", "Noto Sans Arabic"]
    
    # Backup and recovery
    BACKUP_ENABLED = True
    BACKUP_INTERVAL_HOURS = 6
    BACKUP_RETENTION_DAYS = 30
    
    @classmethod
    def validate_config(cls):
        """Validate production configuration"""
        required_vars = [
            "SECRET_KEY",
            "DATABASE_URL",
            "OPENAI_API_KEY"
        ]
        
        missing_vars = [var for var in required_vars if not getattr(cls, var) or not os.environ.get(var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True

class DevelopmentConfig(ProductionConfig):
    """Development configuration"""
    ENVIRONMENT = "development"
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    RATE_LIMIT_ENABLED = False
    DATABASE_POOL_SIZE = 5
    DATABASE_MAX_OVERFLOW = 10

class TestingConfig(ProductionConfig):
    """Testing configuration"""
    ENVIRONMENT = "testing"
    DEBUG = True
    LOG_LEVEL = "DEBUG"
    DATABASE_URL = "sqlite:///test.db"
    RATE_LIMIT_ENABLED = False
    CACHE_TTL = 1

def get_config():
    """Get configuration based on environment"""
    env = os.environ.get("ENVIRONMENT", "production").lower()
    
    if env == "development":
        return DevelopmentConfig
    elif env == "testing":
        return TestingConfig
    else:
        return ProductionConfig