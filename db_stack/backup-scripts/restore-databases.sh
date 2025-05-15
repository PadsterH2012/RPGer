#!/bin/bash
# Database restoration script for RPGer

# Set the base directory for backups
BACKUP_DIR="/data2/rpger/backups"
LOG_DIR="/data2/rpger/logs"
RESTORE_LOG="$LOG_DIR/restore.log"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Log function
log() {
    echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $1" | tee -a "$RESTORE_LOG"
}

# Check if a backup directory exists
check_backup_dir() {
    local backup_date=$1
    local backup_path="$BACKUP_DIR/$backup_date"
    
    if [ ! -d "$backup_path" ]; then
        log "ERROR: Backup directory $backup_path does not exist"
        return 1
    fi
    
    log "Backup directory $backup_path exists"
    return 0
}

# Restore MongoDB
restore_mongodb() {
    local backup_date=$1
    local backup_path="$BACKUP_DIR/$backup_date/mongodb"
    
    log "Starting MongoDB restoration from $backup_path"
    
    # Check if MongoDB backup directory exists
    if [ ! -d "$backup_path" ]; then
        log "ERROR: MongoDB backup directory does not exist"
        return 1
    fi
    
    # Check if MongoDB container is running
    if ! docker ps | grep -q rpger-mongodb; then
        log "ERROR: MongoDB container is not running"
        return 1
    fi
    
    # Copy backup files to container
    log "Copying MongoDB backup files to container"
    docker cp "$backup_path/mongodb_backup" rpger-mongodb:/tmp/
    
    # Get MongoDB credentials from environment or use defaults
    MONGO_USER=${MONGO_USERNAME:-admin}
    MONGO_PASS=${MONGO_PASSWORD:-password}
    
    # Restore databases
    log "Restoring MongoDB databases"
    docker exec rpger-mongodb mongorestore \
        --host localhost \
        --port 27017 \
        --username "$MONGO_USER" \
        --password "$MONGO_PASS" \
        --authenticationDatabase admin \
        --drop \
        /tmp/mongodb_backup
    
    # Check if restoration was successful
    if [ $? -eq 0 ]; then
        log "MongoDB restoration completed successfully"
        
        # Clean up temporary files in container
        docker exec rpger-mongodb rm -rf /tmp/mongodb_backup
        
        return 0
    else
        log "ERROR: MongoDB restoration failed"
        
        # Clean up temporary files in container
        docker exec rpger-mongodb rm -rf /tmp/mongodb_backup
        
        return 1
    fi
}

# Restore Redis
restore_redis() {
    local backup_date=$1
    local backup_path="$BACKUP_DIR/$backup_date/redis"
    
    log "Starting Redis restoration from $backup_path"
    
    # Check if Redis backup directory exists
    if [ ! -d "$backup_path" ]; then
        log "ERROR: Redis backup directory does not exist"
        return 1
    fi
    
    # Check if Redis container is running
    if ! docker ps | grep -q rpger-redis; then
        log "ERROR: Redis container is not running"
        return 1
    fi
    
    # Stop Redis container
    log "Stopping Redis container"
    docker stop rpger-redis
    
    # Copy backup files to Redis data directory
    log "Copying Redis backup files to data directory"
    cp "$backup_path/dump.rdb" /data2/rpger/redis/
    
    # Copy appendonly.aof file if it exists
    if [ -f "$backup_path/appendonly.aof" ]; then
        cp "$backup_path/appendonly.aof" /data2/rpger/redis/
    fi
    
    # Start Redis container
    log "Starting Redis container"
    docker start rpger-redis
    
    # Wait for Redis to start
    sleep 5
    
    # Check if Redis is running
    if docker ps | grep -q rpger-redis; then
        log "Redis restoration completed successfully"
        return 0
    else
        log "ERROR: Redis container failed to start after restoration"
        return 1
    fi
}

