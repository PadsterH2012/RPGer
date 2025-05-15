# Volume Structure for Persistent Storage

This document outlines the volume structure for persistent storage in the RPGer database stack, ensuring data persistence across container restarts and system rebuilds.

## Overview

The RPGer database stack uses Docker named volumes to provide persistent storage for each database service. This approach offers several advantages:

1. **Data Persistence**: Data is preserved even when containers are removed or rebuilt
2. **Performance**: Native filesystem performance without the overhead of bind mounts
3. **Portability**: Volumes can be easily backed up, restored, and migrated
4. **Isolation**: Each service has its own dedicated volume

## Volume Design

### MongoDB Volume

```
Volume Name: rpger-mongodb-data
Container Mount Path: /data/db
Purpose: Stores MongoDB database files, indexes, and journals
Estimated Size: Starting at 1GB, scaling with data growth
Backup Frequency: Daily
```

MongoDB stores its data in the `/data/db` directory within the container. This includes:
- Database files (collections and indexes)
- Journal files for crash recovery
- Metadata and configuration

### Redis Volume

```
Volume Name: rpger-redis-data
Container Mount Path: /data
Purpose: Stores Redis persistence files (AOF and RDB snapshots)
Estimated Size: 500MB initially, scaling with cache usage
Backup Frequency: Daily
```

Redis is configured with appendonly persistence, which stores all write operations in an Append-Only File (AOF). This ensures data durability even in the event of unexpected shutdowns.

### Chroma Volume

```
Volume Name: rpger-chroma-data
Container Mount Path: /chroma/chroma_data
Purpose: Stores vector embeddings and metadata
Estimated Size: 2GB initially, scaling with embedding count
Backup Frequency: Daily
```

Chroma uses DuckDB+Parquet for persistent storage of vector embeddings and associated metadata.

### Backups Volume

```
Volume Name: rpger-backups
Container Mount Path: /backups
Purpose: Stores automated backups of all databases
Estimated Size: 5GB initially, scaling with backup retention policy
Backup Frequency: N/A (this is the backup destination)
```

The backups volume stores compressed backups of all database volumes, organized by date and service.

## Directory Structure

The backup volume will maintain the following directory structure:

```
/backups/
├── mongodb/
│   ├── daily/
│   │   ├── mongodb_20230601.tar.gz
│   │   ├── mongodb_20230602.tar.gz
│   │   └── ...
│   └── weekly/
│       ├── mongodb_202306_week1.tar.gz
│       └── ...
├── redis/
│   ├── daily/
│   │   ├── redis_20230601.tar.gz
│   │   └── ...
│   └── weekly/
│       └── ...
└── chroma/
    ├── daily/
    │   └── ...
    └── weekly/
        └── ...
```

## Volume Management

### Creation

Volumes are created automatically when the Docker Compose stack is first launched. They can also be pre-created with specific options:

```bash
# Create MongoDB volume with specific driver options
docker volume create --name rpger-mongodb-data --opt type=none --opt device=/path/to/mongodb/data --opt o=bind
```

### Backup

Volumes can be backed up using Docker's built-in commands or through the backup service:

```bash
# Manual backup of MongoDB volume
docker run --rm -v rpger-mongodb-data:/source -v $(pwd):/backup alpine tar czf /backup/mongodb-backup.tar.gz -C /source .
```

### Restoration

Volumes can be restored from backups:

```bash
# Restore MongoDB volume from backup
docker run --rm -v rpger-mongodb-data:/target -v $(pwd):/backup alpine sh -c "rm -rf /target/* && tar xzf /backup/mongodb-backup.tar.gz -C /target"
```

## Scaling Considerations

1. **Volume Drivers**: For production deployments, consider using volume drivers that support:
   - Replication
   - Encryption
   - Snapshots
   - Cloud storage integration

2. **Storage Provisioning**: Implement monitoring to track volume usage and provide alerts when volumes approach capacity limits.

3. **Performance Tuning**: For high-performance requirements, consider:
   - Using SSD-backed volumes
   - Adjusting filesystem parameters
   - Implementing volume quotas

## Next Steps

1. Implement automated volume backup scripts
2. Create volume monitoring and alerting
3. Develop volume maintenance procedures (cleanup, optimization)
4. Test volume backup and restore procedures
