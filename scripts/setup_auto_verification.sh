#!/bin/bash
"""
Setup script for automatic frontend verification
Configures git hooks and file watchers
"""

echo "🔧 Setting up automatic frontend verification..."

# Create git hooks directory if it doesn't exist
mkdir -p .git/hooks

# Install pre-commit hook
echo "📝 Installing pre-commit hook..."
cp scripts/auto_verify_hook.py .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit

# Make verification script executable
chmod +x scripts/verify_frontend_integration.py

echo "✅ Auto-verification setup complete!"
echo ""
echo "Available commands:"
echo "  python workflow.py verify  - Manual verification"
echo "  python workflow.py watch   - Watch files for changes"
echo "  git commit                 - Auto-verification on commit"
echo ""
echo "💡 Verification will now run automatically on:"
echo "   - Git commits (pre-commit hook)"
echo "   - Manual verification requests"
echo "   - File watching mode"