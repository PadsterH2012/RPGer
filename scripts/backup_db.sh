#!/bin/bash
# Database Backup Script for RPGer
# This script creates backups of MongoDB and Redis databases

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
BACKUP_DIR="${PROJECT_ROOT}/backups"
DATE_FORMAT=$(date +"%Y-%m-%d_%H-%M-%S")
MONGODB_BACKUP_PATH="${BACKUP_DIR}/mongodb_${DATE_FORMAT}"
REDIS_BACKUP_PATH="${BACKUP_DIR}/redis_${DATE_FORMAT}.rdb"
RETENTION_DAYS=7  # Number of days to keep backups

# Load environment variables if .env file exists
ENV_FILE="${PROJECT_ROOT}/app_stack/backend/.env"
if [ -f "$ENV_FILE" ]; then
    echo "Loading environment variables from ${ENV_FILE}"
    source <(grep -v '^#' "$ENV_FILE" | sed -E 's/(.*)=(.*)/export \1="\2"/')
fi

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}   RPGer Database Backup Script         ${NC}"
echo -e "${BLUE}=========================================${NC}"
echo -e "Backup started at: $(date)"
echo -e "Backup directory: ${BACKUP_DIR}"

# Function to backup MongoDB
backup_mongodb() {
    echo -e "\n${BLUE}Backing up MongoDB...${NC}"
    
    # Get MongoDB connection parameters
    MONGODB_URI=${MONGODB_URI:-"mongodb://localhost:27017/rpger"}
    DB_NAME=$(echo "$MONGODB_URI" | sed -E 's/.*\/([^?]+)(\?.*)?$/\1/')
    
    # Check if we're using Docker
    if [ -f /.dockerenv ] || grep -q docker /proc/self/cgroup 2>/dev/null; then
        echo "Running in Docker environment, using mongodump from container"
        docker exec -it mongodb mongodump --uri="$MONGODB_URI" --out="$MONGODB_BACKUP_PATH" --gzip
    else
        # Check if mongodump is installed
        if command -v mongodump > /dev/null; then
            echo "Using local mongodump command"
            mongodump --uri="$MONGODB_URI" --out="$MONGODB_BACKUP_PATH" --gzip
        else
            echo -e "${RED}mongodump command not found. Please install MongoDB tools.${NC}"
            return 1
        fi
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}MongoDB backup completed successfully: ${MONGODB_BACKUP_PATH}${NC}"
        # Create a compressed archive
        tar -czf "${MONGODB_BACKUP_PATH}.tar.gz" -C "$(dirname "$MONGODB_BACKUP_PATH")" "$(basename "$MONGODB_BACKUP_PATH")"
        echo -e "${GREEN}MongoDB backup compressed: ${MONGODB_BACKUP_PATH}.tar.gz${NC}"
        # Remove the uncompressed directory
        rm -rf "$MONGODB_BACKUP_PATH"
        return 0
    else
        echo -e "${RED}MongoDB backup failed.${NC}"
        return 1
    fi
}

# Function to backup Redis
backup_redis() {
    echo -e "\n${BLUE}Backing up Redis...${NC}"
    
    # Get Redis connection parameters
    REDIS_URL=${REDIS_URL:-"redis://localhost:6379"}
    REDIS_HOST=$(echo "$REDIS_URL" | sed -E 's/redis:\/\/(.*):([0-9]+).*/\1/')
    REDIS_PORT=$(echo "$REDIS_URL" | sed -E 's/redis:\/\/(.*):([0-9]+).*/\2/')
    
    # Check if we're using Docker
    if [ -f /.dockerenv ] || grep -q docker /proc/self/cgroup 2>/dev/null; then
        echo "Running in Docker environment, using redis-cli from container"
        docker exec -it redis redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" --rdb "$REDIS_BACKUP_PATH"
    else
        # Check if redis-cli is installed
        if command -v redis-cli > /dev/null; then
            echo "Using local redis-cli command"
            redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" --rdb "$REDIS_BACKUP_PATH"
        else
            echo -e "${RED}redis-cli command not found. Please install Redis tools.${NC}"
            return 1
        fi
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Redis backup completed successfully: ${REDIS_BACKUP_PATH}${NC}"
        # Compress the backup
        gzip -f "$REDIS_BACKUP_PATH"
        echo -e "${GREEN}Redis backup compressed: ${REDIS_BACKUP_PATH}.gz${NC}"
        return 0
    else
        echo -e "${RED}Redis backup failed.${NC}"
        return 1
    fi
}

# Function to clean up old backups
cleanup_old_backups() {
    echo -e "\n${BLUE}Cleaning up old backups...${NC}"
    
    # Find and delete MongoDB backups older than RETENTION_DAYS
    find "$BACKUP_DIR" -name "mongodb_*" -type f -mtime +$RETENTION_DAYS -exec rm -f {} \;
    
    # Find and delete Redis backups older than RETENTION_DAYS
    find "$BACKUP_DIR" -name "redis_*" -type f -mtime +$RETENTION_DAYS -exec rm -f {} \;
    
    echo -e "${GREEN}Removed backups older than ${RETENTION_DAYS} days.${NC}"
}

# Run backup functions
backup_mongodb
MONGODB_RESULT=$?

backup_redis
REDIS_RESULT=$?

# Clean up old backups
cleanup_old_backups

# Summary
echo -e "\n${BLUE}=========================================${NC}"
echo -e "${BLUE}   Backup Summary                       ${NC}"
echo -e "${BLUE}=========================================${NC}"
echo -e "Backup completed at: $(date)"

if [ $MONGODB_RESULT -eq 0 ]; then
    echo -e "MongoDB backup: ${GREEN}SUCCESS${NC}"
else
    echo -e "MongoDB backup: ${RED}FAILED${NC}"
fi

if [ $REDIS_RESULT -eq 0 ]; then
    echo -e "Redis backup: ${GREEN}SUCCESS${NC}"
else
    echo -e "Redis backup: ${RED}FAILED${NC}"
fi

echo -e "\nBackup files:"
ls -lh "$BACKUP_DIR" | grep -E "mongodb_${DATE_FORMAT}|redis_${DATE_FORMAT}"

# Exit with error if any backup failed
if [ $MONGODB_RESULT -ne 0 ] || [ $REDIS_RESULT -ne 0 ]; then
    exit 1
fi

exit 0
