#!/bin/bash
# Database Health Check Script
# This script checks the health of all database services in the RPGer stack

# Set variables
MONGODB_HOST="mongodb"
MONGODB_PORT="27017"
MONGODB_USER="${MONGO_USERNAME:-admin}"
MONGODB_PASSWORD="${MONGO_PASSWORD:-password}"

REDIS_HOST="redis"
REDIS_PORT="6379"
REDIS_PASSWORD="${REDIS_PASSWORD:-password}"

CHROMA_HOST="chroma"
CHROMA_PORT="8000"

# Output formatting
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check MongoDB health
check_mongodb_health() {
    echo -e "\n${YELLOW}Checking MongoDB health...${NC}"
    
    # Check if MongoDB is running
    if nc -z $MONGODB_HOST $MONGODB_PORT; then
        echo -e "${GREEN}✓ MongoDB service is running${NC}"
        
        # Check if MongoDB is responsive
        if mongosh --quiet --host $MONGODB_HOST --port $MONGODB_PORT -u $MONGODB_USER -p $MONGODB_PASSWORD --authenticationDatabase admin --eval "db.adminCommand('ping')" | grep -q '"ok" : 1'; then
            echo -e "${GREEN}✓ MongoDB is responsive${NC}"
            
            # Get MongoDB version
            VERSION=$(mongosh --quiet --host $MONGODB_HOST --port $MONGODB_PORT -u $MONGODB_USER -p $MONGODB_PASSWORD --authenticationDatabase admin --eval "db.version()")
            echo -e "${GREEN}✓ MongoDB version: $VERSION${NC}"
            
            # Check database statistics
            DB_COUNT=$(mongosh --quiet --host $MONGODB_HOST --port $MONGODB_PORT -u $MONGODB_USER -p $MONGODB_PASSWORD --authenticationDatabase admin --eval "db.adminCommand('listDatabases').databases.length")
            echo -e "${GREEN}✓ Number of databases: $DB_COUNT${NC}"
            
            # Check if rpger database exists
            if mongosh --quiet --host $MONGODB_HOST --port $MONGODB_PORT -u $MONGODB_USER -p $MONGODB_PASSWORD --authenticationDatabase admin --eval "db.adminCommand('listDatabases').databases.map(function(d) { return d.name; }).indexOf('rpger')" | grep -q -v "-1"; then
                echo -e "${GREEN}✓ RPGer database exists${NC}"
                
                # Get collection count
                COLLECTION_COUNT=$(mongosh --quiet --host $MONGODB_HOST --port $MONGODB_PORT -u $MONGODB_USER -p $MONGODB_PASSWORD --authenticationDatabase admin --eval "db.getSiblingDB('rpger').getCollectionNames().length")
                echo -e "${GREEN}✓ Number of collections in rpger database: $COLLECTION_COUNT${NC}"
                
                # List collections
                COLLECTIONS=$(mongosh --quiet --host $MONGODB_HOST --port $MONGODB_PORT -u $MONGODB_USER -p $MONGODB_PASSWORD --authenticationDatabase admin --eval "db.getSiblingDB('rpger').getCollectionNames()")
                echo -e "${GREEN}✓ Collections: $COLLECTIONS${NC}"
            else
                echo -e "${RED}✗ RPGer database does not exist${NC}"
            fi
            
            # Check connection count
            CONNECTIONS=$(mongosh --quiet --host $MONGODB_HOST --port $MONGODB_PORT -u $MONGODB_USER -p $MONGODB_PASSWORD --authenticationDatabase admin --eval "db.serverStatus().connections.current")
            echo -e "${GREEN}✓ Current connections: $CONNECTIONS${NC}"
            
            return 0
        else
            echo -e "${RED}✗ MongoDB is not responsive${NC}"
            return 1
        fi
    else
        echo -e "${RED}✗ MongoDB service is not running${NC}"
        return 1
    fi
}

# Function to check Redis health
check_redis_health() {
    echo -e "\n${YELLOW}Checking Redis health...${NC}"
    
    # Check if Redis is running
    if nc -z $REDIS_HOST $REDIS_PORT; then
        echo -e "${GREEN}✓ Redis service is running${NC}"
        
        # Check if Redis is responsive
        if redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD PING | grep -q "PONG"; then
            echo -e "${GREEN}✓ Redis is responsive${NC}"
            
            # Get Redis version
            VERSION=$(redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD INFO | grep redis_version | cut -d ":" -f2 | tr -d "\r")
            echo -e "${GREEN}✓ Redis version: $VERSION${NC}"
            
            # Check memory usage
            MEMORY=$(redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD INFO memory | grep used_memory_human | cut -d ":" -f2 | tr -d "\r")
            echo -e "${GREEN}✓ Memory usage: $MEMORY${NC}"
            
            # Check database size
            DBSIZE=$(redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD DBSIZE)
            echo -e "${GREEN}✓ Number of keys: $DBSIZE${NC}"
            
            # Check if AOF is enabled
            AOF=$(redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD CONFIG GET appendonly | awk 'NR==2')
            if [ "$AOF" == "yes" ]; then
                echo -e "${GREEN}✓ AOF persistence is enabled${NC}"
            else
                echo -e "${YELLOW}⚠ AOF persistence is disabled${NC}"
            fi
            
            # Check client count
            CLIENTS=$(redis-cli -h $REDIS_HOST -p $REDIS_PORT -a $REDIS_PASSWORD INFO clients | grep connected_clients | cut -d ":" -f2 | tr -d "\r")
            echo -e "${GREEN}✓ Connected clients: $CLIENTS${NC}"
            
            return 0
        else
            echo -e "${RED}✗ Redis is not responsive${NC}"
            return 1
        fi
    else
        echo -e "${RED}✗ Redis service is not running${NC}"
        return 1
    fi
}

