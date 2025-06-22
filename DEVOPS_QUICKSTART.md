# DevOps Quick Start Guide

## Daily Development Workflow

### 1. Start New Feature Development
```bash
# Setup development environment
python scripts/deploy_workflow.py setup-dev

# Create feature branch
git checkout -b feature/improve-arabic-sentiment

# Start development server
python scripts/env_manager.py run development
# Access: http://localhost:5000
```

### 2. Test Your Changes
```bash
# Run full test suite
python scripts/deploy_workflow.py test

# Quick environment health check
python scripts/env_manager.py health development
```

### 3. Deploy Through Pipeline
```bash
# Deploy to staging for testing
python scripts/deploy_workflow.py deploy staging

# Deploy to production (requires confirmation)
python scripts/deploy_workflow.py deploy production
```

### 4. Monitor All Environments
```bash
# Check status of all environments
python scripts/deploy_workflow.py status
```

## Key DevOps Commands

| Command | Purpose |
|---------|---------|
| `python scripts/deploy_workflow.py setup-dev` | Quick dev setup |
| `python scripts/env_manager.py run <env>` | Run specific environment |
| `python scripts/database_manager.py <env> seed` | Add test data |
| `python scripts/deploy_workflow.py deploy staging` | Full staging deployment |
| `python scripts/deploy_workflow.py status` | Check all environments |

## Environment Ports
- Development: 5000
- Staging: 5001  
- Test: 5002
- Production: 5000 (when deployed)

## Best Practices
1. Always run tests before deploying
2. Use staging for integration testing
3. Production requires manual confirmation
4. Monitor health after deployments