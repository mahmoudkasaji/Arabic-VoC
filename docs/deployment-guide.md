# Production Deployment Guide

## Overview

This guide covers the complete deployment process for the Arabic Voice of Customer platform in production environments, including infrastructure setup, monitoring, and maintenance procedures.

## Pre-Deployment Checklist

### Infrastructure Requirements

#### Minimum System Requirements
- **CPU**: 4 cores (2.0 GHz+)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 100GB SSD storage
- **Network**: 1Gbps connection
- **OS**: Ubuntu 20.04+ or CentOS 8+

#### Database Requirements
- **PostgreSQL**: Version 13+ with Arabic collation support
- **Memory**: 4GB dedicated RAM
- **Storage**: 50GB+ for data, 20GB for logs
- **Connections**: 100+ concurrent connections
- **Extensions**: Required extensions installed

#### External Dependencies
- **OpenAI API**: Valid API key with sufficient quota
- **Redis**: Version 6+ for caching (optional but recommended)
- **Load Balancer**: nginx or HAProxy for production
- **SSL Certificate**: Valid SSL certificate for HTTPS

### Security Prerequisites

#### Environment Variables
```bash
# Required environment variables
export SECRET_KEY="your-256-bit-secret-key"
export JWT_SECRET_KEY="your-jwt-secret-key"
export DATABASE_URL="postgresql://user:pass@host:5432/dbname"
export OPENAI_API_KEY="sk-your-openai-api-key"
export REDIS_URL="redis://localhost:6379/0"

# Optional configuration
export ENVIRONMENT="production"
export LOG_LEVEL="INFO"
export WORKER_PROCESSES="4"
export MAX_REQUESTS="1000"
```

#### Firewall Configuration
```bash
# Allow HTTP and HTTPS traffic
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow SSH (change port if needed)
sudo ufw allow 22/tcp

# Database access (if external)
sudo ufw allow from 10.0.0.0/8 to any port 5432

# Enable firewall
sudo ufw --force enable
```

## Step-by-Step Deployment

### 1. System Preparation

#### Update System
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.11 python3.11-venv python3-pip \
  postgresql-client redis-tools nginx supervisor \
  curl wget git htop

# Install Node.js for frontend assets (if needed)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

#### Create Application User
```bash
# Create dedicated user
sudo adduser --system --group --home /opt/arabic-voc arabic-voc
sudo usermod -a -G www-data arabic-voc

# Create directories
sudo mkdir -p /opt/arabic-voc/{app,logs,uploads,backups}
sudo chown -R arabic-voc:arabic-voc /opt/arabic-voc
```

### 2. Database Setup

#### PostgreSQL Installation and Configuration
```bash
# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Create database and user
sudo -u postgres psql << EOF
CREATE DATABASE arabic_voc_prod;
CREATE USER arabic_voc_user WITH ENCRYPTED PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE arabic_voc_prod TO arabic_voc_user;
ALTER DATABASE arabic_voc_prod OWNER TO arabic_voc_user;

-- Configure for Arabic text
ALTER DATABASE arabic_voc_prod SET timezone TO 'UTC';
\c arabic_voc_prod
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;
EOF
```

#### Database Tuning for Arabic Text
```bash
# Edit PostgreSQL configuration
sudo nano /etc/postgresql/13/main/postgresql.conf

# Add/modify these settings:
shared_buffers = 2GB
effective_cache_size = 6GB
maintenance_work_mem = 512MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200

# For Arabic text performance
log_min_duration_statement = 1000
track_activity_query_size = 2048
```

### 3. Application Deployment

#### Clone and Setup Application
```bash
# Switch to application user
sudo -u arabic-voc -i

# Clone repository
cd /opt/arabic-voc
git clone https://github.com/your-org/arabic-voc-platform.git app
cd app

# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn supervisor
```

