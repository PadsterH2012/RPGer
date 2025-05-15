# Resource Requirements and Scaling Considerations

This document outlines the resource requirements and scaling considerations for the RPGer database stack.

## Resource Allocation

### MongoDB

| Resource | Development | Production (Initial) | Production (Scaled) |
|----------|-------------|----------------------|---------------------|
| CPU | 1 core | 2 cores | 4+ cores |
| Memory | 1GB | 4GB | 8-16GB |
| Storage | 10GB | 50GB | 100GB+ |
| Network | 100Mbps | 1Gbps | 10Gbps |

**Configuration Parameters**:
```yaml
mongodb:
  # Resource limits
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 4G
      reservations:
        cpus: '0.5'
        memory: 1G
  # MongoDB configuration
  command: >
    --wiredTigerCacheSizeGB 2
    --oplogSize 1024
```

### Redis

| Resource | Development | Production (Initial) | Production (Scaled) |
|----------|-------------|----------------------|---------------------|
| CPU | 0.5 core | 1 core | 2+ cores |
| Memory | 512MB | 2GB | 4-8GB |
| Storage | 1GB | 5GB | 20GB+ |
| Network | 100Mbps | 1Gbps | 10Gbps |

**Configuration Parameters**:
```yaml
redis:
  # Resource limits
  deploy:
    resources:
      limits:
        cpus: '1'
        memory: 2G
      reservations:
        cpus: '0.2'
        memory: 512M
  # Redis configuration
  command: >
    redis-server
    --appendonly yes
    --maxmemory 1536mb
    --maxmemory-policy allkeys-lru
    --save 900 1
    --save 300 10
    --save 60 10000
```

### Chroma

| Resource | Development | Production (Initial) | Production (Scaled) |
|----------|-------------|----------------------|---------------------|
| CPU | 1 core | 2 cores | 4+ cores |
| Memory | 1GB | 4GB | 8-16GB |
| Storage | 5GB | 20GB | 50GB+ |
| Network | 100Mbps | 1Gbps | 10Gbps |

**Configuration Parameters**:
```yaml
chroma:
  # Resource limits
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 4G
      reservations:
        cpus: '0.5'
        memory: 1G
```

### Admin Interfaces

| Resource | Development | Production |
|----------|-------------|------------|
| CPU | 0.2 core | 0.5 core |
| Memory | 256MB | 512MB |
| Storage | Minimal | Minimal |
| Network | 100Mbps | 1Gbps |

**Configuration Parameters**:
```yaml
mongo-express:
  deploy:
    resources:
      limits:
        cpus: '0.5'
        memory: 512M
      reservations:
        cpus: '0.1'
        memory: 128M
```

## Performance Tuning

### MongoDB Performance Optimization

1. **Indexing Strategy**:
   - Create indexes for frequently queried fields
   - Use compound indexes for multi-field queries
   - Avoid over-indexing (increases write overhead)

2. **Query Optimization**:
   - Use projection to limit returned fields
   - Implement pagination for large result sets
   - Use aggregation pipeline for complex queries

3. **Storage Engine Configuration**:
   - Adjust WiredTiger cache size based on available memory
   - Configure journal compression
   - Tune oplog size for write-heavy workloads

### Redis Performance Optimization

1. **Memory Management**:
   - Set appropriate maxmemory limit
   - Choose eviction policy based on use case
   - Monitor memory fragmentation

2. **Persistence Configuration**:
   - Balance between AOF and RDB persistence
   - Adjust fsync frequency for durability vs. performance
   - Consider disabling persistence for pure caching use cases

3. **Connection Pooling**:
   - Implement connection pooling in clients
   - Monitor connection count
   - Set appropriate timeouts

### Chroma Performance Optimization

1. **Vector Optimization**:
   - Tune vector dimensions and distance metrics
   - Implement batch processing for bulk operations
   - Optimize index parameters

2. **Query Optimization**:
   - Adjust search parameters for precision vs. speed
   - Implement caching for frequent queries
   - Use appropriate filters to narrow search space

## Scaling Strategies

### Vertical Scaling

Increase resources allocated to existing containers:

```yaml
mongodb:
  deploy:
    resources:
      limits:
        cpus: '4'  # Increased from 2
        memory: 8G  # Increased from 4G
```

### Horizontal Scaling

#### MongoDB Replica Set

```yaml
mongodb-primary:
  # Primary configuration
  command: --replSet rpger-rs

mongodb-secondary-1:
  # Secondary configuration
  command: --replSet rpger-rs

mongodb-secondary-2:
  # Secondary configuration
  command: --replSet rpger-rs
```

#### Redis Cluster

```yaml
redis-master:
  # Master configuration

redis-replica-1:
  # Replica configuration
  command: redis-server --replicaof redis-master 6379

redis-replica-2:
  # Replica configuration
  command: redis-server --replicaof redis-master 6379
```

### Load Balancing

For read-heavy workloads, implement load balancing:

```yaml
mongodb-router:
  image: mongo:latest
  command: mongos --configdb rpger-config-rs/config-1:27019,config-2:27019
```

## Monitoring and Alerting

### Key Metrics to Monitor

1. **System Resources**:
   - CPU usage
   - Memory usage
   - Disk I/O
   - Network I/O

2. **Database-Specific Metrics**:
   - MongoDB: Connections, operations/sec, replication lag
   - Redis: Memory usage, evictions, hit rate
   - Chroma: Query latency, index size

### Monitoring Tools

1. **Prometheus + Grafana**:
   ```yaml
   prometheus:
     image: prom/prometheus
     volumes:
       - ./prometheus.yml:/etc/prometheus/prometheus.yml
   
   grafana:
     image: grafana/grafana
     depends_on:
       - prometheus
   ```

2. **MongoDB Exporter**:
   ```yaml
   mongodb-exporter:
     image: percona/mongodb_exporter
     command: --mongodb.uri=mongodb://username:password@mongodb:27017
   ```

3. **Redis Exporter**:
   ```yaml
   redis-exporter:
     image: oliver006/redis_exporter
     environment:
       - REDIS_ADDR=redis://redis:6379
       - REDIS_PASSWORD=password
   ```

## Next Steps

1. Implement resource limits in Docker Compose configuration
2. Set up monitoring and alerting for resource usage
3. Create performance benchmarks for each database service
4. Develop scaling procedures for different growth scenarios
5. Test failover and recovery procedures
