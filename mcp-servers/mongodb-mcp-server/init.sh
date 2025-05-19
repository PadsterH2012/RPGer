#!/bin/bash

# RPGer MongoDB MCP Server Initialization Script

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check command success
check_success() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ $1${NC}"
    else
        echo -e "${RED}✗ $1 failed${NC}"
        exit 1
    fi
}

# Initialize project
initialize_project() {
    # Install dependencies
    npm install
    check_success "Installed dependencies"
}

# Main initialization function
main() {
    echo -e "${GREEN}RPGer MongoDB MCP Server Initialization${NC}"

    initialize_project

    echo -e "\n${GREEN}✓ Initialization Complete!${NC}"
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Set MONGODB_URI environment variable if needed"
    echo "2. Run 'node index.js <tool_name> <json_params>' to use MCP tools"
}

# Execute main function
main