#### Configuration Files
```bash
# Create production configuration
cat > /opt/arabic-voc/app/production.env << EOF
ENVIRONMENT=production
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
DATABASE_URL=postgresql://arabic_voc_user:secure_password@localhost:5432/arabic_voc_prod
OPENAI_API_KEY=sk-your-openai-api-key
REDIS_URL=redis://localhost:6379/0
LOG_LEVEL=INFO
WORKER_PROCESSES=4
MAX_REQUESTS=1000
CORS_ORIGINS=https://your-domain.com,https://www.your-domain.com
EOF

# Set permissions
chmod 600 /opt/arabic-voc/app/production.env
```

#### Database Migration
```bash
# Run database initialization
source venv/bin/activate
source production.env
python -c "
from utils.database_arabic import init_db
init_db()
print('Database initialized successfully')
"

# Verify database setup
python -c "
from utils.database_arabic import arabic_db_manager
import asyncio
async def test_db():
    async with arabic_db_manager.session_factory() as session:
        result = await session.execute('SELECT version()')
        print(f'Database version: {result.fetchone()[0]}')
asyncio.run(test_db())
"
```

### 4. Web Server Configuration

#### Nginx Configuration
```bash
# Create nginx configuration
sudo tee /etc/nginx/sites-available/arabic-voc << EOF
upstream arabic_voc_app {
    server 127.0.0.1:8000 fail_timeout=0;
    server 127.0.0.1:8001 fail_timeout=0;
    server 127.0.0.1:8002 fail_timeout=0;
    server 127.0.0.1:8003 fail_timeout=0;
}

server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    
    # Redirect to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss application/atom+xml image/svg+xml;
    
    # Client max body size (for file uploads)
    client_max_body_size 10M;
    
    # Static files
    location /static/ {
        alias /opt/arabic-voc/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        
        # Arabic font files
        location ~* \.(woff|woff2|ttf|eot)$ {
            add_header Access-Control-Allow-Origin "*";
            expires 1y;
        }
    }
    
    # WebSocket support
    location /api/analytics/realtime/ws {
        proxy_pass http://arabic_voc_app;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }
    
    # Application
    location / {
        proxy_pass http://arabic_voc_app;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }
    
    # Health check
    location /health {
        access_log off;
        proxy_pass http://arabic_voc_app;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/arabic-voc /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test and reload nginx
sudo nginx -t
sudo systemctl reload nginx
```

### 5. Process Management

#### Supervisor Configuration
```bash
# Create supervisor configuration
sudo tee /etc/supervisor/conf.d/arabic-voc.conf << EOF
[group:arabic-voc]
programs=arabic-voc-8000,arabic-voc-8001,arabic-voc-8002,arabic-voc-8003

[program:arabic-voc-8000]
command=/opt/arabic-voc/app/venv/bin/gunicorn --bind 127.0.0.1:8000 --workers 2 --worker-class uvicorn.workers.UvicornWorker --timeout 120 --keepalive 2 --max-requests 1000 --max-requests-jitter 100 main:app
directory=/opt/arabic-voc/app
environment=PATH="/opt/arabic-voc/app/venv/bin"
user=arabic-voc
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/opt/arabic-voc/logs/app-8000.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=5

[program:arabic-voc-8001]
command=/opt/arabic-voc/app/venv/bin/gunicorn --bind 127.0.0.1:8001 --workers 2 --worker-class uvicorn.workers.UvicornWorker --timeout 120 --keepalive 2 --max-requests 1000 --max-requests-jitter 100 main:app
directory=/opt/arabic-voc/app
environment=PATH="/opt/arabic-voc/app/venv/bin"
user=arabic-voc
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/opt/arabic-voc/logs/app-8001.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=5

[program:arabic-voc-8002]
command=/opt/arabic-voc/app/venv/bin/gunicorn --bind 127.0.0.1:8002 --workers 2 --worker-class uvicorn.workers.UvicornWorker --timeout 120 --keepalive 2 --max-requests 1000 --max-requests-jitter 100 main:app
directory=/opt/arabic-voc/app
environment=PATH="/opt/arabic-voc/app/venv/bin"
user=arabic-voc
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/opt/arabic-voc/logs/app-8002.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=5

[program:arabic-voc-8003]
command=/opt/arabic-voc/app/venv/bin/gunicorn --bind 127.0.0.1:8003 --workers 2 --worker-class uvicorn.workers.UvicornWorker --timeout 120 --keepalive 2 --max-requests 1000 --max-requests-jitter 100 main:app
directory=/opt/arabic-voc/app
environment=PATH="/opt/arabic-voc/app/venv/bin"
user=arabic-voc
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/opt/arabic-voc/logs/app-8003.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=5

[program:arabic-voc-monitor]
command=/opt/arabic-voc/app/venv/bin/python scripts/monitoring.py
directory=/opt/arabic-voc/app
environment=PATH="/opt/arabic-voc/app/venv/bin"
user=arabic-voc
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/opt/arabic-voc/logs/monitor.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=3
EOF

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start arabic-voc:*
```