# Restore Chroma
restore_chroma() {
    local backup_date=$1
    local backup_path="$BACKUP_DIR/$backup_date/chroma"
    
    log "Starting Chroma restoration from $backup_path"
    
    # Check if Chroma backup directory exists
    if [ ! -d "$backup_path" ]; then
        log "ERROR: Chroma backup directory does not exist"
        return 1
    fi
    
    # Check if Chroma container is running
    if ! docker ps | grep -q rpger-chroma; then
        log "ERROR: Chroma container is not running"
        return 1
    fi
    
    # Stop Chroma container
    log "Stopping Chroma container"
    docker stop rpger-chroma
    
    # Clear existing Chroma data
    log "Clearing existing Chroma data"
    rm -rf /data2/rpger/chroma/*
    
    # Copy backup files to Chroma data directory
    log "Copying Chroma backup files to data directory"
    cp -r "$backup_path"/* /data2/rpger/chroma/
    
    # Start Chroma container
    log "Starting Chroma container"
    docker start rpger-chroma
    
    # Wait for Chroma to start
    sleep 10
    
    # Check if Chroma is running
    if docker ps | grep -q rpger-chroma; then
        log "Chroma restoration completed successfully"
        return 0
    else
        log "ERROR: Chroma container failed to start after restoration"
        return 1
    fi
}

# Display usage information
usage() {
    echo "Usage: $0 [OPTIONS] [BACKUP_DATE]"
    echo
    echo "Restore databases from backup."
    echo
    echo "Options:"
    echo "  --mongodb-only    Restore only MongoDB"
    echo "  --redis-only      Restore only Redis"
    echo "  --chroma-only     Restore only Chroma"
    echo "  --help            Display this help message"
    echo
    echo "If BACKUP_DATE is not provided, the most recent backup will be used."
    echo "BACKUP_DATE format: YYYY-MM-DD_HH-MM-SS"
    echo
    echo "Examples:"
    echo "  $0                           # Restore all databases from the most recent backup"
    echo "  $0 2025-05-15_20-43-36       # Restore all databases from the specified backup"
    echo "  $0 --mongodb-only            # Restore only MongoDB from the most recent backup"
}

# Main execution
MONGODB_ONLY=0
REDIS_ONLY=0
CHROMA_ONLY=0

# Parse command line options
while [ $# -gt 0 ]; do
    case "$1" in
        --mongodb-only)
            MONGODB_ONLY=1
            shift
            ;;
        --redis-only)
            REDIS_ONLY=1
            shift
            ;;
        --chroma-only)
            CHROMA_ONLY=1
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            # Assume it's a backup date
            BACKUP_DATE="$1"
            shift
            ;;
    esac
done

# If no specific database is selected, restore all
if [ "$MONGODB_ONLY" -eq 0 ] && [ "$REDIS_ONLY" -eq 0 ] && [ "$CHROMA_ONLY" -eq 0 ]; then
    MONGODB_ONLY=1
    REDIS_ONLY=1
    CHROMA_ONLY=1
fi

# If no backup date is provided, use the most recent backup
if [ -z "$BACKUP_DATE" ]; then
    LATEST_BACKUP=$(ls -1tr "$BACKUP_DIR" | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}-[0-9]{2}-[0-9]{2}$' | tail -n 1)
    
    if [ -z "$LATEST_BACKUP" ]; then
        log "ERROR: No backups found in $BACKUP_DIR"
        exit 1
    fi
    
    BACKUP_DATE="$LATEST_BACKUP"
    log "Using latest backup: $BACKUP_DATE"
else
    log "Using specified backup: $BACKUP_DATE"
fi

# Check if the backup directory exists
if ! check_backup_dir "$BACKUP_DATE"; then
    log "ERROR: Cannot restore from backup $BACKUP_DATE"
    exit 1
fi

# Ask for confirmation
echo "WARNING: This will overwrite current database data with backup from $BACKUP_DATE"
echo "Press ENTER to continue or CTRL+C to abort"
read -r

# Initialize error counter
ERRORS=0

# Restore MongoDB if selected
if [ "$MONGODB_ONLY" -eq 1 ]; then
    if ! restore_mongodb "$BACKUP_DATE"; then
        ERRORS=$((ERRORS + 1))
    fi
fi

# Restore Redis if selected
if [ "$REDIS_ONLY" -eq 1 ]; then
    if ! restore_redis "$BACKUP_DATE"; then
        ERRORS=$((ERRORS + 1))
    fi
fi

# Restore Chroma if selected
if [ "$CHROMA_ONLY" -eq 1 ]; then
    if ! restore_chroma "$BACKUP_DATE"; then
        ERRORS=$((ERRORS + 1))
    fi
fi

# Report results
if [ "$ERRORS" -eq 0 ]; then
    log "All database restorations completed successfully"
    exit 0
else
    log "ERROR: $ERRORS database restorations failed"
    exit 1
fi
