#!/bin/bash
# Quick Deploy Workflow
# Run tests and deploy to staging in one command

echo "⚡ Quick Deploy: Test → Staging"
echo "==============================="

# Step 1: Run tests
echo "Step 1: Running tests..."
export FLASK_ENV=test
source environments/.env.test

python -c "
from app import app, db
with app.app_context():
    db.create_all()
"

python -m pytest tests/ -v --tb=short

if [ $? -ne 0 ]; then
    echo "❌ Tests failed - deployment aborted"
    exit 1
fi

echo "✅ Tests passed!"

# Step 2: Deploy to staging
echo ""
echo "Step 2: Deploying to staging..."
export FLASK_ENV=staging
source environments/.env.staging

python scripts/database_manager.py staging create
python scripts/database_manager.py staging seed

echo ""
echo "🚀 Quick deploy completed successfully!"
echo "🎭 Staging environment ready on port 5001"
echo ""
echo "Start staging server with:"
echo "gunicorn --bind 0.0.0.0:5001 --workers 2 main:app"