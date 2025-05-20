#!/bin/bash
# Database Stack Testing Script for RPGer
# This script tests the database stack to verify it's working correctly

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_SCRIPT="${SCRIPT_DIR}/test_endpoints.py"

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}   RPGer Database Stack Testing         ${NC}"
echo -e "${BLUE}=========================================${NC}"

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}Python test script not found: ${PYTHON_SCRIPT}${NC}"
    exit 1
fi

# Make sure Python script is executable
chmod +x "$PYTHON_SCRIPT"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is not installed. Please install Python 3.${NC}"
    exit 1
fi

# Check for required Python packages
echo -e "\n${BLUE}Checking for required Python packages...${NC}"
REQUIRED_PACKAGES=("requests" "pymongo" "redis" "chromadb")
MISSING_PACKAGES=()

for package in "${REQUIRED_PACKAGES[@]}"; do
    if ! python3 -c "import $package" &> /dev/null; then
        MISSING_PACKAGES+=("$package")
    fi
done

if [ ${#MISSING_PACKAGES[@]} -gt 0 ]; then
    echo -e "${YELLOW}The following required packages are missing:${NC}"
    for package in "${MISSING_PACKAGES[@]}"; do
        echo "  - $package"
    done
    
    echo -e "\n${YELLOW}Would you like to install them now? (y/n)${NC}"
    read -p "Install packages? " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Installing missing packages...${NC}"
        python3 -m pip install "${MISSING_PACKAGES[@]}"
        
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to install packages. Please install them manually:${NC}"
            echo "pip install ${MISSING_PACKAGES[@]}"
            exit 1
        fi
    else
        echo -e "${YELLOW}Please install the required packages manually:${NC}"
        echo "pip install ${MISSING_PACKAGES[@]}"
        exit 1
    fi
fi

# Parse command line arguments
HOST="localhost"
PORT="5002"
VERBOSE=""

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
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Usage: $0 [--host HOST] [--port PORT] [--verbose]"
            exit 1
            ;;
    esac
done

# Run the Python test script
echo -e "\n${BLUE}Running database stack tests...${NC}"
python3 "$PYTHON_SCRIPT" --host "$HOST" --port "$PORT" $VERBOSE

# Check the exit code
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "\n${GREEN}All tests passed!${NC}"
    echo -e "${GREEN}The database stack is working correctly.${NC}"
else
    echo -e "\n${RED}Some tests failed.${NC}"
    echo -e "${YELLOW}Please check the output above for details.${NC}"
fi

# Provide additional information
echo -e "\n${BLUE}Additional Information:${NC}"
echo -e "- To test with a different host: $0 --host your-host"
echo -e "- To test with a different port: $0 --port your-port"
echo -e "- To see detailed test results: $0 --verbose"
echo -e "- To check MongoDB status: docker ps | grep mongodb"
echo -e "- To check Redis status: docker ps | grep redis"
echo -e "- To check Chroma status: docker ps | grep chroma"

exit $EXIT_CODE
