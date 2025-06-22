"""
Configuration module for Arabic VoC Platform
"""

import os
from .base import DevelopmentConfig, TestConfig, StagingConfig, ProductionConfig

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