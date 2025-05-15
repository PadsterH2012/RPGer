# Permanent Database Stack Architecture

## Feature Request

Create a permanent database stack architecture for the RPGer system that separates database services (MongoDB, Redis, Chroma) from the application components (frontend, backend). This architecture should support data persistence, automated backups, and container preseeding to facilitate rebuilds and system maintenance.

## Decision

A **containerized multi-database architecture** with persistent storage, automated backups, and preseeding capabilities is recommended to support the RPGer system's growing data needs.

## Recommended Approach

A **permanent database stack** that provides database services to the RPG application:

1. **Containerized Database Services**
   - MongoDB for structured data storage
   - Redis for caching and real-time data
   - Chroma for vector search capabilities
   - Each database in its own container with appropriate resource limits

2. **Persistent Storage Layer**
   - Named Docker volumes for each database
   - Mounted to appropriate container paths
   - Preserved across container restarts and rebuilds
   - Regular volume backups to external storage

3. **Backup System**
   - Scheduled automated backups for all databases
   - Rotation policy to manage backup storage
   - Verification of backup integrity
   - Documentation for manual backup and restore procedures

4. **Preseeding Mechanism**
   - Initialization scripts to detect empty databases
   - Automatic restoration from backups when needed
   - Version control for database schemas
   - Support for data migrations during upgrades

5. **Network Configuration**
   - Internal Docker network for database services
   - Limited external exposure for security
   - Connection pooling for efficient resource usage
   - Health monitoring and alerting

## Implementation Plan

1. **Phase 1: Infrastructure Design (1 week)**
   - Design Docker Compose configuration for database stack
   - Define volume structure for persistent storage
   - Plan network topology and security
   - Document resource requirements and scaling considerations
   - Create initialization and health check scripts

2. **Phase 2: Database Stack Implementation (2 weeks)**
   - Set up MongoDB container with persistent storage
   - Configure Redis container with appropriate persistence settings
   - Deploy Chroma container with vector storage volume
   - Implement internal networking between containers
   - Configure resource limits and restart policies

3. **Phase 3: Backup System Implementation (1 week)**
   - Create backup scripts for each database type
   - Set up scheduled backup jobs
   - Implement backup rotation and cleanup
   - Test backup integrity verification
   - Document manual backup procedures

4. **Phase 4: Preseeding Mechanism (1 week)**
   - Develop initialization scripts for each database
   - Create database dump and restore procedures
   - Implement version checking for schemas
   - Test automatic restoration from backups
   - Document manual intervention procedures

5. **Phase 5: Application Integration (1 week)**
   - Update application configuration to use database stack
   - Implement connection pooling and retry logic
   - Add health checks and monitoring
   - Test failover and recovery scenarios
   - Document operational procedures

## Docker Compose Configuration

```yaml
version: '3.8'

services:
  # MongoDB Service
  mongodb:
    image: mongo:latest
    container_name: rpger-mongodb
    restart: unless-stopped
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD=password
    volumes:
      - mongodb_data:/data/db
      - ./init-scripts/mongo:/docker-entrypoint-initdb.d
    ports:
      - "27017:27017"
    networks:
      - rpger-db-network
    healthcheck:
      test: ["CMD", "mongo", "--eval", "db.adminCommand('ping')"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis Service
  redis:
    image: redis:latest
    container_name: rpger-redis
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass password
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - rpger-db-network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Chroma Vector DB
  chroma:
    image: ghcr.io/chroma-core/chroma:latest
    container_name: rpger-chroma
    restart: unless-stopped
    volumes:
      - chroma_data:/chroma/chroma_data
    ports:
      - "8000:8000"
    environment:
      - CHROMA_DB_IMPL=duckdb+parquet
      - CHROMA_PERSIST_DIRECTORY=/chroma/chroma_data
    networks:
      - rpger-db-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/heartbeat"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Backup Service
  backup:
    image: alpine:latest
    container_name: rpger-backup
    volumes:
      - mongodb_data:/mongodb_data:ro
      - redis_data:/redis_data:ro
      - chroma_data:/chroma_data:ro
      - backups:/backups
      - ./backup-scripts:/scripts
    command: /scripts/backup-scheduler.sh
    depends_on:
      - mongodb
      - redis
      - chroma
    networks:
      - rpger-db-network

volumes:
  mongodb_data:
    name: rpger-mongodb-data
  redis_data:
    name: rpger-redis-data
  chroma_data:
    name: rpger-chroma-data
  backups:
    name: rpger-backups

networks:
  rpger-db-network:
    name: rpger-db-network
```

## Backup Scripts

Example MongoDB backup script:

```bash
#!/bin/bash
# mongodb-backup.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/mongodb"
RETENTION_DAYS=7

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Perform MongoDB dump
mongodump --host mongodb --username admin --password password --authenticationDatabase admin --out $BACKUP_DIR/$TIMESTAMP

# Compress the backup
tar -czf $BACKUP_DIR/$TIMESTAMP.tar.gz $BACKUP_DIR/$TIMESTAMP
rm -rf $BACKUP_DIR/$TIMESTAMP

# Remove backups older than retention period
find $BACKUP_DIR -name "*.tar.gz" -type f -mtime +$RETENTION_DAYS -delete

echo "MongoDB backup completed: $BACKUP_DIR/$TIMESTAMP.tar.gz"
```

## Preseeding Implementation

Example initialization script for MongoDB:

```bash
#!/bin/bash
# mongodb-init.sh

# Check if MongoDB is empty
COLLECTIONS=$(mongo --host mongodb --username admin --password password --authenticationDatabase admin --eval "db.getCollectionNames().length" rpger --quiet)

if [ "$COLLECTIONS" -eq "0" ]; then
  echo "MongoDB is empty, restoring from latest backup..."
  
  # Find the latest backup
  LATEST_BACKUP=$(find /backups/mongodb -name "*.tar.gz" -type f -printf "%T@ %p\n" | sort -n | tail -1 | cut -f2- -d" ")
  
  if [ -n "$LATEST_BACKUP" ]; then
    # Extract the backup
    TEMP_DIR=$(mktemp -d)
    tar -xzf $LATEST_BACKUP -C $TEMP_DIR
    
    # Restore the backup
    mongorestore --host mongodb --username admin --password password --authenticationDatabase admin $TEMP_DIR/*/
    
    # Clean up
    rm -rf $TEMP_DIR
    echo "MongoDB restored successfully from $LATEST_BACKUP"
  else
    echo "No backups found for MongoDB"
  fi
else
  echo "MongoDB already contains data, skipping initialization"
fi
```
