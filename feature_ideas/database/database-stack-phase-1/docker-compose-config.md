# Docker Compose Configuration Design

This document outlines the Docker Compose configuration for the RPGer database stack, focusing on creating a robust, maintainable, and scalable database infrastructure.

## Overview

The Docker Compose configuration will define the following services:
- MongoDB (primary database)
- Redis (caching and real-time data)
- Chroma (vector database)
- Backup service
- Monitoring tools

## Configuration Structure

```yaml
version: '3.8'

services:
  # MongoDB Service
  mongodb:
    image: mongo:latest
    container_name: rpger-mongodb
    restart: unless-stopped
    environment:
      - MONGO_INITDB_ROOT_USERNAME=${MONGO_USERNAME:-admin}
      - MONGO_INITDB_ROOT_PASSWORD=${MONGO_PASSWORD:-password}
      - MONGO_INITDB_DATABASE=rpger
    volumes:
      - mongodb_data:/data/db
      - ./init-scripts/mongo:/docker-entrypoint-initdb.d
    ports:
      - "${MONGO_PORT:-27017}:27017"
    networks:
      - rpger-db-network
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 20s

  # Redis Service
  redis:
    image: redis:latest
    container_name: rpger-redis
    restart: unless-stopped
    command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-password}
    volumes:
      - redis_data:/data
    ports:
      - "${REDIS_PORT:-6379}:6379"
    networks:
      - rpger-db-network
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "${REDIS_PASSWORD:-password}", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s

  # Chroma Vector DB
  chroma:
    image: ghcr.io/chroma-core/chroma:latest
    container_name: rpger-chroma
    restart: unless-stopped
    volumes:
      - chroma_data:/chroma/chroma_data
    ports:
      - "${CHROMA_PORT:-8000}:8000"
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
      start_period: 15s

  # MongoDB Express (Admin Interface)
  mongo-express:
    image: mongo-express:latest
    container_name: rpger-mongo-express
    restart: unless-stopped
    ports:
      - "${MONGO_EXPRESS_PORT:-8081}:8081"
    environment:
      - ME_CONFIG_MONGODB_SERVER=mongodb
      - ME_CONFIG_MONGODB_PORT=27017
      - ME_CONFIG_MONGODB_ADMINUSERNAME=${MONGO_USERNAME:-admin}
      - ME_CONFIG_MONGODB_ADMINPASSWORD=${MONGO_PASSWORD:-password}
      - ME_CONFIG_BASICAUTH_USERNAME=${MONGO_EXPRESS_USERNAME:-admin}
      - ME_CONFIG_BASICAUTH_PASSWORD=${MONGO_EXPRESS_PASSWORD:-password}
    depends_on:
      mongodb:
        condition: service_healthy
    networks:
      - rpger-db-network

  # Redis Commander (Admin Interface)
  redis-commander:
    image: rediscommander/redis-commander:latest
    container_name: rpger-redis-commander
    restart: unless-stopped
    ports:
      - "${REDIS_COMMANDER_PORT:-8082}:8081"
    environment:
      - REDIS_HOSTS=local:redis:6379:0:${REDIS_PASSWORD:-password}
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - rpger-db-network

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
    driver: bridge
```

## Environment Variables

The configuration uses environment variables to allow for easy customization without modifying the Docker Compose file. A `.env` file will be used to store these variables:

```
# MongoDB Configuration
MONGO_USERNAME=admin
MONGO_PASSWORD=password
MONGO_PORT=27017

# Redis Configuration
REDIS_PASSWORD=password
REDIS_PORT=6379

# Chroma Configuration
CHROMA_PORT=8000

# Admin Interfaces
MONGO_EXPRESS_PORT=8081
MONGO_EXPRESS_USERNAME=admin
MONGO_EXPRESS_PASSWORD=password
REDIS_COMMANDER_PORT=8082
```

## Security Considerations

1. **Password Management**:
   - All default passwords in the example should be changed in production
   - Consider using Docker secrets for sensitive information in production

2. **Network Isolation**:
   - The `rpger-db-network` isolates database services
   - Only necessary ports are exposed

3. **Access Control**:
   - Admin interfaces are protected with basic authentication
   - Database services require authentication

## Next Steps

1. Implement initialization scripts for each database service
2. Create backup scripts for automated backups
3. Develop health check scripts for monitoring
4. Test the configuration in a development environment
