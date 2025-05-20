#!/bin/bash
# Chroma Initialization Script for RPGer
# This script initializes the Chroma vector database with required configuration

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PYTHON_SCRIPT="${SCRIPT_DIR}/init_chroma.py"

echo -e "${BLUE}=========================================${NC}"
echo -e "${BLUE}   RPGer Chroma Initialization          ${NC}"
echo -e "${BLUE}=========================================${NC}"

# Check if Python script exists
if [ ! -f "$PYTHON_SCRIPT" ]; then
    echo -e "${RED}Python initialization script not found: ${PYTHON_SCRIPT}${NC}"
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
if ! python3 -c "import chromadb" &> /dev/null; then
    echo -e "${YELLOW}chromadb package is missing. Would you like to install it now? (y/n)${NC}"
    read -p "Install package? " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${BLUE}Installing chromadb package...${NC}"
        python3 -m pip install chromadb
        
        if [ $? -ne 0 ]; then
            echo -e "${RED}Failed to install chromadb. Please install it manually:${NC}"
            echo "pip install chromadb"
            exit 1
        fi
    else
        echo -e "${YELLOW}Please install the required package manually:${NC}"
        echo "pip install chromadb"
        exit 1
    fi
fi

# Parse command line arguments
HOST="localhost"
PORT="8000"
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

# Run the Python initialization script
echo -e "\n${BLUE}Initializing Chroma...${NC}"
python3 "$PYTHON_SCRIPT" --host "$HOST" --port "$PORT" $VERBOSE

# Check the exit code
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "\n${GREEN}Chroma initialization completed successfully!${NC}"
    echo -e "${GREEN}You can now run the database tests again to verify the connection.${NC}"
else
    echo -e "\n${RED}Chroma initialization failed.${NC}"
    echo -e "${YELLOW}Please check the output above for details.${NC}"
fi

# Provide additional information
echo -e "\n${BLUE}Additional Information:${NC}"
echo -e "- To initialize Chroma with a different host: $0 --host your-host"
echo -e "- To initialize Chroma with a different port: $0 --port your-port"
echo -e "- To see detailed initialization information: $0 --verbose"
echo -e "- To check Chroma status: docker logs rpger-chroma"
echo -e "- To test database connections: ./scripts/test_db_comprehensive.sh"

exit $EXIT_CODE
