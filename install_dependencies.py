#!/usr/bin/env python3
"""
Direct dependency installer for Arabic VoC Platform
Bypasses pyproject.toml and uv build system issues
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a package using pip with no cache"""
    cmd = [sys.executable, "-m", "pip", "install", "--no-cache-dir", package]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ Installed: {package}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e.stderr}")
        return False

def main():
    """Install all required dependencies"""
    print("🚀 Installing Arabic VoC Platform dependencies...")
    
    # Set environment variables to avoid uv conflicts
    os.environ["UV_SYSTEM_PYTHON"] = "1"
    os.environ["PIP_NO_BUILD_ISOLATION"] = "1"
    os.environ["PIP_NO_CACHE_DIR"] = "1"
    
    # Core dependencies in installation order
    packages = [
        "setuptools",
        "wheel",
        "flask",
        "flask-sqlalchemy", 
        "psycopg2-binary",
        "sqlalchemy",
        "gunicorn",
        "werkzeug",
        "jinja2",
        "openai",
        "anthropic",
        "langchain",
        "langchain-openai",
        "langgraph",
        "arabic-reshaper",
        "python-bidi",
        "pydantic",
        "aiofiles",
        "twilio",
        "flask-dance",
        "flask-login",
        "oauthlib",
        "pyjwt",
        "uvicorn",
    ]
    
    success_count = 0
    total_packages = len(packages)
    
    for package in packages:
        if install_package(package):
            success_count += 1
    
    print(f"\n📊 Installation Summary:")
    print(f"✅ Successful: {success_count}/{total_packages}")
    
    if success_count == total_packages:
        print("🎉 All dependencies installed successfully!")
        
        # Verify key imports
        try:
            import flask
            import openai
            import psycopg2
            print("🔍 Verification: Core modules can be imported")
            return True
        except ImportError as e:
            print(f"⚠️  Warning: Could not import core module: {e}")
            return False
    else:
        print("❌ Some dependencies failed to install")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)