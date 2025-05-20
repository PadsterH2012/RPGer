#!/bin/bash
# Comprehensive Database Testing Script for RPGer
# This script runs both external and internal database tests

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
EXTERNAL_TEST="${SCRIPT_DIR}/test_db_stack.sh"
INTERNAL_TEST="${SCRIPT_DIR}/test_db_internal.sh"

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}   RPGer Comprehensive DB Testing        ${NC}"
echo -e "${BLUE}=========================================${NC}"

# Check if test scripts exist
if [ ! -f "$EXTERNAL_TEST" ]; then
    echo -e "${RED}External test script not found: ${EXTERNAL_TEST}${NC}"
    exit 1
fi

if [ ! -f "$INTERNAL_TEST" ]; then
    echo -e "${RED}Internal test script not found: ${INTERNAL_TEST}${NC}"
    exit 1
fi

# Make sure test scripts are executable
chmod +x "$EXTERNAL_TEST"
chmod +x "$INTERNAL_TEST"

# Parse command line arguments
VERBOSE=""
if [[ "$*" == *"--verbose"* ]]; then
    VERBOSE="--verbose"
fi

# Run the external tests
echo -e "\n${BLUE}Running external database tests (from host)...${NC}"
echo -e "${BLUE}----------------------------------------${NC}"
"$EXTERNAL_TEST" $VERBOSE
EXTERNAL_EXIT_CODE=$?

# Run the internal tests
echo -e "\n${BLUE}Running internal database tests (from container)...${NC}"
echo -e "${BLUE}----------------------------------------${NC}"
"$INTERNAL_TEST" $VERBOSE
INTERNAL_EXIT_CODE=$?

# Summary
echo -e "\n${BLUE}=========================================${NC}"
echo -e "${BLUE}   Comprehensive Test Summary            ${NC}"
echo -e "${BLUE}=========================================${NC}"

echo -e "External Tests (from host): $([ $EXTERNAL_EXIT_CODE -eq 0 ] && echo "${GREEN}PASS${NC}" || echo "${RED}FAIL${NC}")"
echo -e "Internal Tests (from container): $([ $INTERNAL_EXIT_CODE -eq 0 ] && echo "${GREEN}PASS${NC}" || echo "${RED}FAIL${NC}")"

# Overall result
if [ $EXTERNAL_EXIT_CODE -eq 0 ] && [ $INTERNAL_EXIT_CODE -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed!${NC}"
    echo -e "${GREEN}The database stack is working correctly from both host and container.${NC}"
    EXIT_CODE=0
elif [ $EXTERNAL_EXIT_CODE -ne 0 ] && [ $INTERNAL_EXIT_CODE -eq 0 ]; then
    echo -e "\n${YELLOW}External tests failed, but internal tests passed.${NC}"
    echo -e "${YELLOW}This suggests a network configuration issue between the host and containers.${NC}"
    echo -e "${YELLOW}Check port mappings and host network configuration.${NC}"
    EXIT_CODE=1
elif [ $EXTERNAL_EXIT_CODE -eq 0 ] && [ $INTERNAL_EXIT_CODE -ne 0 ]; then
    echo -e "\n${YELLOW}External tests passed, but internal tests failed.${NC}"
    echo -e "${YELLOW}This suggests a container networking issue or incorrect container names in the configuration.${NC}"
    echo -e "${YELLOW}Check Docker network configuration and container environment variables.${NC}"
    EXIT_CODE=1
else
    echo -e "\n${RED}Both external and internal tests failed.${NC}"
    echo -e "${RED}This suggests that the database services may not be running correctly.${NC}"
    echo -e "${RED}Check if all database containers are running and properly configured.${NC}"
    EXIT_CODE=1
fi

# Provide additional information
echo -e "\n${BLUE}Additional Information:${NC}"
echo -e "- To see detailed test results: $0 --verbose"
echo -e "- To check container status: docker ps"
echo -e "- To check container logs: docker logs <container-name>"
echo -e "- To check Docker networks: docker network ls"
echo -e "- To inspect Docker network: docker network inspect rpger-network"

exit $EXIT_CODE
