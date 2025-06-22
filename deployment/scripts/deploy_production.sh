#!/bin/bash
"""
Production deployment script for Arabic VoC platform
"""

set -e

echo "Deploying to production environment..."

# Load production environment
export FLASK_ENV=production
source environments/.env.production

# Validate production configuration
python -c "
from config import ProductionConfig
print('Validating production configuration...')
try:
    ProductionConfig.validate_required_vars()
    print('Production configuration valid')
except ValueError as e:
    print(f'Configuration error: {e}')
    exit(1)
"

# Database migration (production)
echo "Running production database migrations..."
python -c "
from app import app, db
with app.app_context():
    db.create_all()
    print('Production database migrated')
"

# Start production server
echo "Starting production server..."
gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 --max-requests 1000 main:app