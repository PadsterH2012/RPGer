#!/bin/bash
# Comprehensive Testing Script for RPGer
# This script runs all tests to verify the system is working correctly

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DB_TEST_SCRIPT="${SCRIPT_DIR}/test_db_stack.sh"
API_TEST_SCRIPT="${SCRIPT_DIR}/test_api.sh"

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}   RPGer Comprehensive Testing          ${NC}"
echo -e "${BLUE}=========================================${NC}"
echo -e "Timestamp: $(date)"

# Check if test scripts exist
if [ ! -f "$DB_TEST_SCRIPT" ]; then
    echo -e "${RED}Database test script not found: ${DB_TEST_SCRIPT}${NC}"
    exit 1
fi

if [ ! -f "$API_TEST_SCRIPT" ]; then
    echo -e "${RED}API test script not found: ${API_TEST_SCRIPT}${NC}"
    exit 1
fi

# Make sure test scripts are executable
chmod +x "$DB_TEST_SCRIPT" "$API_TEST_SCRIPT"

# Parse command line arguments
HOST="localhost"
PORT="5002"
VERBOSE=""
SKIP_DB=""
SKIP_API=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            HOST="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE="--verbose"
            shift
            ;;
        --skip-db)
            SKIP_DB="true"
            shift
            ;;
        --skip-api)
            SKIP_API="true"
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Usage: $0 [--host HOST] [--port PORT] [--verbose] [--skip-db] [--skip-api]"
            exit 1
            ;;
    esac
done

# Check if the server is running
echo -e "\n${BLUE}Checking if the server is running...${NC}"
if ! curl -s "http://${HOST}:${PORT}/api/health" > /dev/null; then
    echo -e "${YELLOW}Server does not appear to be running at http://${HOST}:${PORT}${NC}"
    echo -e "Would you like to start the server? (y/n)"
    read -p "Start server? " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Starting the server...${NC}"
        
        # Check if start-rpg.sh exists
        if [ -f "${SCRIPT_DIR}/start-rpg.sh" ]; then
            # Start the server in the background
            "${SCRIPT_DIR}/start-rpg.sh" &
            SERVER_PID=$!
            
            # Wait for the server to start
            echo -e "${BLUE}Waiting for the server to start...${NC}"
            for i in {1..30}; do
                if curl -s "http://${HOST}:${PORT}/api/health" > /dev/null; then
                    echo -e "${GREEN}Server started successfully.${NC}"
                    break
                fi
                
                if [ $i -eq 30 ]; then
                    echo -e "${RED}Server failed to start within 30 seconds.${NC}"
                    echo -e "${RED}Please start the server manually and try again.${NC}"
                    exit 1
                fi
                
                echo -n "."
                sleep 1
            done
            echo
        else
            echo -e "${RED}start-rpg.sh script not found. Please start the server manually.${NC}"
            exit 1
        fi
    else
        echo -e "${RED}Server is not running. Please start the server and try again.${NC}"
        exit 1
    fi
fi

# Run database tests
if [ -z "$SKIP_DB" ]; then
    echo -e "\n${BLUE}Running database stack tests...${NC}"
    "$DB_TEST_SCRIPT" --host "$HOST" --port "$PORT" $VERBOSE
    DB_EXIT_CODE=$?
    
    if [ $DB_EXIT_CODE -eq 0 ]; then
        echo -e "\n${GREEN}Database stack tests passed!${NC}"
    else
        echo -e "\n${RED}Database stack tests failed.${NC}"
    fi
else
    echo -e "\n${YELLOW}Skipping database stack tests.${NC}"
    DB_EXIT_CODE=0
fi

# Run API tests
if [ -z "$SKIP_API" ]; then
    echo -e "\n${BLUE}Running API endpoint tests...${NC}"
    "$API_TEST_SCRIPT" --host "$HOST" --port "$PORT" $VERBOSE
    API_EXIT_CODE=$?
    
    if [ $API_EXIT_CODE -eq 0 ]; then
        echo -e "\n${GREEN}API endpoint tests passed!${NC}"
    else
        echo -e "\n${RED}API endpoint tests failed.${NC}"
    fi
else
    echo -e "\n${YELLOW}Skipping API endpoint tests.${NC}"
    API_EXIT_CODE=0
fi

# Summary
echo -e "\n${BLUE}=========================================${NC}"
echo -e "${BLUE}   Test Summary                         ${NC}"
echo -e "${BLUE}=========================================${NC}"

if [ -z "$SKIP_DB" ]; then
    echo -e "Database Stack Tests: ${DB_EXIT_CODE -eq 0 ? "${GREEN}PASSED${NC}" : "${RED}FAILED${NC}"}"
else
    echo -e "Database Stack Tests: ${YELLOW}SKIPPED${NC}"
fi

if [ -z "$SKIP_API" ]; then
    echo -e "API Endpoint Tests: ${API_EXIT_CODE -eq 0 ? "${GREEN}PASSED${NC}" : "${RED}FAILED${NC}"}"
else
    echo -e "API Endpoint Tests: ${YELLOW}SKIPPED${NC}"
fi

# Overall result
if [ $DB_EXIT_CODE -eq 0 ] && [ $API_EXIT_CODE -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed!${NC}"
    echo -e "${GREEN}The system is working correctly.${NC}"
    EXIT_CODE=0
else
    echo -e "\n${RED}Some tests failed.${NC}"
    echo -e "${YELLOW}Please check the output above for details.${NC}"
    EXIT_CODE=1
fi

# Provide additional information
echo -e "\n${BLUE}Additional Information:${NC}"
echo -e "- To test with a different host: $0 --host your-host"
echo -e "- To test with a different port: $0 --port your-port"
echo -e "- To see detailed test results: $0 --verbose"
echo -e "- To skip database tests: $0 --skip-db"
echo -e "- To skip API tests: $0 --skip-api"
echo -e "- To test only the database stack: ${DB_TEST_SCRIPT}"
echo -e "- To test only the API endpoints: ${API_TEST_SCRIPT}"

exit $EXIT_CODE
