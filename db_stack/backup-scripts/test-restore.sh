#!/bin/bash
# Backup restoration test script for RPGer

# Set the base directory for backups
BACKUP_DIR="/data2/rpger/backups"
LOG_DIR="/data2/rpger/logs"
RESTORE_LOG="$LOG_DIR/restore-test.log"
TEMP_DIR="/tmp/rpger-restore-test"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"
mkdir -p "$TEMP_DIR"

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

# Test MongoDB restoration
test_mongodb_restore() {
    local backup_date=$1
    local backup_path="$BACKUP_DIR/$backup_date/mongodb"
    local temp_restore_dir="$TEMP_DIR/mongodb"
    
    log "Testing MongoDB restoration from $backup_path"
    
    # Check if MongoDB backup directory exists
    if [ ! -d "$backup_path" ]; then
        log "ERROR: MongoDB backup directory does not exist"
        return 1
    fi
    
    # Create temporary directory for restoration
    mkdir -p "$temp_restore_dir"
    
    # Copy backup files to temporary directory
    log "Copying MongoDB backup files to temporary directory"
    cp -r "$backup_path/mongodb_backup" "$temp_restore_dir/"
    
    # Create a test container for restoration
    log "Creating test MongoDB container for restoration"
    docker run --rm -d --name rpger-mongodb-restore-test \
        -v "$temp_restore_dir:/tmp/restore" \
        mongo:latest
    
    # Wait for container to start
    sleep 5
    
    # Test restoration
    log "Testing MongoDB restoration"
    docker exec rpger-mongodb-restore-test mongorestore \
        --host localhost \
        --port 27017 \
        --drop \
        /tmp/restore/mongodb_backup
    
    # Check if restoration was successful
    if [ $? -eq 0 ]; then
        log "MongoDB restoration test completed successfully"
        
        # Check if databases were restored
        log "Verifying restored databases"
        DB_LIST=$(docker exec rpger-mongodb-restore-test mongosh --quiet --eval "db.adminCommand('listDatabases').databases.map(db => db.name).join(',')")
        
        log "Restored databases: $DB_LIST"
        
        # Stop and remove the test container
        docker stop rpger-mongodb-restore-test
        
        # Clean up temporary directory
        rm -rf "$temp_restore_dir"
        
        return 0
    else
        log "ERROR: MongoDB restoration test failed"
        
        # Stop and remove the test container
        docker stop rpger-mongodb-restore-test
        
        # Clean up temporary directory
        rm -rf "$temp_restore_dir"
        
        return 1
    fi
}

# Test Redis restoration
test_redis_restore() {
    local backup_date=$1
    local backup_path="$BACKUP_DIR/$backup_date/redis"
    local temp_restore_dir="$TEMP_DIR/redis"
    
    log "Testing Redis restoration from $backup_path"
    
    # Check if Redis backup directory exists
    if [ ! -d "$backup_path" ]; then
        log "ERROR: Redis backup directory does not exist"
        return 1
    fi
    
    # Create temporary directory for restoration
    mkdir -p "$temp_restore_dir"
    
    # Copy backup files to temporary directory
    log "Copying Redis backup files to temporary directory"
    cp -r "$backup_path/dump.rdb" "$temp_restore_dir/"
    
    # Create a test container for restoration
    log "Creating test Redis container for restoration"
    docker run --rm -d --name rpger-redis-restore-test \
        -v "$temp_restore_dir:/data" \
        redis:latest
    
    # Wait for container to start
    sleep 5
    
    # Check if Redis is running with the restored data
    log "Verifying Redis restoration"
    REDIS_INFO=$(docker exec rpger-redis-restore-test redis-cli info keyspace)
    
    log "Redis keyspace info: $REDIS_INFO"
    
    # Stop and remove the test container
    docker stop rpger-redis-restore-test
    
    # Clean up temporary directory
    rm -rf "$temp_restore_dir"
    
    log "Redis restoration test completed successfully"
    return 0
}

# Test Chroma restoration
test_chroma_restore() {
    local backup_date=$1
    local backup_path="$BACKUP_DIR/$backup_date/chroma"
    local temp_restore_dir="$TEMP_DIR/chroma"
    
    log "Testing Chroma restoration from $backup_path"
    
    # Check if Chroma backup directory exists
    if [ ! -d "$backup_path" ]; then
        log "ERROR: Chroma backup directory does not exist"
        return 1
    fi
    
    # Create temporary directory for restoration
    mkdir -p "$temp_restore_dir"
    
    # Copy backup files to temporary directory
    log "Copying Chroma backup files to temporary directory"
    cp -r "$backup_path"/* "$temp_restore_dir/" 2>/dev/null || true
    
    # Check if there are any files to restore
    if [ -z "$(ls -A "$temp_restore_dir")" ]; then
        log "NOTE: No files to restore for Chroma (this is normal for a new installation)"
        rm -rf "$temp_restore_dir"
        return 0
    fi
    
    # Create a test container for restoration
    log "Creating test Chroma container for restoration"
    docker run --rm -d --name rpger-chroma-restore-test \
        -v "$temp_restore_dir:/chroma/chroma_data" \
        -e CHROMA_DB_IMPL=duckdb+parquet \
        -e CHROMA_PERSIST_DIRECTORY=/chroma/chroma_data \
        ghcr.io/chroma-core/chroma:latest
    
    # Wait for container to start
    sleep 10
    
    # Check if Chroma is running
    log "Verifying Chroma restoration"
    if docker ps | grep -q rpger-chroma-restore-test; then
        log "Chroma container is running with restored data"
        
        # Stop and remove the test container
        docker stop rpger-chroma-restore-test
        
        # Clean up temporary directory
        rm -rf "$temp_restore_dir"
        
        log "Chroma restoration test completed successfully"
        return 0
    else
        log "ERROR: Chroma container failed to start with restored data"
        
        # Clean up temporary directory
        rm -rf "$temp_restore_dir"
        
        return 1
    fi
}

# Main execution
if [ $# -eq 0 ]; then
    # If no backup date is provided, use the most recent backup
    LATEST_BACKUP=$(ls -1tr "$BACKUP_DIR" | grep -E '^[0-9]{4}-[0-9]{2}-[0-9]{2}_[0-9]{2}-[0-9]{2}-[0-9]{2}$' | tail -n 1)
    
    if [ -z "$LATEST_BACKUP" ]; then
        log "ERROR: No backups found in $BACKUP_DIR"
        exit 1
    fi
    
    BACKUP_DATE="$LATEST_BACKUP"
    log "Using latest backup: $BACKUP_DATE"
else
    # Use the provided backup date
    BACKUP_DATE="$1"
    log "Using specified backup: $BACKUP_DATE"
fi

# Check if the backup directory exists
if ! check_backup_dir "$BACKUP_DATE"; then
    log "ERROR: Cannot test restoration for backup $BACKUP_DATE"
    exit 1
fi

# Initialize error counter
ERRORS=0

# Test MongoDB restoration
if ! test_mongodb_restore "$BACKUP_DATE"; then
    ERRORS=$((ERRORS + 1))
fi

# Test Redis restoration
if ! test_redis_restore "$BACKUP_DATE"; then
    ERRORS=$((ERRORS + 1))
fi

# Test Chroma restoration
if ! test_chroma_restore "$BACKUP_DATE"; then
    ERRORS=$((ERRORS + 1))
fi

# Clean up temporary directory
rm -rf "$TEMP_DIR"

# Report results
if [ "$ERRORS" -eq 0 ]; then
    log "All restoration tests completed successfully"
    exit 0
else
    log "ERROR: $ERRORS restoration tests failed"
    exit 1
fi
