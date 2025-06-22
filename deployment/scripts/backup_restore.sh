#!/bin/bash

# Backup and Restore System for Arabic VoC Platform
# Comprehensive data protection and disaster recovery

set -euo pipefail

BACKUP_BASE_DIR="/opt/backups/arabic-voc"
RETENTION_DAYS=30
DB_NAME="arabicvoc"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Create comprehensive backup
create_backup() {
    local backup_type="${1:-manual}"
    local backup_timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_dir="${BACKUP_BASE_DIR}/${backup_type}_${backup_timestamp}"
    
    log "Creating $backup_type backup..."
    mkdir -p "$backup_dir"
    
    # Backup database with compression
    log "Backing up database..."
    pg_dump "$DATABASE_URL" | gzip > "$backup_dir/database.sql.gz"
    
    # Backup application files
    log "Backing up application files..."
    tar -czf "$backup_dir/application.tar.gz" -C /opt/arabic-voc .
    
    # Backup configuration files
    log "Backing up configuration..."
    mkdir -p "$backup_dir/config"
    cp /etc/supervisor/conf.d/arabic-voc.conf "$backup_dir/config/" 2>/dev/null || true
    cp /etc/nginx/sites-available/arabic-voc "$backup_dir/config/" 2>/dev/null || true
    
    # Backup logs (last 7 days)
    log "Backing up recent logs..."
    if [[ -d "/var/log/arabic-voc" ]]; then
        find /var/log/arabic-voc -name "*.log" -mtime -7 -exec cp {} "$backup_dir/" \;
    fi
    
    # Create backup manifest
    cat > "$backup_dir/MANIFEST" << EOF
Backup Type: $backup_type
Created: $(date -u +%Y-%m-%dT%H:%M:%SZ)
Database: $(pg_dump --version | head -1)
Platform Version: $(cat /opt/arabic-voc/VERSION 2>/dev/null || echo "Unknown")
System: $(uname -a)
Disk Usage: $(du -sh "$backup_dir" | cut -f1)
EOF
    
    # Calculate checksums
    log "Calculating checksums..."
    cd "$backup_dir"
    find . -type f -exec sha256sum {} \; > checksums.sha256
    
    success "Backup created: $backup_dir"
    echo "$backup_dir"
}

# Restore from backup
restore_backup() {
    local backup_path="$1"
    local restore_type="${2:-full}"
    
    if [[ ! -d "$backup_path" ]]; then
        error "Backup directory not found: $backup_path"
        exit 1
    fi
    
    log "Restoring from backup: $backup_path"
    
    # Verify backup integrity
    if ! verify_backup "$backup_path"; then
        error "Backup verification failed"
        exit 1
    fi
    
    # Create pre-restore backup
    log "Creating pre-restore backup..."
    local pre_restore_backup=$(create_backup "pre-restore")
    
    case "$restore_type" in
        "full")
            restore_full "$backup_path"
            ;;
        "database-only")
            restore_database_only "$backup_path"
            ;;
        "application-only")
            restore_application_only "$backup_path"
            ;;
        *)
            error "Unknown restore type: $restore_type"
            exit 1
            ;;
    esac
    
    success "Restore completed successfully"
    log "Pre-restore backup saved at: $pre_restore_backup"
}

# Full system restore
restore_full() {
    local backup_path="$1"
    
    log "Performing full system restore..."
    
    # Stop services
    log "Stopping services..."
    supervisorctl stop arabic-voc || true
    systemctl stop nginx || true
    
    # Restore database
    restore_database_only "$backup_path"
    
    # Restore application
    restore_application_only "$backup_path"
    
    # Restore configuration
    log "Restoring configuration..."
    if [[ -f "$backup_path/config/arabic-voc.conf" ]]; then
        cp "$backup_path/config/arabic-voc.conf" /etc/supervisor/conf.d/
    fi
    
    if [[ -f "$backup_path/config/arabic-voc" ]]; then
        cp "$backup_path/config/arabic-voc" /etc/nginx/sites-available/
    fi
    
    # Restart services
    log "Restarting services..."
    supervisorctl reread
    supervisorctl update
    supervisorctl start arabic-voc
    systemctl start nginx
    
    # Health check
    sleep 10
    if curl -f -s "http://localhost:5000/api/health" > /dev/null; then
        success "System restore completed and health check passed"
    else
        warning "System restored but health check failed"
    fi
}

# Database-only restore
restore_database_only() {
    local backup_path="$1"
    
    log "Restoring database..."
    
    if [[ ! -f "$backup_path/database.sql.gz" ]]; then
        error "Database backup file not found"
        exit 1
    fi
    
    # Create temporary restore database
    local temp_db="arabicvoc_restore_$(date +%s)"
    createdb "$temp_db" || true
    
    # Restore to temporary database first
    log "Restoring to temporary database for validation..."
    gunzip -c "$backup_path/database.sql.gz" | psql "$temp_db"
    
    # Validate restored data
    local record_count=$(psql -t -c "SELECT COUNT(*) FROM feedback;" "$temp_db" 2>/dev/null || echo "0")
    log "Restored database contains $record_count feedback records"
    
    # Drop temporary database and restore to production
    dropdb "$temp_db"
    
    log "Restoring to production database..."
    gunzip -c "$backup_path/database.sql.gz" | psql "$DATABASE_URL"
    
    success "Database restore completed"
}

