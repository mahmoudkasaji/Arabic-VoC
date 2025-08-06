#!/bin/bash
# Fallback build script for Arabic VoC Platform
# This script provides alternative installation methods if pyproject.toml fails

set -e

echo "🔧 Starting fallback build process..."

# Environment setup
export UV_SYSTEM_PYTHON=1
export PIP_NO_BUILD_ISOLATION=1
export PIP_NO_CACHE_DIR=1

echo "📦 Installing core dependencies with pip..."

# Core Flask dependencies
python -m pip install --no-cache-dir flask flask-sqlalchemy flask-login flask-dance
python -m pip install --no-cache-dir gunicorn werkzeug jinja2

# Database
python -m pip install --no-cache-dir psycopg2-binary sqlalchemy

# AI/ML packages  
python -m pip install --no-cache-dir openai anthropic
python -m pip install --no-cache-dir langchain langchain-openai langgraph

# Arabic processing
python -m pip install --no-cache-dir arabic-reshaper python-bidi

# Additional dependencies
python -m pip install --no-cache-dir pydantic aiofiles
python -m pip install --no-cache-dir twilio oauthlib pyjwt uvicorn

echo "✅ Core dependencies installed successfully"

# Verify installation
echo "🔍 Verifying installation..."
python -c "import flask; print('✅ Flask:', flask.__version__)"
python -c "import openai; print('✅ OpenAI installed')"
python -c "import psycopg2; print('✅ PostgreSQL adapter installed')"
python -c "import arabic_reshaper; print('✅ Arabic processing installed')"

echo "🚀 Installation complete! Ready for deployment."