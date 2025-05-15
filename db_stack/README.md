# RPGer Database Stack

This directory contains the containerized database infrastructure for the RPGer application.

## Overview

The database stack provides the following services:

1. **MongoDB**: Primary database for structured data and document storage
2. **Redis**: In-memory database for caching and real-time data access
3. **Chroma**: Vector database for embeddings and semantic search capabilities
4. **MongoDB Express**: Web-based MongoDB admin interface
5. **Redis Commander**: Web-based Redis admin interface

## Directory Structure

```
db_stack/
├── docker-compose.yml       # Docker Compose configuration
├── .env                     # Environment variables
├── init-scripts/            # Initialization scripts
│   └── mongo/               # MongoDB initialization scripts
│       └── init.js          # MongoDB initialization script
├── health-check-scripts/    # Health check scripts
└── backup-scripts/          # Backup scripts
```

## Configuration

The database stack is configured through the `.env` file, which contains environment variables for:

- MongoDB credentials and port
- Redis password and port
- Chroma port
- Admin interface credentials and ports

## Usage

### Starting the Database Stack

You can start the database stack using the master script from the root directory:

```bash
./start-rpger.sh db-only
```

Or directly using Docker Compose:

```bash
cd db_stack
docker-compose up -d
```

### Accessing Admin Interfaces

- **MongoDB Express**: http://localhost:8081
  - Username: admin (configurable in .env)
  - Password: password (configurable in .env)

- **Redis Commander**: http://localhost:8082

### Connecting from Application

Applications can connect to the databases using the following connection strings:

- **MongoDB**: `mongodb://admin:password@localhost:27017/rpger?authSource=admin`
- **Redis**: `redis://:password@localhost:6379`
- **Chroma**: `http://localhost:8000`

Replace `admin`, `password`, and ports with the values from your `.env` file.

## Data Persistence

All data is stored in Docker named volumes:

- `rpger-mongodb-data`: MongoDB data
- `rpger-redis-data`: Redis data
- `rpger-chroma-data`: Chroma data

These volumes persist across container restarts and rebuilds.

## Maintenance

### Backup

To manually backup the databases:

```bash
# MongoDB
docker exec rpger-mongodb mongodump --username admin --password password --authenticationDatabase admin --out /dump
docker cp rpger-mongodb:/dump ./backups/mongodb_$(date +%Y%m%d)

# Redis
docker exec rpger-redis redis-cli -a password SAVE
docker cp rpger-redis:/data/dump.rdb ./backups/redis_$(date +%Y%m%d).rdb
```

### Restore

To restore from backups:

```bash
# MongoDB
docker cp ./backups/mongodb_20230101 rpger-mongodb:/dump
docker exec rpger-mongodb mongorestore --username admin --password password --authenticationDatabase admin /dump

# Redis
docker cp ./backups/redis_20230101.rdb rpger-redis:/data/dump.rdb
docker restart rpger-redis
```

## Security Notes

- Default passwords in the `.env` file should be changed in production
- Consider using Docker secrets for sensitive information in production
- Restrict access to admin interfaces in production environments
