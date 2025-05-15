#!/bin/bash
# Backup verification script for RPGer

# Set the base directory for backups
BACKUP_DIR="/data2/rpger/backups"
LOG_DIR="/data2/rpger/logs"
VERIFY_LOG="$LOG_DIR/backup-verify.log"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Log function
log() {
    echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $1" | tee -a "$VERIFY_LOG"
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

# Verify MongoDB backup
verify_mongodb_backup() {
    local backup_date=$1
    local backup_path="$BACKUP_DIR/$backup_date/mongodb"
    
    log "Verifying MongoDB backup in $backup_path"
    
    # Check if MongoDB backup directory exists
    if [ ! -d "$backup_path" ]; then
        log "ERROR: MongoDB backup directory does not exist"
        return 1
    fi
    
    # Check if MongoDB backup files exist
    if [ ! -d "$backup_path/mongodb_backup" ]; then
        log "ERROR: MongoDB backup files do not exist"
        return 1
    fi
    
    # Count the number of database directories
    local db_count=$(find "$backup_path/mongodb_backup" -maxdepth 1 -type d | wc -l)
    db_count=$((db_count - 1))  # Subtract 1 for the parent directory
    
    if [ "$db_count" -lt 1 ]; then
        log "ERROR: No database directories found in MongoDB backup"
        return 1
    fi
    
    log "MongoDB backup contains $db_count database directories"
    
    # Check for specific databases
    if [ -d "$backup_path/mongodb_backup/admin" ]; then
        log "Found admin database in MongoDB backup"
    else
        log "WARNING: admin database not found in MongoDB backup"
    fi
    
    if [ -d "$backup_path/mongodb_backup/rpger" ]; then
        log "Found rpger database in MongoDB backup"
    else
        log "WARNING: rpger database not found in MongoDB backup"
    fi
    
    log "MongoDB backup verification completed successfully"
    return 0
}

# Verify Redis backup
verify_redis_backup() {
    local backup_date=$1
    local backup_path="$BACKUP_DIR/$backup_date/redis"
    
    log "Verifying Redis backup in $backup_path"
    
    # Check if Redis backup directory exists
    if [ ! -d "$backup_path" ]; then
        log "ERROR: Redis backup directory does not exist"
        return 1
    fi
    
    # Check if Redis dump.rdb file exists
    if [ ! -f "$backup_path/dump.rdb" ]; then
        log "ERROR: Redis dump.rdb file does not exist"
        return 1
    fi
    
    # Check file size of dump.rdb (should be > 0)
    local dump_size=$(stat -c%s "$backup_path/dump.rdb")
    if [ "$dump_size" -eq 0 ]; then
        log "ERROR: Redis dump.rdb file is empty"
        return 1
    fi
    
    log "Redis dump.rdb file size: $dump_size bytes"
    
    # Check for appendonly.aof file (optional)
    if [ -f "$backup_path/appendonly.aof" ]; then
        local aof_size=$(stat -c%s "$backup_path/appendonly.aof")
        log "Redis appendonly.aof file size: $aof_size bytes"
    else
        log "NOTE: Redis appendonly.aof file not found (this is normal if AOF is not enabled)"
    fi
    
    log "Redis backup verification completed successfully"
    return 0
}

# Verify Chroma backup
verify_chroma_backup() {
    local backup_date=$1
    local backup_path="$BACKUP_DIR/$backup_date/chroma"
    
    log "Verifying Chroma backup in $backup_path"
    
    # Check if Chroma backup directory exists
    if [ ! -d "$backup_path" ]; then
        log "ERROR: Chroma backup directory does not exist"
        return 1
    fi
    
    # Check if there are any files in the Chroma backup directory
    local file_count=$(find "$backup_path" -type f | wc -l)
    
    if [ "$file_count" -eq 0 ]; then
        log "NOTE: No files found in Chroma backup (this is normal for a new installation)"
    else
        log "Chroma backup contains $file_count files"
    fi
    
    log "Chroma backup verification completed successfully"
    return 0
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
    log "ERROR: Cannot verify backup $BACKUP_DATE"
    exit 1
fi

# Initialize error counter
ERRORS=0

# Verify MongoDB backup
if ! verify_mongodb_backup "$BACKUP_DATE"; then
    ERRORS=$((ERRORS + 1))
fi

# Verify Redis backup
if ! verify_redis_backup "$BACKUP_DATE"; then
    ERRORS=$((ERRORS + 1))
fi

# Verify Chroma backup
if ! verify_chroma_backup "$BACKUP_DATE"; then
    ERRORS=$((ERRORS + 1))
fi

# Report results
if [ "$ERRORS" -eq 0 ]; then
    log "All backup verifications completed successfully"
    exit 0
else
    log "ERROR: $ERRORS backup verifications failed"
    exit 1
fi
