#!/bin/bash
# Environment Status Workflow
# Check status of all environments

echo "📊 Arabic VoC Environment Status"
echo "================================"

# Check development environment
echo ""
echo "🔧 DEVELOPMENT ENVIRONMENT"
echo "-------------------------"
python scripts/database_manager.py development stats 2>/dev/null || echo "❌ Development database not accessible"

# Check if development server is running
if curl -s http://localhost:5000/health >/dev/null 2>&1; then
    echo "✅ Development server running on port 5000"
    curl -s http://localhost:5000/health | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print('   Status: ' + data.get('status', 'unknown'))
    print('   Database: ' + data.get('database', 'unknown'))
    print('   Arabic support: ' + data.get('arabic_support', 'unknown'))
except:
    print('   Server responding but health data unavailable')
"
else
    echo "❌ Development server not running"
fi

# Check staging environment
echo ""
echo "🎭 STAGING ENVIRONMENT"
echo "---------------------"
if curl -s http://localhost:5001/health >/dev/null 2>&1; then
    echo "✅ Staging server running on port 5001"
    curl -s http://localhost:5001/health | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print('   Status: ' + data.get('status', 'unknown'))
except:
    print('   Server responding but health data unavailable')
"
else
    echo "❌ Staging server not running"
fi

# Check test environment
echo ""
echo "🧪 TEST ENVIRONMENT"
echo "------------------"
if curl -s http://localhost:5002/health >/dev/null 2>&1; then
    echo "✅ Test server running on port 5002"
else
    echo "❌ Test server not running (normal when not testing)"
fi

echo ""
echo "🔗 Quick Actions:"
echo "- Development: Already running (port 5000)"
echo "- Deploy to staging: Use 'Deploy Staging' workflow"
echo "- Run tests: Use 'Test Suite' workflow"