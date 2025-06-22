# Deployment Guide

## Overview
This folder contains all deployment and operations related files for the Arabic VoC Platform.

## Structure
- `scripts/` - Deployment automation scripts
- `monitoring/` - System monitoring and health checks  
- `environments/` - Environment-specific configuration templates

## Quick Deploy
```bash
# Production deployment
./scripts/deploy_production.sh

# Staging deployment  
./scripts/deploy_staging.sh
```

## Environment Setup
1. Copy appropriate environment template from `environments/`
2. Fill in required values
3. Run deployment script

For detailed instructions, see the deployment documentation.