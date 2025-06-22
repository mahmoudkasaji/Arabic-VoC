#!/bin/bash
# Database Seed Workflow
# Add Arabic test data to development environment

echo "🌱 Seeding Development Database with Arabic Data..."
echo "================================================="

# Seed development database with Arabic feedback samples
python scripts/database_manager.py development seed

# Show current statistics
echo ""
echo "📊 Current Database Statistics:"
python scripts/database_manager.py development stats

echo ""
echo "✅ Development database seeded successfully!"
echo "🔗 View data at: http://localhost:5000/api/feedback/list"
echo "📈 Dashboard metrics: http://localhost:5000/api/dashboard/metrics"