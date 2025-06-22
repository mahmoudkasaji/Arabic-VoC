#!/bin/bash
# Test Suite Workflow
# Run comprehensive tests for Arabic VoC platform

echo "🧪 Starting Arabic VoC Test Suite..."
echo "=================================="

# Set test environment
export FLASK_ENV=test

# Load test configuration
source environments/.env.test

# Initialize test database
echo "Setting up test database..."
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('✓ Test database created')
"

# Run tests
echo "Running test suite..."
python -m pytest tests/ -v --tb=short

# Check test results
if [ $? -eq 0 ]; then
    echo "✅ All tests passed!"
    echo "Test environment ready on port 5002"
else
    echo "❌ Some tests failed"
    exit 1
fi