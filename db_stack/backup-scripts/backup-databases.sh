#!/bin/bash
# Database backup script for RPGer

# Set the base directory for backups
BACKUP_DIR="/data2/rpger/backups"
DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_PATH="$BACKUP_DIR/$DATE"

# Create backup directory
mkdir -p "$BACKUP_PATH"

# Log function
log() {
    echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $1" | tee -a "$BACKUP_DIR/backup.log"
}

# Backup MongoDB
backup_mongodb() {
    log "Starting MongoDB backup..."
    
    # Create MongoDB backup directory
    mkdir -p "$BACKUP_PATH/mongodb"
    
    # Get MongoDB credentials from environment or use defaults
    MONGO_USER=${MONGO_USERNAME:-admin}
    MONGO_PASS=${MONGO_PASSWORD:-password}
    
    # Run mongodump
    docker exec rpger-mongodb mongodump \
        --host localhost \
        --port 27017 \
        --username "$MONGO_USER" \
        --password "$MONGO_PASS" \
        --authenticationDatabase admin \
        --out /tmp/mongodb_backup
    
    # Copy backup from container to host
    docker cp rpger-mongodb:/tmp/mongodb_backup "$BACKUP_PATH/mongodb"
    
    # Clean up temporary files in container
    docker exec rpger-mongodb rm -rf /tmp/mongodb_backup
    
    log "MongoDB backup completed"
}

# Backup Redis
backup_redis() {
    log "Starting Redis backup..."
    
    # Create Redis backup directory
    mkdir -p "$BACKUP_PATH/redis"
    
    # Trigger Redis to save its data
    docker exec rpger-redis redis-cli -a "${REDIS_PASSWORD:-password}" SAVE
    
    # Copy the dump.rdb file
    docker cp rpger-redis:/data/dump.rdb "$BACKUP_PATH/redis/"
    
    # Copy the appendonly.aof file if it exists
    docker cp rpger-redis:/data/appendonly.aof "$BACKUP_PATH/redis/" 2>/dev/null || true
    
    log "Redis backup completed"
}

# Backup Chroma
backup_chroma() {
    log "Starting Chroma backup..."
    
    # Create Chroma backup directory
    mkdir -p "$BACKUP_PATH/chroma"
    
    # Stop Chroma container to ensure data consistency
    docker stop rpger-chroma
    
    # Copy Chroma data
    cp -r /data2/rpger/chroma/* "$BACKUP_PATH/chroma/"
    
    # Restart Chroma container
    docker start rpger-chroma
    
    log "Chroma backup completed"
}

# Rotate backups (keep last 7 daily backups)
rotate_backups() {
    log "Rotating backups..."
    
    # List all backup directories sorted by date (oldest first)
    BACKUPS=$(ls -1tr "$BACKUP_DIR" | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}-[0-9]{2}-[0-9]{2}$')
    
    # Count backups
    BACKUP_COUNT=$(echo "$BACKUPS" | wc -l)
    
    # If we have more than 7 backups, remove the oldest ones
    if [ "$BACKUP_COUNT" -gt 7 ]; then
        REMOVE_COUNT=$((BACKUP_COUNT - 7))
        REMOVE_BACKUPS=$(echo "$BACKUPS" | head -n "$REMOVE_COUNT")
        
        for backup in $REMOVE_BACKUPS; do
            log "Removing old backup: $backup"
            rm -rf "$BACKUP_DIR/$backup"
        done
    fi
    
    log "Backup rotation completed"
}

# Main execution
log "Starting database backup process"

# Run backups
backup_mongodb
backup_redis
backup_chroma

# Rotate old backups
rotate_backups

log "Backup process completed successfully"

# Set appropriate permissions
chmod -R 755 "$BACKUP_PATH"

exit 0
