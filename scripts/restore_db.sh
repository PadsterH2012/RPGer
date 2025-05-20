#!/bin/bash
# Database Restore Script for RPGer
# This script restores MongoDB and Redis databases from backups

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

# Load environment variables if .env file exists
ENV_FILE="${PROJECT_ROOT}/app_stack/backend/.env"
if [ -f "$ENV_FILE" ]; then
    echo "Loading environment variables from ${ENV_FILE}"
    source <(grep -v '^#' "$ENV_FILE" | sed -E 's/(.*)=(.*)/export \1="\2"/')
fi

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}   RPGer Database Restore Script        ${NC}"
echo -e "${BLUE}=========================================${NC}"
echo -e "Restore started at: $(date)"

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo -e "${RED}Backup directory does not exist: ${BACKUP_DIR}${NC}"
    exit 1
fi

# List available backups
echo -e "\n${BLUE}Available MongoDB backups:${NC}"
MONGODB_BACKUPS=($(ls -1 "$BACKUP_DIR" | grep -E "mongodb_.*\.tar\.gz" | sort -r))
if [ ${#MONGODB_BACKUPS[@]} -eq 0 ]; then
    echo -e "${YELLOW}No MongoDB backups found.${NC}"
else
    for i in "${!MONGODB_BACKUPS[@]}"; do
        echo -e "$((i+1)). ${MONGODB_BACKUPS[$i]}"
    done
fi

echo -e "\n${BLUE}Available Redis backups:${NC}"
REDIS_BACKUPS=($(ls -1 "$BACKUP_DIR" | grep -E "redis_.*\.rdb\.gz" | sort -r))
if [ ${#REDIS_BACKUPS[@]} -eq 0 ]; then
    echo -e "${YELLOW}No Redis backups found.${NC}"
else
    for i in "${!REDIS_BACKUPS[@]}"; do
        echo -e "$((i+1)). ${REDIS_BACKUPS[$i]}"
    done
fi

# Function to restore MongoDB
restore_mongodb() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        echo -e "${YELLOW}No MongoDB backup selected.${NC}"
        return 0
    fi
    
    echo -e "\n${BLUE}Restoring MongoDB from: ${backup_file}${NC}"
    
    # Get MongoDB connection parameters
    MONGODB_URI=${MONGODB_URI:-"mongodb://localhost:27017/rpger"}
    DB_NAME=$(echo "$MONGODB_URI" | sed -E 's/.*\/([^?]+)(\?.*)?$/\1/')
    
    # Create a temporary directory for extraction
    TEMP_DIR=$(mktemp -d)
    
    # Extract the backup
    echo "Extracting backup..."
    tar -xzf "${BACKUP_DIR}/${backup_file}" -C "$TEMP_DIR"
    
    # Find the extracted directory
    EXTRACTED_DIR=$(find "$TEMP_DIR" -type d -name "mongodb_*" | head -n 1)
    
    if [ -z "$EXTRACTED_DIR" ]; then
        echo -e "${RED}Failed to extract backup.${NC}"
        rm -rf "$TEMP_DIR"
        return 1
    fi
    
    # Check if we're using Docker
    if [ -f /.dockerenv ] || grep -q docker /proc/self/cgroup 2>/dev/null; then
        echo "Running in Docker environment, using mongorestore from container"
        docker exec -it mongodb mongorestore --uri="$MONGODB_URI" --drop "$EXTRACTED_DIR"
    else
        # Check if mongorestore is installed
        if command -v mongorestore > /dev/null; then
            echo "Using local mongorestore command"
            mongorestore --uri="$MONGODB_URI" --drop "$EXTRACTED_DIR"
        else
            echo -e "${RED}mongorestore command not found. Please install MongoDB tools.${NC}"
            rm -rf "$TEMP_DIR"
            return 1
        fi
    fi
    
    # Clean up
    rm -rf "$TEMP_DIR"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}MongoDB restore completed successfully.${NC}"
        return 0
    else
        echo -e "${RED}MongoDB restore failed.${NC}"
        return 1
    fi
}

# Function to restore Redis
restore_redis() {
    local backup_file=$1
    
    if [ -z "$backup_file" ]; then
        echo -e "${YELLOW}No Redis backup selected.${NC}"
        return 0
    fi
    
    echo -e "\n${BLUE}Restoring Redis from: ${backup_file}${NC}"
    
    # Get Redis connection parameters
    REDIS_URL=${REDIS_URL:-"redis://localhost:6379"}
    REDIS_HOST=$(echo "$REDIS_URL" | sed -E 's/redis:\/\/(.*):([0-9]+).*/\1/')
    REDIS_PORT=$(echo "$REDIS_URL" | sed -E 's/redis:\/\/(.*):([0-9]+).*/\2/')
    
    # Create a temporary directory for extraction
    TEMP_DIR=$(mktemp -d)
    TEMP_RDB="${TEMP_DIR}/dump.rdb"
    
    # Extract the backup
    echo "Extracting backup..."
    gunzip -c "${BACKUP_DIR}/${backup_file}" > "$TEMP_RDB"
    
    # Check if we're using Docker
    if [ -f /.dockerenv ] || grep -q docker /proc/self/cgroup 2>/dev/null; then
        echo "Running in Docker environment, copying RDB file to Redis container"
        # Stop Redis server
        docker exec -it redis redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" SHUTDOWN SAVE
        
        # Copy RDB file to Redis data directory
        docker cp "$TEMP_RDB" redis:/data/dump.rdb
        
        # Start Redis server
        docker start redis
    else
        echo -e "${YELLOW}Redis restore outside of Docker is not supported.${NC}"
        echo -e "${YELLOW}Please manually copy the RDB file to your Redis data directory and restart Redis.${NC}"
        echo -e "${YELLOW}Extracted RDB file: ${TEMP_RDB}${NC}"
        read -p "Press Enter to continue..."
    fi
    
    # Clean up
    rm -rf "$TEMP_DIR"
    
    echo -e "${GREEN}Redis restore completed.${NC}"
    return 0
}

# Prompt user to select backups
if [ ${#MONGODB_BACKUPS[@]} -gt 0 ]; then
    read -p "Select MongoDB backup to restore (1-${#MONGODB_BACKUPS[@]}, or 0 to skip): " mongodb_choice
    
    if [ "$mongodb_choice" -gt 0 ] 2>/dev/null && [ "$mongodb_choice" -le ${#MONGODB_BACKUPS[@]} ]; then
        SELECTED_MONGODB_BACKUP=${MONGODB_BACKUPS[$((mongodb_choice-1))]}
    else
        SELECTED_MONGODB_BACKUP=""
    fi
else
    SELECTED_MONGODB_BACKUP=""
fi

if [ ${#REDIS_BACKUPS[@]} -gt 0 ]; then
    read -p "Select Redis backup to restore (1-${#REDIS_BACKUPS[@]}, or 0 to skip): " redis_choice
    
    if [ "$redis_choice" -gt 0 ] 2>/dev/null && [ "$redis_choice" -le ${#REDIS_BACKUPS[@]} ]; then
        SELECTED_REDIS_BACKUP=${REDIS_BACKUPS[$((redis_choice-1))]}
    else
        SELECTED_REDIS_BACKUP=""
    fi
else
    SELECTED_REDIS_BACKUP=""
fi

# Confirm restore
echo -e "\n${YELLOW}You are about to restore the following backups:${NC}"
if [ -n "$SELECTED_MONGODB_BACKUP" ]; then
    echo -e "MongoDB: ${SELECTED_MONGODB_BACKUP}"
else
    echo -e "MongoDB: (skipped)"
fi

if [ -n "$SELECTED_REDIS_BACKUP" ]; then
    echo -e "Redis: ${SELECTED_REDIS_BACKUP}"
else
    echo -e "Redis: (skipped)"
fi

echo -e "${RED}WARNING: This will overwrite your current databases!${NC}"
read -p "Are you sure you want to continue? (y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo -e "${YELLOW}Restore cancelled.${NC}"
    exit 0
fi

# Run restore functions
if [ -n "$SELECTED_MONGODB_BACKUP" ]; then
    restore_mongodb "$SELECTED_MONGODB_BACKUP"
    MONGODB_RESULT=$?
else
    MONGODB_RESULT=0
fi

if [ -n "$SELECTED_REDIS_BACKUP" ]; then
    restore_redis "$SELECTED_REDIS_BACKUP"
    REDIS_RESULT=$?
else
    REDIS_RESULT=0
fi

# Summary
echo -e "\n${BLUE}=========================================${NC}"
echo -e "${BLUE}   Restore Summary                      ${NC}"
echo -e "${BLUE}=========================================${NC}"
echo -e "Restore completed at: $(date)"

if [ -n "$SELECTED_MONGODB_BACKUP" ]; then
    if [ $MONGODB_RESULT -eq 0 ]; then
        echo -e "MongoDB restore: ${GREEN}SUCCESS${NC}"
    else
        echo -e "MongoDB restore: ${RED}FAILED${NC}"
    fi
else
    echo -e "MongoDB restore: ${YELLOW}SKIPPED${NC}"
fi

if [ -n "$SELECTED_REDIS_BACKUP" ]; then
    if [ $REDIS_RESULT -eq 0 ]; then
        echo -e "Redis restore: ${GREEN}SUCCESS${NC}"
    else
        echo -e "Redis restore: ${RED}FAILED${NC}"
    fi
else
    echo -e "Redis restore: ${YELLOW}SKIPPED${NC}"
fi

# Exit with error if any restore failed
if [ $MONGODB_RESULT -ne 0 ] || [ $REDIS_RESULT -ne 0 ]; then
    exit 1
fi

exit 0