### 6. Monitoring Setup

#### Create Monitoring Script
```bash
# Create monitoring script
cat > /opt/arabic-voc/app/scripts/monitoring.py << 'EOF'
#!/usr/bin/env python3
"""
Production monitoring daemon
"""

import asyncio
import logging
import os
import sys

# Add app directory to Python path
sys.path.insert(0, '/opt/arabic-voc/app')

from deployment.monitoring import start_production_monitoring
from deployment.production_config import get_config

async def main():
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load configuration
    config = get_config()
    
    # Start monitoring
    await start_production_monitoring(config)

if __name__ == "__main__":
    asyncio.run(main())
EOF

chmod +x /opt/arabic-voc/app/scripts/monitoring.py
```

#### Log Rotation
```bash
# Create logrotate configuration
sudo tee /etc/logrotate.d/arabic-voc << EOF
/opt/arabic-voc/logs/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 arabic-voc arabic-voc
    postrotate
        supervisorctl restart arabic-voc:*
    endscript
}
EOF
```

### 7. Backup Configuration

#### Database Backup Script
```bash
# Create backup script
cat > /opt/arabic-voc/app/scripts/backup.sh << 'EOF'
#!/bin/bash
# Arabic VoC Database Backup Script

BACKUP_DIR="/opt/arabic-voc/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="arabic_voc_prod"
DB_USER="arabic_voc_user"

# Create backup directory
mkdir -p $BACKUP_DIR

# Database backup
pg_dump -h localhost -U $DB_USER -d $DB_NAME \
  --no-password --verbose --clean --create \
  | gzip > $BACKUP_DIR/db_backup_$DATE.sql.gz

# Application backup (configuration and uploads)
tar -czf $BACKUP_DIR/app_backup_$DATE.tar.gz \
  -C /opt/arabic-voc \
  app/production.env \
  uploads/

# Remove backups older than 30 days
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /opt/arabic-voc/app/scripts/backup.sh

# Setup cron job for daily backups
sudo -u arabic-voc crontab -l > /tmp/crontab-arabic-voc
echo "0 2 * * * /opt/arabic-voc/app/scripts/backup.sh >> /opt/arabic-voc/logs/backup.log 2>&1" >> /tmp/crontab-arabic-voc
sudo -u arabic-voc crontab /tmp/crontab-arabic-voc
rm /tmp/crontab-arabic-voc
```

### 8. SSL Certificate Setup

#### Let's Encrypt Installation
```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Test automatic renewal
sudo certbot renew --dry-run

# Setup automatic renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

## Post-Deployment Verification

### 1. Health Checks

#### Application Health
```bash
# Check application status
curl -f http://localhost:8000/health
curl -f https://your-domain.com/health

# Check WebSocket connection
wscat -c wss://your-domain.com/api/analytics/realtime/ws

# Check Arabic text processing
curl -X POST https://your-domain.com/api/feedback/submit \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{"content": "اختبار النظام", "channel": "website"}'
```

#### Database Health
```bash
# Check database connections
sudo -u postgres psql -c "SELECT count(*) FROM pg_stat_activity WHERE datname='arabic_voc_prod';"

