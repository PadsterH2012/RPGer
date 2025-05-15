# RPGer Disaster Recovery Runbook

This runbook provides step-by-step instructions for recovering the RPGer system in various disaster scenarios.

## Table of Contents

1. [Emergency Contacts](#emergency-contacts)
2. [System Overview](#system-overview)
3. [Recovery Scenarios](#recovery-scenarios)
   - [Database Corruption](#database-corruption)
   - [Container Failure](#container-failure)
   - [Disk Failure](#disk-failure)
   - [Complete System Failure](#complete-system-failure)
4. [Verification Procedures](#verification-procedures)

## Emergency Contacts

| Role | Name | Contact |
|------|------|---------|
| System Administrator | [Name] | [Contact Information] |
| Database Administrator | [Name] | [Contact Information] |
| Application Owner | [Name] | [Contact Information] |

## System Overview

The RPGer system consists of:

- **Frontend**: React application
- **Backend**: Flask-SocketIO application
- **Database Stack**:
  - MongoDB (primary data store)
  - Redis (caching and real-time features)
  - Chroma (vector database for AI)

All database data is stored on a dedicated disk mounted at `/data2/rpger/`.

## Recovery Scenarios

### Database Corruption

#### Symptoms
- Application errors related to database operations
- Error messages in container logs
- Failed health checks

#### Recovery Steps

1. **Verify the issue**:
   ```bash
   cd /mnt/network_repo/RPGer && sudo /mnt/network_repo/RPGer/db_stack/health-check-scripts/database-health-check.sh
   ```

2. **Stop the application**:
   ```bash
   cd /mnt/network_repo/RPGer && ./start-rpger.sh stop
   ```

3. **Restore from the latest backup**:
   ```bash
   sudo /mnt/network_repo/RPGer/db_stack/backup-scripts/restore-databases.sh
   ```

4. **Start the application**:
   ```bash
   cd /mnt/network_repo/RPGer && ./start-rpger.sh start
   ```

5. **Verify the recovery**:
   ```bash
   cd /mnt/network_repo/RPGer && sudo /mnt/network_repo/RPGer/db_stack/health-check-scripts/database-health-check.sh
   ```

### Container Failure

#### Symptoms
- Missing containers in `docker ps` output
- Container in "Exited" or "Restarting" state
- Application functionality issues

#### Recovery Steps

1. **Check container status**:
   ```bash
   docker ps -a | grep rpger
   ```

2. **View container logs**:
   ```bash
   docker logs rpger-mongodb  # Replace with the affected container name
   ```

3. **Restart the container**:
   ```bash
   docker restart rpger-mongodb  # Replace with the affected container name
   ```

4. **If restart fails, recreate the container**:
   ```bash
   cd /mnt/network_repo/RPGer && ./start-rpger.sh db-only  # For database containers
   # OR
   cd /mnt/network_repo/RPGer && ./start-rpger.sh start  # For all containers
   ```

5. **Verify the recovery**:
   ```bash
   cd /mnt/network_repo/RPGer && sudo /mnt/network_repo/RPGer/db_stack/health-check-scripts/database-health-check.sh
   ```

### Disk Failure

#### Symptoms
- I/O errors in container logs
- Disk-related error messages in system logs
- Failed health checks

#### Recovery Steps

1. **Stop all containers**:
   ```bash
   cd /mnt/network_repo/RPGer && ./start-rpger.sh stop
   ```

2. **Replace the failed disk and mount it at `/data2`**

3. **Create the required directory structure**:
   ```bash
   sudo mkdir -p /data2/rpger/mongodb /data2/rpger/redis /data2/rpger/chroma /data2/rpger/backups /data2/rpger/logs
   ```

4. **Set appropriate permissions**:
   ```bash
   sudo chown -R 1001:1001 /data2/rpger/mongodb && sudo chown -R 999:999 /data2/rpger/redis && sudo chown -R 1000:1000 /data2/rpger/chroma && sudo chmod -R 755 /data2/rpger
   ```

5. **If you have an external backup, restore it to the new disk**

6. **Start the database stack**:
   ```bash
   cd /mnt/network_repo/RPGer && ./start-rpger.sh db-only
   ```

7. **Start the application**:
   ```bash
   cd /mnt/network_repo/RPGer && ./start-rpger.sh start
   ```

8. **Verify the recovery**:
   ```bash
   cd /mnt/network_repo/RPGer && sudo /mnt/network_repo/RPGer/db_stack/health-check-scripts/database-health-check.sh
   ```

### Complete System Failure

#### Symptoms
- System is completely unavailable
- All containers are down
- Host system may be unreachable

#### Recovery Steps

1. **Ensure the host system is operational**

2. **Ensure the required disk is mounted at `/data2`**:
   ```bash
   df -h | grep /data2
   ```

3. **If the disk is not mounted, mount it**:
   ```bash
   sudo mount /dev/sdX /data2  # Replace sdX with the actual device
   ```

4. **Ensure Docker is installed and running**:
   ```bash
   docker --version
   systemctl status docker
   ```

5. **Clone the RPGer repository (if not already present)**:
   ```bash
   git clone [repository-url] /mnt/network_repo/RPGer
   ```

6. **Start the database stack**:
   ```bash
   cd /mnt/network_repo/RPGer && ./start-rpger.sh db-only
   ```

7. **If you have a backup, restore it**:
   ```bash
   sudo /mnt/network_repo/RPGer/db_stack/backup-scripts/restore-databases.sh
   ```

8. **Start the application**:
   ```bash
   cd /mnt/network_repo/RPGer && ./start-rpger.sh start
   ```

9. **Verify the recovery**:
   ```bash
   cd /mnt/network_repo/RPGer && sudo /mnt/network_repo/RPGer/db_stack/health-check-scripts/database-health-check.sh
   ```

## Verification Procedures

### Database Health Check

Run the health check script to verify all database services are operational:

```bash
cd /mnt/network_repo/RPGer && sudo /mnt/network_repo/RPGer/db_stack/health-check-scripts/database-health-check.sh
```

### Application Verification

1. **Check if all containers are running**:
   ```bash
   docker ps | grep rpger
   ```

2. **Verify frontend access**:
   Open http://localhost:3001 in a web browser

3. **Verify backend API access**:
   ```bash
   curl http://localhost:5000/api/v1/heartbeat
   ```

4. **Verify MongoDB admin interface**:
   Open http://localhost:8081 in a web browser

5. **Verify Redis admin interface**:
   Open http://localhost:8082 in a web browser

### Data Integrity Verification

1. **Check MongoDB collections**:
   Access the MongoDB admin interface at http://localhost:8081 and verify that all expected collections are present

2. **Check Redis keys**:
   Access the Redis admin interface at http://localhost:8082 and verify that all expected keys are present

3. **Run application-specific tests**:
   Perform basic operations in the RPGer application to verify functionality
