# GitHub Repository Setup Guide

## Current Issue
The repository has git lock files preventing remote operations. The error "Error (UNKNOWN) adding origin" occurs because:

1. `.git/index.lock` and `.git/config.lock` files are blocking operations
2. No remote origin is currently configured
3. Replit's git protections are preventing direct manipulation

## Solution Steps

### Step 1: Clean Git State (Manual)
You need to manually resolve the git lock files:

1. Open the Shell tab in Replit
2. Run these commands one by one:
```bash
# Remove lock files
rm -f .git/index.lock .git/config.lock

# Check git status
git status

# Verify no remotes exist
git remote -v
```

### Step 2: Configure Remote Repository
```bash
# Add your GitHub repository as origin
git remote add origin https://github.com/akschneider1/Arabic-VoC-2.git

# Verify remote was added
git remote -v

# Test connectivity
git ls-remote origin
```

### Step 3: Initial Push Setup
```bash
# Add all files to staging
git add .

# Create initial commit
git commit -m "Initial Flask Arabic VoC Platform setup"

# Push to GitHub (may require authentication)
git push -u origin main
```

### Step 4: Authentication Setup
If authentication fails, you'll need to:

1. Go to GitHub.com → Settings → Developer settings → Personal Access Tokens
2. Generate a new token with repo permissions
3. Use the token as your password when prompted

### Alternative: Use Replit's GitHub Integration
1. Go to the Replit project settings
2. Look for "GitHub" or "Version Control" section
3. Connect the repository through Replit's interface
4. This bypasses command-line git issues

## Repository Information
- GitHub URL: https://github.com/akschneider1/Arabic-VoC-2.git
- Owner: akschneider1
- Project: Flask-based Arabic Voice of Customer Platform
- Main Branch: main (or master)

## Current Project State
- Flask application running successfully
- Database models configured
- Arabic text processing working
- All dependencies installed
- Ready for version control