# Function to check Chroma health
check_chroma_health() {
    echo -e "\n${YELLOW}Checking Chroma health...${NC}"
    
    # Check if Chroma is running
    if nc -z $CHROMA_HOST $CHROMA_PORT; then
        echo -e "${GREEN}✓ Chroma service is running${NC}"
        
        # Check if Chroma API is responsive
        if curl -s -o /dev/null -w "%{http_code}" http://$CHROMA_HOST:$CHROMA_PORT/api/v1/heartbeat | grep -q "200"; then
            echo -e "${GREEN}✓ Chroma API is responsive${NC}"
            
            # Get Chroma version if available
            VERSION=$(curl -s http://$CHROMA_HOST:$CHROMA_PORT/api/v1/version 2>/dev/null | grep -o '"version":"[^"]*"' | cut -d '"' -f 4)
            if [ -n "$VERSION" ]; then
                echo -e "${GREEN}✓ Chroma version: $VERSION${NC}"
            else
                echo -e "${YELLOW}⚠ Could not determine Chroma version${NC}"
            fi
            
            # Check collections if API supports it
            COLLECTIONS=$(curl -s http://$CHROMA_HOST:$CHROMA_PORT/api/v1/collections 2>/dev/null)
            if [ -n "$COLLECTIONS" ] && [ "$COLLECTIONS" != "Not Found" ]; then
                COLLECTION_COUNT=$(echo $COLLECTIONS | grep -o '"id"' | wc -l)
                echo -e "${GREEN}✓ Number of collections: $COLLECTION_COUNT${NC}"
            else
                echo -e "${YELLOW}⚠ Could not retrieve collections information${NC}"
            fi
            
            return 0
        else
            echo -e "${RED}✗ Chroma API is not responsive${NC}"
            return 1
        fi
    else
        echo -e "${RED}✗ Chroma service is not running${NC}"
        return 1
    fi
}

# Main function to run all health checks
main() {
    echo -e "${YELLOW}RPGer Database Stack Health Check${NC}"
    echo -e "${YELLOW}===============================${NC}"
    echo -e "Date: $(date)"
    
    # Check if required tools are installed
    command -v nc >/dev/null 2>&1 || { echo -e "${RED}Error: netcat (nc) is required but not installed.${NC}"; exit 1; }
    command -v curl >/dev/null 2>&1 || { echo -e "${RED}Error: curl is required but not installed.${NC}"; exit 1; }
    
    # Run health checks
    MONGODB_STATUS=0
    REDIS_STATUS=0
    CHROMA_STATUS=0
    
    check_mongodb_health || MONGODB_STATUS=1
    check_redis_health || REDIS_STATUS=1
    check_chroma_health || CHROMA_STATUS=1
    
    # Summary
    echo -e "\n${YELLOW}Health Check Summary${NC}"
    echo -e "${YELLOW}===================${NC}"
    
    if [ $MONGODB_STATUS -eq 0 ]; then
        echo -e "${GREEN}MongoDB: Healthy${NC}"
    else
        echo -e "${RED}MongoDB: Unhealthy${NC}"
    fi
    
    if [ $REDIS_STATUS -eq 0 ]; then
        echo -e "${GREEN}Redis: Healthy${NC}"
    else
        echo -e "${RED}Redis: Unhealthy${NC}"
    fi
    
    if [ $CHROMA_STATUS -eq 0 ]; then
        echo -e "${GREEN}Chroma: Healthy${NC}"
    else
        echo -e "${RED}Chroma: Unhealthy${NC}"
    fi
    
    # Overall status
    if [ $MONGODB_STATUS -eq 0 ] && [ $REDIS_STATUS -eq 0 ] && [ $CHROMA_STATUS -eq 0 ]; then
        echo -e "\n${GREEN}Overall Status: All services are healthy${NC}"
        exit 0
    else
        echo -e "\n${RED}Overall Status: One or more services are unhealthy${NC}"
        exit 1
    fi
}

# Run the main function
main
