#!/bin/bash
# Setup cron jobs for database maintenance

# Base directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Log function
log() {
    echo -e "\e[1;34m[RPGer DB]\e[0m $1"
}

# Check if running as root
if [ "$(id -u)" -ne 0 ]; then
    log "This script must be run as root to set up cron jobs"
    exit 1
fi

# Create temporary crontab file
TEMP_CRONTAB=$(mktemp)

# Add header
cat > "$TEMP_CRONTAB" << EOL
# RPGer Database Maintenance Cron Jobs
# Automatically generated - do not edit directly

# Environment variables
MONGO_USERNAME=admin
MONGO_PASSWORD=password
REDIS_PASSWORD=password

EOL

# Add daily backup job (runs at 2 AM)
cat >> "$TEMP_CRONTAB" << EOL
# Daily database backup at 2 AM
0 2 * * * $BASE_DIR/backup-scripts/backup-databases.sh >> /data2/rpger/logs/backup.log 2>&1

EOL

# Add health check job (runs every hour)
cat >> "$TEMP_CRONTAB" << EOL
# Hourly health check
0 * * * * $BASE_DIR/health-check-scripts/database-health-check.sh >> /data2/rpger/logs/health-check.log 2>&1

EOL

# Install crontab
log "Installing cron jobs..."
crontab "$TEMP_CRONTAB"

# Clean up
rm "$TEMP_CRONTAB"

log "Cron jobs installed successfully"
log "Backup will run daily at 2 AM"
log "Health check will run hourly"

exit 0
