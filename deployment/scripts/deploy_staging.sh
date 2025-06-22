#!/bin/bash
"""
Staging deployment script for Arabic VoC platform
"""

set -e

echo "Deploying to staging environment..."

# Load staging environment
export FLASK_ENV=staging
source environments/.env.staging

# Validate required environment variables
python -c "
from config import StagingConfig
print('Validating staging configuration...')
required_vars = ['STAGING_SECRET_KEY', 'STAGING_DATABASE_URL', 'STAGING_OPENAI_API_KEY']
import os
missing = [var for var in required_vars if not os.environ.get(var)]
if missing:
    raise ValueError(f'Missing required variables: {missing}')
print('Staging configuration valid')
"

# Database migration
echo "Running database migrations..."
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Staging database migrated')
"

# Run staging server
echo "Starting staging server..."
gunicorn --bind 0.0.0.0:5001 --workers 2 --timeout 120 main:app