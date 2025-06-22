# Multi-Environment Setup for Arabic VoC Platform

## Overview

The Arabic Voice of Customer platform now supports four distinct environments:

- **Development** - Local development with debug enabled
- **Test** - Automated testing with in-memory database
- **Staging** - Pre-production testing environment
- **Production** - Live production environment

## Environment Configuration

### Quick Start

```bash
# Run in development mode (default)
python scripts/env_manager.py run development

# Run test suite
python scripts/env_manager.py test

# Run in staging mode
python scripts/env_manager.py run staging

# Check environment health
python scripts/env_manager.py health development
```

### Environment Files

Each environment has its own configuration file in `environments/`:

- `.env.development` - Development settings
- `.env.test` - Test settings  
- `.env.staging` - Staging settings
- `.env.production` - Production settings

### Database Management

```bash
# Create database for specific environment
python scripts/database_manager.py development create

# Seed test data (development/staging only)
python scripts/database_manager.py development seed

# Get database statistics
python scripts/database_manager.py development stats

# Backup database
python scripts/database_manager.py production backup
```

## Environment Details

### Development Environment
- **Port**: 5000
- **Database**: SQLite local file
- **Debug**: Enabled
- **Hot reload**: Enabled
- **CORS**: Permissive (*)
- **Rate limiting**: Disabled

### Test Environment  
- **Port**: 5002
- **Database**: In-memory SQLite
- **Debug**: Disabled
- **OpenAI**: Mocked responses
- **Rate limiting**: Disabled
- **Purpose**: Automated testing

### Staging Environment
- **Port**: 5001
- **Database**: Staging PostgreSQL
- **Debug**: Disabled
- **Workers**: 2
- **Rate limiting**: Moderate (200/min)
- **CORS**: Staging domains only

### Production Environment
- **Port**: 5000
- **Database**: Production PostgreSQL
- **Debug**: Disabled
- **Workers**: 4
- **Rate limiting**: Strict (100/min)
- **CORS**: Production domains only
- **Security**: Full validation

## Required Environment Variables

### Development
- `SECRET_KEY` (auto-generated for dev)
- `DATABASE_URL` (defaults to SQLite)

### Staging
- `STAGING_SECRET_KEY` (required)
- `STAGING_DATABASE_URL` (required)
- `STAGING_OPENAI_API_KEY` (required)

### Production
- `SECRET_KEY` (required, 256-bit)
- `DATABASE_URL` (required)
- `OPENAI_API_KEY` (required)

## Security Notes

1. **Never use development secrets in production**
2. **Production environment variables must be properly secured**
3. **Staging should mirror production configuration**
4. **Test environment uses mock data only**

## Deployment Workflow

1. **Development** → Develop and test locally
2. **Test** → Run automated test suite
3. **Staging** → Deploy for integration testing
4. **Production** → Deploy live application

## Monitoring

Each environment provides health check endpoints:

```bash
GET /health
{
  "status": "healthy",
  "database": "connected", 
  "arabic_support": "enabled",
  "environment": "production"
}
```

## Troubleshooting

### Common Issues

1. **Missing environment variables**
   ```bash
   # Check required variables
   python scripts/env_manager.py list
   ```

2. **Database connection errors**
   ```bash
   # Check database status
   python scripts/database_manager.py development stats
   ```

3. **Port conflicts**
   - Development: 5000
   - Staging: 5001  
   - Test: 5002

### Log Locations

- Development: Console output
- Staging: Application logs + file
- Production: Structured logging with rotation