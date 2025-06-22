# DevOps Workflow Guide for Arabic VoC Platform

## Overview

This guide outlines the complete DevOps workflow for developing, testing, and deploying the Arabic Voice of Customer platform using the established environments.

## Development Workflow

### 1. Feature Development Cycle

```bash
# Start development environment
python scripts/env_manager.py run development

# Create feature branch
git checkout -b feature/new-arabic-feature

# Develop your feature with hot reload enabled
# Application runs on http://localhost:5000
```

### 2. Local Testing

```bash
# Run comprehensive test suite
python scripts/env_manager.py test

# Check test coverage
# Results saved in htmlcov/index.html

# Run specific tests
python -m pytest tests/test_arabic_processing.py -v

# Database operations for development
python scripts/database_manager.py development seed
python scripts/database_manager.py development stats
```

### 3. Code Quality Checks

```bash
# Format code (if needed)
black . --line-length 88

# Check for issues
flake8 . --max-line-length 88 --ignore E203,W503

# Security scan
bandit -r . -x tests/
```

## Environment Promotion Pipeline

### Stage 1: Development → Test

```bash
# Ensure all tests pass
python scripts/env_manager.py test

# Commit changes
git add .
git commit -m "feat: implement Arabic sentiment analysis improvements"

# Push feature branch
git push origin feature/new-arabic-feature
```

### Stage 2: Test → Staging

```bash
# Merge to main branch (after code review)
git checkout main
git merge feature/new-arabic-feature

# Deploy to staging environment
python scripts/env_manager.py run staging

# Set up staging database
python scripts/database_manager.py staging create
python scripts/database_manager.py staging seed

# Verify staging deployment
python scripts/env_manager.py health staging

# Run integration tests against staging
curl -X POST http://localhost:5001/api/feedback/submit \
  -H "Content-Type: application/json" \
  -d '{"content":"اختبار البيئة التجريبية","channel":"website"}'
```

### Stage 3: Staging → Production

```bash
# Create production release
git tag -a v1.1.0 -m "Release v1.1.0: Arabic sentiment improvements"
git push origin v1.1.0

# Deploy to production (requires environment variables)
export FLASK_ENV=production
export SECRET_KEY="your-production-secret"
export DATABASE_URL="your-production-db-url"
export OPENAI_API_KEY="your-production-openai-key"

python scripts/env_manager.py run production

# Initialize production database (first time only)
python scripts/database_manager.py production create

# Verify production health
python scripts/env_manager.py health production
```

## Environment-Specific Operations

### Development Environment
- **Purpose**: Active development and debugging
- **Database**: SQLite with sample data
- **Configuration**: Debug enabled, hot reload
- **Port**: 5000

```bash
# Development workflow
python scripts/env_manager.py run development

# Add test data
python scripts/database_manager.py development seed

# Monitor logs
tail -f logs/development.log
```

### Test Environment
- **Purpose**: Automated testing and CI/CD
- **Database**: In-memory (clean state each run)
- **Configuration**: Mock external services
- **Port**: 5002

```bash
# Run automated tests
python scripts/env_manager.py test

# Custom test scenarios
FLASK_ENV=test python -m pytest tests/test_arabic_dialects.py

# Performance testing
python performance/load_test.py --environment test
```

### Staging Environment
- **Purpose**: Pre-production validation
- **Database**: Staging PostgreSQL
- **Configuration**: Production-like settings
- **Port**: 5001

```bash
# Deploy to staging
source environments/.env.staging
python scripts/env_manager.py run staging

# User acceptance testing
python scripts/database_manager.py staging seed

# Load testing
python performance/load_test.py --environment staging --users 50
```

### Production Environment
- **Purpose**: Live customer-facing application
- **Database**: Production PostgreSQL with backups
- **Configuration**: Full security, monitoring
- **Port**: 5000

```bash
# Production deployment
source environments/.env.production
python scripts/env_manager.py run production

# Database backup before updates
python scripts/database_manager.py production backup

# Monitor health
watch -n 30 "python scripts/env_manager.py health production"
```

## Continuous Integration Pipeline

### GitHub Actions Workflow (Recommended)

```yaml
# .github/workflows/ci-cd.yml
name: Arabic VoC CI/CD Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.11
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python scripts/env_manager.py test
    
    - name: Security scan
      run: |
        bandit -r . -x tests/
        
  deploy-staging:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to staging
      run: |
        # Deploy to staging environment
        python scripts/deploy_staging.sh
        
  deploy-production:
    needs: deploy-staging
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to production
      run: |
        # Deploy to production environment
        python scripts/deploy_production.sh
```

## Monitoring and Maintenance

### Health Monitoring

```bash
# Automated health checks
while true; do
  python scripts/env_manager.py health production
  sleep 300  # Check every 5 minutes
done

# Database monitoring
python scripts/database_manager.py production stats

# Performance monitoring
curl -s http://localhost:5000/health | jq '.'
```

### Database Operations

```bash
# Regular backups
python scripts/database_manager.py production backup

# Database migrations (when schema changes)
python scripts/database_manager.py production create

# Performance optimization
python scripts/database_manager.py production stats
```

### Log Management

```bash
# Application logs
tail -f logs/production.log

# Error monitoring
grep ERROR logs/production.log | tail -20

# Performance logs
grep "slow query" logs/production.log
```

## Security Best Practices

### Environment Variable Management

```bash
# Never commit secrets to git
echo "environments/.env.production" >> .gitignore

# Use environment-specific secrets
source environments/.env.production  # For production
source environments/.env.staging     # For staging
```

### Production Checklist

- [ ] All environment variables set securely
- [ ] Database backups configured
- [ ] SSL certificates valid
- [ ] Rate limiting enabled
- [ ] Monitoring alerts configured
- [ ] Error tracking active
- [ ] Performance monitoring enabled

## Rollback Procedures

### Emergency Rollback

```bash
# Rollback to previous version
git checkout v1.0.9
python scripts/deploy_production.sh

# Database rollback (if needed)
python scripts/database_manager.py production backup
# Restore from previous backup
```

### Feature Rollback

```bash
# Disable specific features
export FEATURE_ARABIC_ADVANCED=false
python scripts/env_manager.py run production
```

This workflow ensures reliable, scalable deployment of your Arabic VoC platform across all environments.