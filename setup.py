#!/usr/bin/env python3
"""
Fallback setup.py for Arabic VoC Platform
This provides an alternative build method if pyproject.toml fails
"""

from setuptools import setup, find_packages

# Core dependencies for the platform
REQUIRED_PACKAGES = [
    "flask>=2.3.0",
    "flask-sqlalchemy>=3.0.0", 
    "psycopg2-binary>=2.9.0",
    "openai>=1.0.0",
    "langchain>=0.1.0",
    "langchain-openai>=0.1.0",
    "langgraph>=0.1.0", 
    "arabic-reshaper>=3.0.0",
    "python-bidi>=0.4.0",
    "gunicorn>=20.1.0",
    "werkzeug>=2.3.0",
    "jinja2>=3.1.0",
    "pydantic>=2.0.0",
    "aiofiles>=23.0.0",
    "sqlalchemy>=2.0.41",
    "uvicorn>=0.34.3",
    "anthropic>=0.54.0",
    "twilio>=9.6.3",
    "flask-dance>=7.0.0",
    "flask-login>=0.6.0",
    "oauthlib>=3.2.0",
    "pyjwt>=2.8.0",
]

setup(
    name="arabic-voc-platform",
    version="1.0.0",
    description="Arabic Voice of Customer Platform with AI-powered sentiment analysis",
    python_requires=">=3.11",
    install_requires=REQUIRED_PACKAGES,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "arabic-voc=main:app",
        ],
    },
)