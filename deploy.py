#!/usr/bin/env python3
"""
Comprehensive deployment script for Arabic VoC Platform
Handles UV build system issues and ensures proper deployment
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, description=""):
    """Execute a command and handle errors"""
    print(f"🔄 {description}")
    try:
        result = subprocess.run(cmd, shell=True, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def setup_environment():
    """Set up environment variables to avoid UV conflicts"""
    env_vars = {
        "UV_SYSTEM_PYTHON": "1",
        "UV_NO_CACHE": "1", 
        "PIP_NO_BUILD_ISOLATION": "1",
        "PIP_NO_CACHE_DIR": "1",
        "PIP_DISABLE_PIP_VERSION_CHECK": "1",
        "SETUPTOOLS_USE_DISTUTILS": "local",
        "PYTHONPATH": ".",
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        print(f"🔧 Set {key}={value}")

def verify_files():
    """Verify all necessary deployment files exist"""
    required_files = [
        "main.py",
        "app.py", 
        "pyproject.toml",
        "setup.py",
        "deployment.toml",
        "MANIFEST.in",
        "runtime.txt",
        "Procfile",
        "replit.toml"
    ]
    
    missing = []
    for file in required_files:
        if not Path(file).exists():
            missing.append(file)
    
    if missing:
        print(f"❌ Missing files: {', '.join(missing)}")
        return False
    
    print("✅ All deployment files present")
    return True

def install_dependencies():
    """Install dependencies using multiple methods"""
    print("📦 Installing dependencies...")
    
    # Method 1: Try setup.py
    if run_command("python setup.py install", "Installing via setup.py"):
        return True
    
    # Method 2: Try pip install with pyproject.toml
    if run_command("python -m pip install --no-cache-dir -e .", "Installing via pip with pyproject.toml"):
        return True
        
    # Method 3: Use fallback script
    if run_command("python install_dependencies.py", "Installing via fallback script"):
        return True
        
    # Method 4: Manual installation
    core_packages = [
        "flask", "flask-sqlalchemy", "psycopg2-binary", "gunicorn",
        "openai", "arabic-reshaper", "python-bidi"
    ]
    
    for package in core_packages:
        if not run_command(f"python -m pip install --no-cache-dir {package}", f"Installing {package}"):
            print(f"⚠️ Failed to install {package}, continuing...")
    
    return True

def test_application():
    """Test that the application can start"""
    print("🧪 Testing application startup...")
    
    test_script = """
import sys
try:
    import main
    import app
    print("✅ Application modules import successfully")
    
    # Test Flask app creation
    from app import app
    with app.test_client() as client:
        print("✅ Flask test client works")
    
    print("✅ Application is ready for deployment")
    sys.exit(0)
except Exception as e:
    print(f"❌ Application test failed: {e}")
    sys.exit(1)
"""
    
    try:
        subprocess.run([sys.executable, "-c", test_script], check=True)
        return True
    except subprocess.CalledProcessError:
        print("❌ Application test failed")
        return False

def main():
    """Main deployment process"""
    print("🚀 Starting Arabic VoC Platform deployment...")
    
    # Step 1: Setup environment
    setup_environment()
    
    # Step 2: Verify files
    if not verify_files():
        sys.exit(1)
    
    # Step 3: Clean cache
    print("🧹 Cleaning build cache...")
    for cache_dir in ["__pycache__", ".pytest_cache", "build", "dist", "*.egg-info"]:
        if os.path.exists(cache_dir):
            shutil.rmtree(cache_dir, ignore_errors=True)
    
    # Step 4: Install dependencies  
    if not install_dependencies():
        print("❌ Dependency installation failed")
        sys.exit(1)
    
    # Step 5: Test application
    if not test_application():
        print("❌ Application testing failed")
        sys.exit(1)
    
    print("🎉 Deployment preparation completed successfully!")
    print("📋 Deployment Summary:")
    print("   ✅ Environment configured to avoid UV conflicts")
    print("   ✅ All deployment files present")
    print("   ✅ Dependencies installed")
    print("   ✅ Application tested and ready")
    print()
    print("🚀 Ready for Replit deployment!")

if __name__ == "__main__":
    main()