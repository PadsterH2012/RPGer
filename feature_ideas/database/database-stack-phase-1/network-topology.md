# Network Topology and Security

This document outlines the network topology and security considerations for the RPGer database stack.

## Network Architecture

The RPGer database stack uses a dedicated Docker network to isolate database services and control communication between components.

### Network Diagram

```
                                  +-------------------+
                                  |                   |
                                  |  External Access  |
                                  |                   |
                                  +--------+----------+
                                           |
                                           | (Exposed Ports)
                                           |
+------------------------------------------+------------------------------------------+
|                                                                                     |
|                             rpger-db-network (Bridge)                               |
|                                                                                     |
+------------------------------------------+------------------------------------------+
                |                |                |                |                |
        +-------v------+  +------v-------+  +----v---------+ +----v---------+ +----v---------+
        |              |  |              |  |              | |              | |              |
        |   MongoDB    |  |    Redis     |  |    Chroma    | | MongoDB      | | Redis        |
        |              |  |              |  |              | | Express      | | Commander    |
        |  (27017)     |  |   (6379)     |  |   (8000)     | | (8081)       | | (8082)       |
        |              |  |              |  |              | |              | |              |
        +--------------+  +--------------+  +--------------+ +--------------+ +--------------+
                |                |                |
                v                v                v
        +---------------+---------------+---------------+
        |                                               |
        |               Backup Service                  |
        |                                               |
        +-----------------------------------------------+
```

### Network Configuration

```yaml
networks:
  rpger-db-network:
    name: rpger-db-network
    driver: bridge
    ipam:
      driver: default
      config:
        - subnet: 172.28.0.0/16
    driver_opts:
      com.docker.network.bridge.name: rpger-db-br
      com.docker.network.bridge.enable_icc: "true"
      com.docker.network.bridge.enable_ip_masquerade: "true"
```

## Port Exposure

The following ports are exposed to the host system:

| Service | Container Port | Host Port | Purpose |
|---------|---------------|-----------|---------|
| MongoDB | 27017 | 27017 | Database access |
| Redis | 6379 | 6379 | Cache access |
| Chroma | 8000 | 8000 | Vector database API |
| MongoDB Express | 8081 | 8081 | MongoDB admin interface |
| Redis Commander | 8081 | 8082 | Redis admin interface |

In production environments, consider:
- Restricting port exposure to localhost only
- Using a reverse proxy for admin interfaces
- Implementing IP-based access controls

## Security Measures

### Authentication

All database services require authentication:

1. **MongoDB**:
   - Root username and password
   - Database-specific users with limited permissions
   - Role-based access control (RBAC)

2. **Redis**:
   - Password authentication
   - ACL (Access Control Lists) for fine-grained control

3. **Chroma**:
   - API authentication (if supported)

4. **Admin Interfaces**:
   - Basic authentication for web interfaces
   - Restricted access to authorized IPs

### Encryption

1. **Data in Transit**:
   - TLS/SSL for MongoDB connections
   - Redis encrypted connections (if required)
   - HTTPS for admin interfaces

2. **Data at Rest**:
   - Volume encryption options for sensitive data
   - Encrypted backups

### Network Isolation

1. **Container Segmentation**:
   - Each service runs in its own container
   - Principle of least privilege for inter-service communication

2. **Firewall Rules**:
   - Internal firewall rules to restrict container-to-container traffic
   - Host-level firewall to restrict external access

## Integration with Application Stack

The database stack will be accessed by the application stack through:

1. **Direct Connection**:
   - Application containers connect to database services using internal Docker network DNS
   - Example: `mongodb://username:password@mongodb:27017/rpger`

2. **Network Bridge**:
   - If the application stack uses a separate Docker network, networks can be connected
   - Example: `docker network connect rpger-app-network rpger-mongodb`

## Security Best Practices

1. **Regular Updates**:
   - Keep database images updated with security patches
   - Implement a vulnerability scanning process

2. **Access Logging**:
   - Enable audit logging for all database services
   - Centralize logs for analysis

3. **Penetration Testing**:
   - Regularly test the security of the database stack
   - Address vulnerabilities promptly

4. **Secrets Management**:
   - Use Docker secrets or external secrets management
   - Avoid hardcoding credentials in configuration files

## Next Steps

1. Implement network access controls
2. Configure TLS/SSL for database connections
3. Set up centralized logging for security events
4. Create network monitoring and alerting
5. Develop network security testing procedures