# Check Arabic text storage
sudo -u postgres psql -d arabic_voc_prod -c "SELECT content FROM feedback LIMIT 1;"
```

### 2. Performance Testing

#### Load Testing
```bash
# Install load testing tools
pip install locust

# Create load test script
cat > /opt/arabic-voc/app/scripts/load_test.py << 'EOF'
from locust import HttpUser, task, between

class ArabicVoCUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login and get token
        response = self.client.post("/api/auth/login", json={
            "username": "test_user",
            "password": "test_password"
        })
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def view_dashboard(self):
        self.client.get("/", headers=self.headers)
    
    @task(2)
    def submit_feedback(self):
        self.client.post("/api/feedback/submit", 
            headers=self.headers,
            json={
                "content": "الخدمة ممتازة جداً",
                "channel": "website",
                "rating": 5
            })
    
    @task(1)
    def get_analytics(self):
        self.client.get("/api/analytics/realtime/dashboard", 
                       headers=self.headers)
EOF

# Run load test
cd /opt/arabic-voc/app/scripts
locust -f load_test.py --host=https://your-domain.com
```

### 3. Security Verification

#### Security Scan
```bash
# Check SSL configuration
curl -I https://your-domain.com

# Test security headers
curl -I https://your-domain.com | grep -E "(X-Frame-Options|X-Content-Type-Options|Strict-Transport-Security)"

# Check for common vulnerabilities
nmap -sV --script=vuln your-domain.com
```

## Maintenance Procedures

### Daily Tasks
- Monitor application logs
- Check system resource usage
- Verify backup completion
- Review performance metrics

### Weekly Tasks
- Analyze performance trends
- Review security logs
- Update system packages
- Database maintenance (VACUUM, ANALYZE)

### Monthly Tasks
- Security updates
- Certificate renewal check
- Capacity planning review
- Disaster recovery testing

### Quarterly Tasks
- Full security audit
- Performance optimization
- Documentation updates
- Backup restore testing

## Troubleshooting

### Common Issues

#### High CPU Usage
```bash
# Identify CPU-intensive processes
top -p $(pgrep -d',' -f arabic-voc)

# Check database queries
sudo -u postgres psql -d arabic_voc_prod -c "SELECT query, state, query_start FROM pg_stat_activity WHERE state = 'active';"

# Scale horizontally if needed
sudo supervisorctl start arabic-voc-8004
```

#### Memory Issues
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head -20

# Restart application processes
sudo supervisorctl restart arabic-voc:*

# Database memory tuning
sudo nano /etc/postgresql/13/main/postgresql.conf
```

#### WebSocket Connection Issues
```bash
# Check nginx WebSocket configuration
sudo nginx -T | grep -A 10 -B 10 websocket

# Test WebSocket directly
curl -i -N -H "Connection: Upgrade" -H "Upgrade: websocket" \
  -H "Sec-WebSocket-Version: 13" -H "Sec-WebSocket-Key: test" \
  http://localhost:8000/api/analytics/realtime/ws
```

## Emergency Procedures

### Application Recovery
```bash
# Quick restart
sudo supervisorctl restart arabic-voc:*

# Database failover (if using replication)
sudo systemctl stop postgresql
sudo systemctl start postgresql

# Emergency maintenance mode
sudo nginx -s stop
echo "Maintenance in progress" | sudo tee /var/www/html/index.html
sudo python3 -m http.server 80
```

### Data Recovery
```bash
# Restore from backup
gunzip < /opt/arabic-voc/backups/db_backup_YYYYMMDD_HHMMSS.sql.gz | \
  sudo -u postgres psql -d arabic_voc_prod

# Application data restore
tar -xzf /opt/arabic-voc/backups/app_backup_YYYYMMDD_HHMMSS.tar.gz \
  -C /opt/arabic-voc/
```

---

This deployment guide ensures a robust, scalable, and secure production environment for the Arabic Voice of Customer platform with comprehensive monitoring and maintenance procedures.