# Application-only restore
restore_application_only() {
    local backup_path="$1"
    
    log "Restoring application files..."
    
    if [[ ! -f "$backup_path/application.tar.gz" ]]; then
        error "Application backup file not found"
        exit 1
    fi
    
    # Stop application service
    supervisorctl stop arabic-voc || true
    
    # Backup current application
    if [[ -d "/opt/arabic-voc" ]]; then
        mv /opt/arabic-voc "/opt/arabic-voc.backup.$(date +%s)"
    fi
    
    # Restore application files
    mkdir -p /opt/arabic-voc
    tar -xzf "$backup_path/application.tar.gz" -C /opt/arabic-voc
    
    # Set permissions
    chown -R www-data:www-data /opt/arabic-voc
    chmod -R 755 /opt/arabic-voc
    
    # Restart application
    supervisorctl start arabic-voc
    
    success "Application restore completed"
}

# Verify backup integrity
verify_backup() {
    local backup_path="$1"
    
    log "Verifying backup integrity..."
    
    # Check required files
    local required_files=("database.sql.gz" "application.tar.gz" "MANIFEST" "checksums.sha256")
    for file in "${required_files[@]}"; do
        if [[ ! -f "$backup_path/$file" ]]; then
            error "Required backup file missing: $file"
            return 1
        fi
    done
    
    # Verify checksums
    cd "$backup_path"
    if ! sha256sum -c checksums.sha256 --quiet; then
        error "Checksum verification failed"
        return 1
    fi
    
    # Test database backup
    if ! gunzip -t database.sql.gz; then
        error "Database backup file is corrupted"
        return 1
    fi
    
    # Test application backup
    if ! tar -tzf application.tar.gz > /dev/null; then
        error "Application backup file is corrupted"
        return 1
    fi
    
    success "Backup integrity verified"
    return 0
}

# List available backups
list_backups() {
    log "Available backups:"
    
    if [[ ! -d "$BACKUP_BASE_DIR" ]]; then
        warning "No backup directory found"
        return
    fi
    
    find "$BACKUP_BASE_DIR" -maxdepth 1 -type d -name "*_*" | sort -r | while read backup_dir; do
        if [[ -f "$backup_dir/MANIFEST" ]]; then
            local backup_name=$(basename "$backup_dir")
            local backup_size=$(du -sh "$backup_dir" | cut -f1)
            local backup_date=$(grep "Created:" "$backup_dir/MANIFEST" | cut -d' ' -f2-)
            
            echo "  $backup_name ($backup_size) - $backup_date"
        fi
    done
}

# Clean old backups
cleanup_old_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days..."
    
    local deleted_count=0
    
    find "$BACKUP_BASE_DIR" -maxdepth 1 -type d -name "*_*" -mtime +$RETENTION_DAYS | while read old_backup; do
        log "Removing old backup: $(basename "$old_backup")"
        rm -rf "$old_backup"
        ((deleted_count++))
    done
    
    if [[ $deleted_count -gt 0 ]]; then
        success "Removed $deleted_count old backups"
    else
        log "No old backups to remove"
    fi
}

# Automated backup with rotation
automated_backup() {
    log "Starting automated backup..."
    
    # Create backup
    local backup_path=$(create_backup "automated")
    
    # Cleanup old backups
    cleanup_old_backups
    
    # Send notification (if configured)
    if [[ -n "${BACKUP_NOTIFICATION_EMAIL:-}" ]]; then
        echo "Automated backup completed: $(basename "$backup_path")" | \
        mail -s "Arabic VoC Platform Backup Completed" "$BACKUP_NOTIFICATION_EMAIL"
    fi
    
    success "Automated backup completed"
}

# Show usage
usage() {
    cat << EOF
Arabic VoC Platform Backup and Restore System

Usage: $0 <command> [options]

Commands:
    backup [type]           Create backup (types: manual, automated)
    restore <path> [type]   Restore from backup (types: full, database-only, application-only)
    list                    List available backups
    verify <path>           Verify backup integrity
    cleanup                 Remove old backups
    automated               Run automated backup with cleanup

Examples:
    $0 backup manual
    $0 restore /opt/backups/arabic-voc/manual_20250622_120000 full
    $0 list
    $0 verify /opt/backups/arabic-voc/automated_20250622_060000
    $0 cleanup

Environment Variables:
    DATABASE_URL            PostgreSQL connection string
    BACKUP_NOTIFICATION_EMAIL   Email for backup notifications
EOF
}

# Main function
main() {
    case "${1:-}" in
        "backup")
            create_backup "${2:-manual}"
            ;;
        "restore")
            if [[ -z "${2:-}" ]]; then
                error "Backup path required for restore"
                usage
                exit 1
            fi
            restore_backup "$2" "${3:-full}"
            ;;
        "list")
            list_backups
            ;;
        "verify")
            if [[ -z "${2:-}" ]]; then
                error "Backup path required for verify"
                usage
                exit 1
            fi
            verify_backup "$2"
            ;;
        "cleanup")
            cleanup_old_backups
            ;;
        "automated")
            automated_backup
            ;;
        *)
            usage
            ;;
    esac
}

# Run with provided arguments
main "$@"