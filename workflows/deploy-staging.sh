#!/bin/bash
# Deploy to Staging Workflow
# Deploy Arabic VoC platform to staging environment

echo "🚀 Deploying to Staging Environment..."
echo "====================================="

# Set staging environment
export FLASK_ENV=staging

# Load staging configuration
if [ -f "environments/.env.staging" ]; then
    source environments/.env.staging
    echo "✓ Staging configuration loaded"
else
    echo "❌ Staging configuration not found"
    exit 1
fi

# Create staging database
echo "Setting up staging database..."
python scripts/database_manager.py staging create

# Seed with test data
echo "Adding test data..."
python scripts/database_manager.py staging seed

# Start staging server
echo "Starting staging server on port 5001..."
echo "Access staging at: http://localhost:5001"

gunicorn --bind 0.0.0.0:5001 --workers 2 --timeout 120 main:app