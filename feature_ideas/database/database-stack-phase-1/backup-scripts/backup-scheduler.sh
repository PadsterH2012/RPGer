#!/bin/bash
# Backup Scheduler Script
# This script schedules and manages backups for all database services in the RPGer stack

# Set variables
BACKUP_DIR="/backups"
MONGODB_BACKUP_DIR="$BACKUP_DIR/mongodb"
REDIS_BACKUP_DIR="$BACKUP_DIR/redis"
CHROMA_BACKUP_DIR="$BACKUP_DIR/chroma"

# Backup retention settings
DAILY_RETENTION_DAYS=7
WEEKLY_RETENTION_WEEKS=4
MONTHLY_RETENTION_MONTHS=6

# Create backup directories if they don't exist
mkdir -p "$MONGODB_BACKUP_DIR/daily" "$MONGODB_BACKUP_DIR/weekly" "$MONGODB_BACKUP_DIR/monthly"
mkdir -p "$REDIS_BACKUP_DIR/daily" "$REDIS_BACKUP_DIR/weekly" "$REDIS_BACKUP_DIR/monthly"
mkdir -p "$CHROMA_BACKUP_DIR/daily" "$CHROMA_BACKUP_DIR/weekly" "$CHROMA_BACKUP_DIR/monthly"

# Set permissions
chmod -R 755 "$BACKUP_DIR"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Function to backup MongoDB
backup_mongodb() {
    local backup_type=$1
    local backup_dir="$MONGODB_BACKUP_DIR/$backup_type"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$backup_dir/mongodb_$timestamp.tar.gz"
    
    log "Starting MongoDB $backup_type backup..."
    
    # Create temporary directory for MongoDB dump
    local temp_dir=$(mktemp -d)
    
    # Perform MongoDB dump
    mongodump --host mongodb --username admin --password password --authenticationDatabase admin --out "$temp_dir/mongodb_dump"
    
    # Check if dump was successful
    if [ $? -eq 0 ]; then
        # Compress the backup
        tar -czf "$backup_file" -C "$temp_dir" mongodb_dump
        
        # Check if compression was successful
        if [ $? -eq 0 ]; then
            log "MongoDB $backup_type backup completed successfully: $backup_file"
            
            # Calculate backup size
            local backup_size=$(du -h "$backup_file" | cut -f1)
            log "Backup size: $backup_size"
        else
            log "Error: Failed to compress MongoDB backup"
        fi
    else
        log "Error: MongoDB dump failed"
    fi
    
    # Clean up temporary directory
    rm -rf "$temp_dir"
    
    # Perform backup rotation based on type
    case "$backup_type" in
        daily)
            find "$backup_dir" -name "mongodb_*.tar.gz" -type f -mtime +$DAILY_RETENTION_DAYS -delete
            ;;
        weekly)
            find "$backup_dir" -name "mongodb_*.tar.gz" -type f -mtime +$((WEEKLY_RETENTION_WEEKS * 7)) -delete
            ;;
        monthly)
            find "$backup_dir" -name "mongodb_*.tar.gz" -type f -mtime +$((MONTHLY_RETENTION_MONTHS * 30)) -delete
            ;;
    esac
}

# Function to backup Redis
backup_redis() {
    local backup_type=$1
    local backup_dir="$REDIS_BACKUP_DIR/$backup_type"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$backup_dir/redis_$timestamp.rdb"
    
    log "Starting Redis $backup_type backup..."
    
    # Trigger Redis to save its database
    redis-cli -h redis -a password SAVE
    
    # Check if save was successful
    if [ $? -eq 0 ]; then
        # Copy the RDB file from the Redis container
        docker cp rpger-redis:/data/dump.rdb "$backup_file"
        
        # Check if copy was successful
        if [ $? -eq 0 ]; then
            # Compress the backup
            gzip "$backup_file"
            
            log "Redis $backup_type backup completed successfully: $backup_file.gz"
            
            # Calculate backup size
            local backup_size=$(du -h "$backup_file.gz" | cut -f1)
            log "Backup size: $backup_size"
        else
            log "Error: Failed to copy Redis RDB file"
        fi
    else
        log "Error: Redis SAVE command failed"
    fi
    
    # Perform backup rotation based on type
    case "$backup_type" in
        daily)
            find "$backup_dir" -name "redis_*.rdb.gz" -type f -mtime +$DAILY_RETENTION_DAYS -delete
            ;;
        weekly)
            find "$backup_dir" -name "redis_*.rdb.gz" -type f -mtime +$((WEEKLY_RETENTION_WEEKS * 7)) -delete
            ;;
        monthly)
            find "$backup_dir" -name "redis_*.rdb.gz" -type f -mtime +$((MONTHLY_RETENTION_MONTHS * 30)) -delete
            ;;
    esac
}

