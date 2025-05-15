#!/bin/bash
# Redis initialization script
# This script will be executed when the Redis container starts

# Set variables
REDIS_HOST="redis"
REDIS_PORT="6379"
REDIS_PASSWORD="${REDIS_PASSWORD:-password}"

# Function to execute Redis commands
execute_redis_command() {
    redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD "$@"
}

echo "Starting Redis initialization..."

# Check if Redis is ready
max_attempts=30
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if execute_redis_command PING | grep -q "PONG"; then
        echo "Redis is ready"
        break
    fi
    attempt=$((attempt+1))
    echo "Waiting for Redis to be ready... ($attempt/$max_attempts)"
    sleep 1
done

if [ $attempt -eq $max_attempts ]; then
    echo "Redis did not become ready in time. Exiting."
    exit 1
fi

# Check if Redis already has data
key_count=$(execute_redis_command DBSIZE)
echo "Current Redis database size: $key_count keys"

if [ "$key_count" -eq "0" ]; then
    echo "Redis database is empty, initializing..."
    
    # Create session configuration
    execute_redis_command CONFIG SET maxmemory-policy volatile-lru
    execute_redis_command CONFIG SET notify-keyspace-events Ex
    
    # Create some initial data structures
    
    # Session expiration settings
    execute_redis_command HSET config:session expiration_seconds 3600
    
    # Create rate limiting configuration
    execute_redis_command HSET config:rate_limits api_requests_per_minute 60
    execute_redis_command HSET config:rate_limits api_burst 10
    
    # Create cache configuration
    execute_redis_command HSET config:cache default_ttl_seconds 300
    execute_redis_command HSET config:cache max_items 10000
    
    # Create some example data for testing
    execute_redis_command HSET example:user:1 username "admin" email "admin@example.com" role "admin"
    execute_redis_command HSET example:user:2 username "user" email "user@example.com" role "user"
    
    # Set expiration for example data (24 hours)
    execute_redis_command EXPIRE example:user:1 86400
    execute_redis_command EXPIRE example:user:2 86400
    
    # Create pub/sub channels
    execute_redis_command PUBLISH system:init "Redis initialization completed"
    
    echo "Redis initialization completed successfully"
else
    echo "Redis database already contains data, skipping initialization"
fi

# Create Redis ACL users if ACL is supported
redis_version=$(execute_redis_command INFO | grep redis_version | cut -d ":" -f2 | tr -d "\r")
major_version=$(echo $redis_version | cut -d "." -f1)

if [ "$major_version" -ge "6" ]; then
    echo "Redis version $redis_version supports ACL, setting up users..."
    
    # Check if rpgerapp user already exists
    user_exists=$(execute_redis_command ACL LIST | grep -c "rpgerapp")
    
    if [ "$user_exists" -eq "0" ]; then
        echo "Creating application user..."
        
        # Create application user with limited permissions
        execute_redis_command ACL SETUSER rpgerapp on >rpgerapppassword ~rpger:* +@read +@write +@hash +@list +@set +@string +@sorted_set -@admin
        
        echo "Application user created successfully"
    else
        echo "Application user already exists"
    fi
else
    echo "Redis version $redis_version does not support ACL, skipping user creation"
fi

echo "Redis initialization script completed"
