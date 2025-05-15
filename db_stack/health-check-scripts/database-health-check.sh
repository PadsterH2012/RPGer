#!/bin/bash
# Database health check script for RPGer

# Log file
LOG_DIR="/data2/rpger/logs"
LOG_FILE="$LOG_DIR/health-check.log"

# Create log directory if it doesn't exist
mkdir -p "$LOG_DIR"

# Log function
log() {
    echo "[$(date +%Y-%m-%d\ %H:%M:%S)] $1" | tee -a "$LOG_FILE"
}

# Check if a container is running
check_container_running() {
    local container_name=$1
    if docker ps --format '{{.Names}}' | grep -q "^$container_name$"; then
        return 0
    else
        return 1
    fi
}

# Check MongoDB health
check_mongodb() {
    log "Checking MongoDB health..."

    if ! check_container_running "rpger-mongodb"; then
        log "ERROR: MongoDB container is not running"
        return 1
    fi

    # Get MongoDB credentials from environment or use defaults
    MONGO_USER="admin"
    MONGO_PASS="password"

    # Check MongoDB connection
    if docker exec rpger-mongodb mongosh \
        --quiet \
        --host localhost \
        --port 27017 \
        --username "$MONGO_USER" \
        --password "$MONGO_PASS" \
        --authenticationDatabase admin \
        --eval "db.adminCommand('ping').ok" | grep -q "1"; then

        log "MongoDB is healthy"

        # Get database stats
        DB_STATS=$(docker exec rpger-mongodb mongosh \
            --quiet \
            --host localhost \
            --port 27017 \
            --username "$MONGO_USER" \
            --password "$MONGO_PASS" \
            --authenticationDatabase admin \
            --eval "db.stats()")

        log "MongoDB stats: $DB_STATS"
        return 0
    else
        log "ERROR: MongoDB is not responding"
        return 1
    fi
}

# Check Redis health
check_redis() {
    log "Checking Redis health..."

    if ! check_container_running "rpger-redis"; then
        log "ERROR: Redis container is not running"
        return 1
    fi

    # Check Redis connection
    if docker exec rpger-redis redis-cli -a "password" ping | grep -q "PONG"; then
        log "Redis is healthy"

        # Get Redis info
        REDIS_INFO=$(docker exec rpger-redis redis-cli -a "password" info | grep -E "used_memory|connected_clients|total_connections_received")

        log "Redis stats: $REDIS_INFO"
        return 0
    else
        log "ERROR: Redis is not responding"
        return 1
    fi
}

# Check Chroma health
check_chroma() {
    log "Checking Chroma health..."

    if ! check_container_running "rpger-chroma"; then
        log "ERROR: Chroma container is not running"
        return 1
    fi

    # Check Chroma API using external curl
    # Note: The Chroma container doesn't have curl or Python installed
    # so we use the host's curl to check the API
    if curl -s -f http://localhost:8000/api/v2/heartbeat > /dev/null; then
        log "Chroma is healthy"
        return 0
    else
        log "ERROR: Chroma is not responding"
        return 1
    fi
}

# Check disk space
check_disk_space() {
    log "Checking disk space..."

    # Check disk space on /data2
    DISK_USAGE=$(df -h /data2 | tail -n 1)
    DISK_USED_PERCENT=$(echo "$DISK_USAGE" | awk '{print $5}' | tr -d '%')

    log "Disk usage for /data2: $DISK_USAGE"

    if [ "$DISK_USED_PERCENT" -gt 90 ]; then
        log "WARNING: Disk space is critically low (${DISK_USED_PERCENT}%)"
        return 1
    elif [ "$DISK_USED_PERCENT" -gt 80 ]; then
        log "WARNING: Disk space is running low (${DISK_USED_PERCENT}%)"
        return 0
    else
        log "Disk space is sufficient (${DISK_USED_PERCENT}%)"
        return 0
    fi
}

# Main execution
log "Starting database health check"

# Run checks
MONGODB_STATUS=0
REDIS_STATUS=0
CHROMA_STATUS=0
DISK_STATUS=0

check_mongodb || MONGODB_STATUS=1
check_redis || REDIS_STATUS=1
check_chroma || CHROMA_STATUS=1
check_disk_space || DISK_STATUS=1

# Overall status
if [ $MONGODB_STATUS -eq 0 ] && [ $REDIS_STATUS -eq 0 ] && [ $CHROMA_STATUS -eq 0 ] && [ $DISK_STATUS -eq 0 ]; then
    log "All database services are healthy"
    exit 0
else
    log "One or more database services have issues"
    exit 1
fi