# Function to backup Chroma
backup_chroma() {
    local backup_type=$1
    local backup_dir="$CHROMA_BACKUP_DIR/$backup_type"
    local timestamp=$(date +%Y%m%d_%H%M%S)
    local backup_file="$backup_dir/chroma_$timestamp.tar.gz"
    
    log "Starting Chroma $backup_type backup..."
    
    # Create temporary directory for Chroma data
    local temp_dir=$(mktemp -d)
    
    # Copy Chroma data from the container
    docker cp rpger-chroma:/chroma/chroma_data "$temp_dir/"
    
    # Check if copy was successful
    if [ $? -eq 0 ]; then
        # Compress the backup
        tar -czf "$backup_file" -C "$temp_dir" chroma_data
        
        # Check if compression was successful
        if [ $? -eq 0 ]; then
            log "Chroma $backup_type backup completed successfully: $backup_file"
            
            # Calculate backup size
            local backup_size=$(du -h "$backup_file" | cut -f1)
            log "Backup size: $backup_size"
        else
            log "Error: Failed to compress Chroma backup"
        fi
    else
        log "Error: Failed to copy Chroma data"
    fi
    
    # Clean up temporary directory
    rm -rf "$temp_dir"
    
    # Perform backup rotation based on type
    case "$backup_type" in
        daily)
            find "$backup_dir" -name "chroma_*.tar.gz" -type f -mtime +$DAILY_RETENTION_DAYS -delete
            ;;
        weekly)
            find "$backup_dir" -name "chroma_*.tar.gz" -type f -mtime +$((WEEKLY_RETENTION_WEEKS * 7)) -delete
            ;;
        monthly)
            find "$backup_dir" -name "chroma_*.tar.gz" -type f -mtime +$((MONTHLY_RETENTION_MONTHS * 30)) -delete
            ;;
    esac
}

# Function to verify backups
verify_backups() {
    log "Verifying recent backups..."
    
    # Verify MongoDB backup
    local latest_mongodb_backup=$(find "$MONGODB_BACKUP_DIR/daily" -name "mongodb_*.tar.gz" -type f -printf "%T@ %p\n" | sort -n | tail -1 | cut -f2- -d" ")
    if [ -n "$latest_mongodb_backup" ]; then
        log "Verifying MongoDB backup: $latest_mongodb_backup"
        
        # Check if the file is a valid tar archive
        tar -tzf "$latest_mongodb_backup" > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            log "MongoDB backup verification successful"
        else
            log "Error: MongoDB backup verification failed"
        fi
    else
        log "Warning: No MongoDB backups found to verify"
    fi
    
    # Verify Redis backup
    local latest_redis_backup=$(find "$REDIS_BACKUP_DIR/daily" -name "redis_*.rdb.gz" -type f -printf "%T@ %p\n" | sort -n | tail -1 | cut -f2- -d" ")
    if [ -n "$latest_redis_backup" ]; then
        log "Verifying Redis backup: $latest_redis_backup"
        
        # Check if the file is a valid gzip archive
        gzip -t "$latest_redis_backup"
        if [ $? -eq 0 ]; then
            log "Redis backup verification successful"
        else
            log "Error: Redis backup verification failed"
        fi
    else
        log "Warning: No Redis backups found to verify"
    fi
    
    # Verify Chroma backup
    local latest_chroma_backup=$(find "$CHROMA_BACKUP_DIR/daily" -name "chroma_*.tar.gz" -type f -printf "%T@ %p\n" | sort -n | tail -1 | cut -f2- -d" ")
    if [ -n "$latest_chroma_backup" ]; then
        log "Verifying Chroma backup: $latest_chroma_backup"
        
        # Check if the file is a valid tar archive
        tar -tzf "$latest_chroma_backup" > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            log "Chroma backup verification successful"
        else
            log "Error: Chroma backup verification failed"
        fi
    else
        log "Warning: No Chroma backups found to verify"
    fi
}

# Function to calculate backup statistics
backup_stats() {
    log "Calculating backup statistics..."
    
    # Calculate total backup size
    local total_size=$(du -sh "$BACKUP_DIR" | cut -f1)
    log "Total backup size: $total_size"
    
    # Count backups by type
    local mongodb_count=$(find "$MONGODB_BACKUP_DIR" -name "mongodb_*.tar.gz" -type f | wc -l)
    local redis_count=$(find "$REDIS_BACKUP_DIR" -name "redis_*.rdb.gz" -type f | wc -l)
    local chroma_count=$(find "$CHROMA_BACKUP_DIR" -name "chroma_*.tar.gz" -type f | wc -l)
    
    log "MongoDB backups: $mongodb_count"
    log "Redis backups: $redis_count"
    log "Chroma backups: $chroma_count"
    log "Total backups: $((mongodb_count + redis_count + chroma_count))"
}

# Main backup function
run_backups() {
    local backup_type=$1
    log "Starting $backup_type backups..."
    
    backup_mongodb "$backup_type"
    backup_redis "$backup_type"
    backup_chroma "$backup_type"
    
    verify_backups
    backup_stats
    
    log "$backup_type backups completed"
}

# Main scheduler function
scheduler() {
    log "Starting backup scheduler..."
    
    # Run daily backups
    run_backups "daily"
    
    # Run weekly backups on Sunday
    if [ "$(date +%u)" -eq 7 ]; then
        run_backups "weekly"
    fi
    
    # Run monthly backups on the 1st of the month
    if [ "$(date +%d)" -eq 1 ]; then
        run_backups "monthly"
    fi
    
    log "Backup scheduler completed"
}

# Run the scheduler
scheduler
