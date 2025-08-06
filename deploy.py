#!/usr/bin/env python3
"""
Deployment script for Arabic VoC Platform
Handles UV conflicts and ensures proper package installation
"""

import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def set_deployment_env():
    """Set environment variables to handle UV conflicts"""
    env_vars = {
        'UV_SYSTEM_PYTHON': '1',
        'PIP_NO_BUILD_ISOLATION': '1',
        'PIP_NO_CACHE_DIR': '1',
        'PYTHONPATH': '.',
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        logger.info(f"Set {key}={value}")

def get_python_executable():
    """Get the correct Python executable"""
    # Try to find the system python3 with pip support
    candidates = [
        'python3',
        '/usr/bin/python3',
        '/nix/store/*/bin/python3',
        sys.executable
    ]
    
    for candidate in candidates:
        try:
            result = subprocess.run([candidate, '-m', 'pip', '--version'], 
                                   capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Found working Python with pip: {candidate}")
                return candidate
        except FileNotFoundError:
            continue
    
    # Fallback to system python3
    return 'python3'

def install_with_pip():
    """Install packages using pip directly"""
    python_exec = get_python_executable()
    packages = [
        'flask>=2.3.0',
        'flask-sqlalchemy>=3.0.0',
        'psycopg2-binary>=2.9.0',
        'openai>=1.0.0',
        'arabic-reshaper>=3.0.0',
        'python-bidi>=0.4.0',
        'gunicorn>=20.1.0',
        'werkzeug>=2.3.0',
        'jinja2>=3.1.0',
        'pydantic>=2.0.0',
        'sqlalchemy>=2.0.0',
        'anthropic>=0.25.0',
        'twilio>=8.0.0',
        'flask-dance>=7.0.0',
        'flask-login>=0.6.0',
        'oauthlib>=3.2.0',
        'pyjwt>=2.8.0',
    ]
    
    for package in packages:
        try:
            subprocess.run([
                python_exec, '-m', 'pip', 'install', 
                '--no-cache-dir', '--no-build-isolation', package
            ], check=True)
            logger.info(f"Successfully installed {package}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install {package}: {e}")
            return False
    
    return True

def install_with_pyproject():
    """Try installing with pyproject.toml"""
    python_exec = get_python_executable()
    try:
        subprocess.run([
            python_exec, '-m', 'pip', 'install', 
            '--no-cache-dir', '--no-build-isolation', '-e', '.'
        ], check=True)
        logger.info("Successfully installed via pyproject.toml")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"pyproject.toml installation failed: {e}")
        return False

def main():
    """Main deployment process"""
    logger.info("Starting Arabic VoC Platform deployment...")
    
    # Set environment variables
    set_deployment_env()
    
    # Try pyproject.toml first, fallback to pip
    if not install_with_pyproject():
        logger.info("Falling back to direct pip installation...")
        if not install_with_pip():
            logger.error("All installation methods failed!")
            sys.exit(1)
    
    # Verify key imports
    try:
        import flask
        import openai
        import psycopg2
        import arabic_reshaper
        logger.info("All key packages verified successfully")
    except ImportError as e:
        logger.error(f"Import verification failed: {e}")
        sys.exit(1)
    
    logger.info("Deployment completed successfully!")

if __name__ == "__main__":
    main()