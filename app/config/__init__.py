"""
Configuration module for Arabic VoC Platform
"""

import os

# Import config classes with fallback
try:
    from .base import DevelopmentConfig, TestConfig, StagingConfig, ProductionConfig
except ImportError:
    # Fallback basic config if base config not available
    class DevelopmentConfig:
        DEBUG = True
        SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")
        SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///arabic_voc.db")
        SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    TestConfig = StagingConfig = ProductionConfig = DevelopmentConfig

def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('FLASK_ENV', 'development').lower()
    
    config_map = {
        'development': DevelopmentConfig,
        'testing': TestConfig,
        'staging': StagingConfig,
        'production': ProductionConfig
    }
    
    return config_map.get(env, DevelopmentConfig)