#!/bin/bash
"""
Test environment runner for Arabic VoC platform
"""

set -e

echo "Starting test environment for Arabic VoC Platform..."

# Load test environment
export FLASK_ENV=test
source environments/.env.test

# Create test database if needed
echo "Setting up test database..."
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Test database created')
"

# Run tests
echo "Running test suite..."
python -m pytest tests/ -v --cov=. --cov-report=html --cov-report=term

# Generate test report
echo "Test environment completed successfully"
echo "Coverage report available in htmlcov/index.html"