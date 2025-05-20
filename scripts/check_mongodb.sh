#!/bin/bash
# Script to check if MongoDB is running and start it if needed

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Checking MongoDB status..."

# Check if MongoDB is running
if pgrep -x "mongod" > /dev/null
then
    echo -e "${GREEN}MongoDB is running.${NC}"
    exit 0
else
    echo -e "${YELLOW}MongoDB is not running. Attempting to start...${NC}"
    
    # Check if we're running in Docker
    if [ -f /.dockerenv ]; then
        echo -e "${YELLOW}Running in Docker environment. MongoDB should be started as a separate container.${NC}"
        echo -e "${YELLOW}Please ensure the MongoDB container is running with: docker-compose up -d mongodb${NC}"
        exit 1
    fi
    
    # Try to start MongoDB service
    if command -v systemctl > /dev/null; then
        echo "Using systemctl to start MongoDB..."
        sudo systemctl start mongod
        sleep 2
        
        if systemctl is-active --quiet mongod; then
            echo -e "${GREEN}MongoDB started successfully.${NC}"
            exit 0
        else
            echo -e "${RED}Failed to start MongoDB with systemctl.${NC}"
        fi
    elif command -v service > /dev/null; then
        echo "Using service to start MongoDB..."
        sudo service mongod start
        sleep 2
        
        if pgrep -x "mongod" > /dev/null; then
            echo -e "${GREEN}MongoDB started successfully.${NC}"
            exit 0
        else
            echo -e "${RED}Failed to start MongoDB with service.${NC}"
        fi
    else
        echo -e "${RED}Could not find systemctl or service commands.${NC}"
    fi
    
    # Try to start MongoDB directly
    echo "Attempting to start MongoDB directly..."
    if command -v mongod > /dev/null; then
        echo "Found mongod command. Starting MongoDB in the background..."
        mongod --dbpath /var/lib/mongodb --logpath /var/log/mongodb/mongod.log --fork
        
        sleep 2
        if pgrep -x "mongod" > /dev/null; then
            echo -e "${GREEN}MongoDB started successfully.${NC}"
            exit 0
        else
            echo -e "${RED}Failed to start MongoDB directly.${NC}"
        fi
    else
        echo -e "${RED}MongoDB (mongod) command not found.${NC}"
    fi
    
    echo -e "${RED}All attempts to start MongoDB failed.${NC}"
    echo -e "${YELLOW}Please check if MongoDB is installed correctly and try to start it manually.${NC}"
    echo -e "${YELLOW}You can install MongoDB with:${NC}"
    echo -e "  Ubuntu/Debian: sudo apt install mongodb"
    echo -e "  CentOS/RHEL: sudo yum install mongodb"
    echo -e "  macOS: brew install mongodb-community"
    
    exit 1
fi
