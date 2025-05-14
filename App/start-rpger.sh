#!/bin/bash

# Start RPGer Dashboard

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Node.js is not installed. Please install Node.js to run this application."
    exit 1
fi

# Function to check if a port is in use
is_port_in_use() {
    lsof -i:"$1" >/dev/null 2>&1
    return $?
}

# Function to kill process using a specific port
kill_process_on_port() {
    local PORT=$1
    local PID=$(lsof -t -i:$PORT)
    if [ ! -z "$PID" ]; then
        echo "Killing process $PID using port $PORT"
        kill -9 $PID
        sleep 1
    fi
}

# Clean up any existing processes
echo "Checking for existing processes..."
if is_port_in_use 5001; then
    echo "Port 5001 is already in use. Killing the process..."
    kill_process_on_port 5001
fi

# Check for React development server ports
for PORT in 3000 3001 3002 3003; do
    if is_port_in_use $PORT; then
        echo "Port $PORT is already in use. Killing the process..."
        kill_process_on_port $PORT
    fi
done

# Create necessary files if they don't exist
echo "Checking for required files..."
if [ ! -f "client/public/logo192.png" ] || [ ! -s "client/public/logo192.png" ]; then
    echo "Downloading logo files..."
    mkdir -p client/public
    curl -s -o client/public/logo192.png https://raw.githubusercontent.com/facebook/create-react-app/main/packages/cra-template/template/public/logo192.png
    curl -s -o client/public/logo512.png https://raw.githubusercontent.com/facebook/create-react-app/main/packages/cra-template/template/public/logo512.png
    curl -s -o client/public/favicon.ico https://raw.githubusercontent.com/facebook/create-react-app/main/packages/cra-template/template/public/favicon.ico
fi

# Start the server in the background
echo "Starting RPGer server on port 5001..."
node /mnt/network_repo/test_ai_rpg/RPGer/server/simple-server.js &
SERVER_PID=$!

# Wait for the server to start
echo "Waiting for server to start..."
sleep 2

# Check if the server started successfully
MAX_RETRIES=5
RETRY_COUNT=0
SERVER_STARTED=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:5001/api/health > /dev/null; then
        SERVER_STARTED=true
        break
    fi
    echo "Server not ready yet. Retrying in 2 seconds..."
    RETRY_COUNT=$((RETRY_COUNT + 1))
    sleep 2
done

if [ "$SERVER_STARTED" = false ]; then
    echo "Failed to start the server after $MAX_RETRIES attempts. Please check the logs for errors."
    kill $SERVER_PID 2>/dev/null
    exit 1
fi

echo "Server started successfully!"
echo "Server is running at: http://localhost:5001"

# Start the React client in the current terminal
echo "Starting RPGer client..."
echo "If prompted to use a different port, select 'Yes'."
echo "Press Ctrl+C to stop both the client and server when you're done."

# Set up trap to kill the server when the script exits
trap "echo 'Stopping server...'; kill $SERVER_PID 2>/dev/null" EXIT

# Start the client
echo "Starting client..."
cd client && BROWSER=none npx react-scripts start

# This point is reached only if the client is stopped
echo "Client stopped. Stopping server..."
kill $SERVER_PID 2>/dev/null
