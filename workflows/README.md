# Replit Workflows for Arabic VoC Platform

## Available Workflows

### 1. Start Application
**Button**: "Start application" (already configured)
- Runs development environment
- Port: 5000
- Hot reload enabled

### 2. Test Suite
**Button**: "Test Suite"
- Runs comprehensive tests
- Creates clean test database
- Shows test results

### 3. Deploy Staging
**Button**: "Deploy Staging"
- Deploys to staging environment
- Port: 5001
- Production-like configuration

### 4. Environment Status
**Button**: "Environment Status"
- Shows status of all environments
- Health checks for running servers
- Database statistics

### 5. Seed Database
**Button**: "Seed Database"
- Adds Arabic test data to development
- Shows current database statistics
- Useful for testing with real data

### 6. Quick Deploy
**Button**: "Quick Deploy"
- Runs tests then deploys to staging
- One-click test and deploy
- Aborts if tests fail

## How to Use

1. **Daily Development**: Use "Start application" (default)
2. **Before Committing**: Click "Test Suite"
3. **Integration Testing**: Click "Deploy Staging"
4. **Check Everything**: Click "Environment Status"
5. **Need Test Data**: Click "Seed Database"
6. **Fast Deployment**: Click "Quick Deploy"

## Workflow Benefits

- **One-click operations** instead of typing commands
- **Visual feedback** in Replit console
- **Error handling** with clear messages
- **Environment isolation** maintained
- **Simplified DevOps** for both you and AI assistants

These workflows make the DevOps pipeline accessible through Replit's interface while maintaining the full functionality of the command-line tools.