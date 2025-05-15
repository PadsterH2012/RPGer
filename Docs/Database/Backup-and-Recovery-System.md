# RPGer Database Backup and Recovery System

This document describes the backup and recovery system for the RPGer database stack, including MongoDB, Redis, and Chroma.

## Table of Contents

1. [Overview](#overview)
2. [Backup System](#backup-system)
3. [Backup Verification](#backup-verification)
4. [Restoration Testing](#restoration-testing)
5. [Recovery Procedures](#recovery-procedures)
6. [Disaster Recovery](#disaster-recovery)
7. [Maintenance Tasks](#maintenance-tasks)

## Overview

The RPGer database stack consists of three main components:

1. **MongoDB**: Stores structured data including game state, character information, and campaign data
2. **Redis**: In-memory cache and message broker for real-time features
3. **Chroma**: Vector database for AI embeddings and semantic search

All data is stored on a dedicated disk mounted at `/data2` with the following directory structure:

```
/data2/rpger/
├── mongodb/       # MongoDB data files
├── redis/         # Redis data files
├── chroma/        # Chroma data files
├── backups/       # Database backups
└── logs/          # Log files
```

## Backup System

### Backup Schedule

Backups are performed daily at 2 AM using the `backup-databases.sh` script. The script creates a full backup of all databases and stores them in the `/data2/rpger/backups` directory.

### Backup Retention

The backup system retains the last 7 daily backups. Older backups are automatically deleted by the backup rotation process.

### Backup Contents

Each backup includes:

1. **MongoDB**: Full dump of all databases using `mongodump`
2. **Redis**: Snapshot of the Redis database (`dump.rdb`) and append-only file (`appendonly.aof`) if enabled
3. **Chroma**: Copy of all Chroma data files

### Backup Directory Structure

Backups are organized by date and time in the following structure:

```
/data2/rpger/backups/
├── YYYY-MM-DD_HH-MM-SS/
│   ├── mongodb/
│   │   └── mongodb_backup/
│   │       ├── admin/
│   │       ├── rpger/
│   │       └── ...
│   ├── redis/
│   │   ├── dump.rdb
│   │   └── appendonly.aof
│   └── chroma/
│       └── ...
├── YYYY-MM-DD_HH-MM-SS/
│   └── ...
└── ...
```

### Manual Backup

To manually trigger a backup, run:

```bash
sudo /mnt/network_repo/RPGer/db_stack/backup-scripts/backup-databases.sh
```

## Backup Verification

### Automated Verification

The `verify-backups.sh` script checks the integrity of backups by verifying:

1. **MongoDB**: Presence of database directories and files
2. **Redis**: Existence and size of dump.rdb and appendonly.aof files
3. **Chroma**: Presence of data files

### Running Verification

To verify the latest backup:

```bash
sudo /mnt/network_repo/RPGer/db_stack/backup-scripts/verify-backups.sh
```

To verify a specific backup:

```bash
sudo /mnt/network_repo/RPGer/db_stack/backup-scripts/verify-backups.sh YYYY-MM-DD_HH-MM-SS
```

### Verification Logs

Verification logs are stored in `/data2/rpger/logs/backup-verify.log`.

## Restoration Testing

### Test Restoration Process

The `test-restore.sh` script tests the restoration process by:

1. Creating temporary containers for each database
2. Restoring backup data to these containers
3. Verifying that the data can be accessed

This allows testing backup integrity without affecting the production environment.

### Running Restoration Tests

To test restoration of the latest backup:

```bash
sudo /mnt/network_repo/RPGer/db_stack/backup-scripts/test-restore.sh
```

To test restoration of a specific backup:

```bash
sudo /mnt/network_repo/RPGer/db_stack/backup-scripts/test-restore.sh YYYY-MM-DD_HH-MM-SS
```

### Test Logs

Restoration test logs are stored in `/data2/rpger/logs/restore-test.log`.

## Recovery Procedures

### Full System Recovery

To restore all databases from the latest backup:

```bash
sudo /mnt/network_repo/RPGer/db_stack/backup-scripts/restore-databases.sh
```

To restore all databases from a specific backup:

```bash
sudo /mnt/network_repo/RPGer/db_stack/backup-scripts/restore-databases.sh YYYY-MM-DD_HH-MM-SS
```

### Single Database Recovery

To restore only MongoDB:

```bash
sudo /mnt/network_repo/RPGer/db_stack/backup-scripts/restore-databases.sh --mongodb-only
```

To restore only Redis:

```bash
sudo /mnt/network_repo/RPGer/db_stack/backup-scripts/restore-databases.sh --redis-only
```

To restore only Chroma:

```bash
sudo /mnt/network_repo/RPGer/db_stack/backup-scripts/restore-databases.sh --chroma-only
```

### Recovery Logs

Recovery logs are stored in `/data2/rpger/logs/restore.log`.

## Disaster Recovery

### Complete System Failure

In case of complete system failure:

1. Ensure the system is operational with the required disk mounted at `/data2`
2. Install Docker and Docker Compose
3. Clone the RPGer repository
4. Start the database stack:
   ```bash
   cd /mnt/network_repo/RPGer && ./start-rpger.sh db-only
   ```
5. Restore from backup:
   ```bash
   sudo /mnt/network_repo/RPGer/db_stack/backup-scripts/restore-databases.sh
   ```
6. Start the application stack:
   ```bash
   cd /mnt/network_repo/RPGer && ./start-rpger.sh start
   ```

### Disk Failure

In case of disk failure:

1. Replace the failed disk and mount it at `/data2`
2. Create the required directory structure:
   ```bash
   sudo mkdir -p /data2/rpger/mongodb /data2/rpger/redis /data2/rpger/chroma /data2/rpger/backups /data2/rpger/logs
   ```
3. Set appropriate permissions:
   ```bash
   sudo chown -R 1001:1001 /data2/rpger/mongodb && sudo chown -R 999:999 /data2/rpger/redis && sudo chown -R 1000:1000 /data2/rpger/chroma && sudo chmod -R 755 /data2/rpger
   ```
4. Restore from an external backup if available, or rebuild the system from scratch

## Maintenance Tasks

### Regular Verification

It is recommended to regularly verify backups by running:

```bash
sudo /mnt/network_repo/RPGer/db_stack/backup-scripts/verify-backups.sh
```

### Test Restoration

Periodically test the restoration process to ensure backups can be successfully restored:

```bash
sudo /mnt/network_repo/RPGer/db_stack/backup-scripts/test-restore.sh
```

### Monitoring Disk Space

Monitor disk space usage to ensure sufficient space for backups:

```bash
df -h /data2
```

### External Backups

For additional safety, consider copying backups to an external location periodically.
