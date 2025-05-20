#!/bin/bash
# Internal Database Connection Testing Script for RPGer
# This script tests database connections from within the backend container

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_SCRIPT="${SCRIPT_DIR}/test_db_connections_internal.py"

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}   RPGer Internal DB Connection Testing  ${NC}"
echo -e "${BLUE}=========================================${NC}"

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}Python test script not found: ${PYTHON_SCRIPT}${NC}"
    exit 1
fi

# Make sure Python script is executable
chmod +x "$PYTHON_SCRIPT"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if the backend container is running
BACKEND_CONTAINER=$(docker ps --filter "name=rpger-backend" --format "{{.Names}}")
if [ -z "$BACKEND_CONTAINER" ]; then
    echo -e "${RED}Backend container is not running. Please start the backend container first.${NC}"
    exit 1
fi

echo -e "\n${BLUE}Copying test script to backend container...${NC}"
docker cp "$PYTHON_SCRIPT" "$BACKEND_CONTAINER:/app/test_db_connections_internal.py"

# Parse command line arguments
VERBOSE=""
if [[ "$*" == *"--verbose"* ]]; then
    VERBOSE="--verbose"
fi

# Run the Python test script inside the container
echo -e "\n${BLUE}Running database connection tests inside the container...${NC}"
docker exec "$BACKEND_CONTAINER" python /app/test_db_connections_internal.py $VERBOSE

# Check the exit code
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "\n${GREEN}All internal tests passed!${NC}"
    echo -e "${GREEN}The database connections from within the container are working correctly.${NC}"
else
    echo -e "\n${RED}Some internal tests failed.${NC}"
    echo -e "${YELLOW}Please check the output above for details.${NC}"
fi

# Provide additional information
echo -e "\n${BLUE}Additional Information:${NC}"
echo -e "- To see detailed test results: $0 --verbose"
echo -e "- To check MongoDB status: docker logs rpger-mongodb"
echo -e "- To check Redis status: docker logs rpger-redis"
echo -e "- To check Chroma status: docker logs rpger-chroma"
echo -e "- To check backend logs: docker logs rpger-backend"

# Clean up
echo -e "\n${BLUE}Cleaning up...${NC}"
docker exec "$BACKEND_CONTAINER" rm -f /app/test_db_connections_internal.py

exit $EXIT_CODE
