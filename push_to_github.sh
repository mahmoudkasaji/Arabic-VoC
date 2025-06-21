#!/bin/bash
# Script to push Arabic VoC Platform to GitHub
# Run this script to resolve git locks and push to your repository

echo "🚀 Pushing Arabic Voice of Customer Platform to GitHub"
echo "======================================================"

# Navigate to project directory
cd /home/runner/workspace

# Remove any git lock files
echo "1. Cleaning git lock files..."
rm -f .git/config.lock .git/index.lock .git/refs/heads/main.lock

# Remove existing origin if any
echo "2. Configuring remote repository..."
git remote remove origin 2>/dev/null || true

# Add your GitHub repository as origin
git remote add origin https://github.com/akschneider1/arabic-voice-of-customer.git

# Verify remote configuration
echo "3. Verifying remote configuration..."
git remote -v

# Show current status
echo "4. Current repository status:"
echo "   - Branch: $(git branch --show-current)"
echo "   - Commits: $(git log --oneline | wc -l)"
echo "   - User: $(git config user.name) ($(git config user.email))"

# Push to GitHub
echo "5. Pushing to GitHub..."
git push -u origin main

if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed to GitHub!"
    echo "🔗 Repository URL: https://github.com/akschneider1/arabic-voice-of-customer"
else
    echo "❌ Push failed. Please check:"
    echo "   - Repository exists and is private on GitHub"
    echo "   - You have write access to akschneider1/arabic-voice-of-customer"
    echo "   - Your GitHub authentication is configured"
fi