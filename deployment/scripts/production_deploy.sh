#!/bin/bash

# Production Deployment Script for Arabic VoC Platform
# Comprehensive deployment with safety checks and rollback capability

set -euo pipefail

# Configuration
DEPLOYMENT_DIR="/opt/arabic-voc"
BACKUP_DIR="/opt/backups/arabic-voc"
SERVICE_NAME="arabic-voc"
HEALTH_CHECK_URL="http://localhost:5000/api/health"
MAX_DEPLOY_TIME=600  # 10 minutes

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Pre-deployment validation
validate_environment() {
    log "Validating deployment environment..."
    
    # Check required environment variables
    local required_vars=("DATABASE_URL" "OPENAI_API_KEY" "SECRET_KEY")
    for var in "${required_vars[@]}"; do
        if [[ -z "${!var:-}" ]]; then
            error "Required environment variable $var is not set"
            exit 1
        fi
    done
    
    # Check disk space
    local available_space=$(df / | awk 'NR==2 {print $4}')
    if [[ $available_space -lt 1048576 ]]; then  # 1GB in KB
        error "Insufficient disk space. Need at least 1GB free."
        exit 1
    fi
    
    # Check database connectivity
    if ! python3 -c "
import psycopg2
import os
try:
    conn = psycopg2.connect(os.environ['DATABASE_URL'])
    conn.close()
    print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
    "; then
        error "Database connectivity check failed"
        exit 1
    fi
    
    success "Environment validation passed"
}

# Create backup of current deployment
create_backup() {
    log "Creating backup of current deployment..."
    
    local backup_timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_path="${BACKUP_DIR}/backup_${backup_timestamp}"
    
    mkdir -p "$backup_path"
    
    # Backup application code
    if [[ -d "$DEPLOYMENT_DIR" ]]; then
        cp -r "$DEPLOYMENT_DIR" "$backup_path/app"
    fi
    
    # Backup database
    log "Creating database backup..."
    pg_dump "$DATABASE_URL" > "$backup_path/database_backup.sql"
    
    # Store backup path for potential rollback
    echo "$backup_path" > /tmp/last_backup_path
    
    success "Backup created at $backup_path"
}

# Install dependencies and prepare environment
prepare_deployment() {
    log "Preparing deployment environment..."
    
    # Create deployment directory
    mkdir -p "$DEPLOYMENT_DIR"
    cd "$DEPLOYMENT_DIR"
    
    # Install system dependencies
    sudo apt-get update
    sudo apt-get install -y python3-pip python3-venv nginx postgresql-client
    
    # Create Python virtual environment
    python3 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip and install Python dependencies
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Install additional production dependencies
    pip install gunicorn supervisor
    
    success "Deployment environment prepared"
}

# Deploy application code
deploy_application() {
    log "Deploying application code..."
    
    cd "$DEPLOYMENT_DIR"
    source venv/bin/activate
    
    # Run database migrations if needed
    python app/main.py --migrate || true
    
    # Collect static files
    if [[ -d "static" ]]; then
        mkdir -p /var/www/arabic-voc/static
        cp -r static/* /var/www/arabic-voc/static/
    fi
    
    # Set proper permissions
    chown -R www-data:www-data "$DEPLOYMENT_DIR"
    chmod -R 755 "$DEPLOYMENT_DIR"
    
    success "Application code deployed"
}

# Configure and start services
configure_services() {
    log "Configuring system services..."
    
    # Configure Gunicorn
    cat > /etc/supervisor/conf.d/arabic-voc.conf << EOF
[program:arabic-voc]
command=${DEPLOYMENT_DIR}/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 3 --timeout 120 app.main:app
directory=${DEPLOYMENT_DIR}
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/arabic-voc/app.log
environment=PATH="${DEPLOYMENT_DIR}/venv/bin",DATABASE_URL="${DATABASE_URL}",OPENAI_API_KEY="${OPENAI_API_KEY}",SECRET_KEY="${SECRET_KEY}"
EOF
    
    # Configure Nginx
    cat > /etc/nginx/sites-available/arabic-voc << EOF
server {
    listen 80;
    server_name _;
    
    client_max_body_size 50M;
    
    location /static/ {
        alias /var/www/arabic-voc/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 300;
    }
}
EOF
    
    # Enable Nginx site
    ln -sf /etc/nginx/sites-available/arabic-voc /etc/nginx/sites-enabled/
    rm -f /etc/nginx/sites-enabled/default
    
    # Test Nginx configuration
    nginx -t
    
    # Create log directories
    mkdir -p /var/log/arabic-voc
    chown www-data:www-data /var/log/arabic-voc
    
    success "Services configured"
}

# Start services
start_services() {
    log "Starting services..."
    
    # Reload supervisor configuration
    supervisorctl reread
    supervisorctl update
    
    # Start application
    supervisorctl start arabic-voc
    
    # Restart Nginx
    systemctl restart nginx
    
    # Enable services to start on boot
    systemctl enable nginx
    systemctl enable supervisor
    
    success "Services started"
}

# Health check with timeout
health_check() {
    log "Performing health checks..."
    
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if curl -f -s "$HEALTH_CHECK_URL" > /dev/null; then
            success "Health check passed"
            return 0
        fi
        
        log "Health check attempt $attempt/$max_attempts failed, retrying in 10 seconds..."
        sleep 10
        ((attempt++))
    done
    
    error "Health check failed after $max_attempts attempts"
    return 1
}

# Rollback to previous version
rollback() {
    error "Deployment failed, initiating rollback..."
    
    if [[ -f "/tmp/last_backup_path" ]]; then
        local backup_path=$(cat /tmp/last_backup_path)
        
        if [[ -d "$backup_path" ]]; then
            log "Rolling back to backup: $backup_path"
            
            # Stop services
            supervisorctl stop arabic-voc || true
            
            # Restore application
            rm -rf "$DEPLOYMENT_DIR"
            cp -r "$backup_path/app" "$DEPLOYMENT_DIR"
            
            # Restore database
            if [[ -f "$backup_path/database_backup.sql" ]]; then
                psql "$DATABASE_URL" < "$backup_path/database_backup.sql"
            fi
            
            # Restart services
            supervisorctl start arabic-voc
            
            success "Rollback completed"
        else
            error "Backup path not found: $backup_path"
        fi
    else
        error "No backup information found for rollback"
    fi
}

# Main deployment function
main() {
    log "Starting production deployment of Arabic VoC Platform..."
    
    # Set trap for cleanup on failure
    trap rollback ERR
    
    # Deployment steps
    validate_environment
    create_backup
    prepare_deployment
    deploy_application
    configure_services
    start_services
    
    # Final health check
    if health_check; then
        success "Deployment completed successfully!"
        
        # Clean up old backups (keep last 5)
        find "$BACKUP_DIR" -maxdepth 1 -type d -name "backup_*" | sort -r | tail -n +6 | xargs rm -rf
        
        log "Deployment summary:"
        log "- Application: Running on port 5000"
        log "- Web server: Nginx configured as reverse proxy"
        log "- Logs: /var/log/arabic-voc/"
        log "- Health check: $HEALTH_CHECK_URL"
        
    else
        error "Deployment validation failed"
        exit 1
    fi
}

# Run deployment
main "$@"