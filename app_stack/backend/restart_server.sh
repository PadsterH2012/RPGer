#!/bin/bash

# Script to restart the RPGer backend server

echo "Restarting RPGer backend server..."

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "WARNING: Not running in a virtual environment. It's recommended to activate your venv first."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted. Please activate your virtual environment and try again."
        exit 1
    fi
fi

# Kill any existing Python processes running rpg_web_app.py
echo "Stopping any existing backend processes..."
pkill -f "python.*rpg_web_app.py" || echo "No existing processes found."

# Wait a moment for processes to terminate
sleep 2

# Start the server in the background
echo "Starting backend server..."
python rpg_web_app.py > server.log 2>&1 &

# Get the PID of the new process
PID=$!
echo "Server started with PID: $PID"

# Wait a moment for the server to start
sleep 3

# Check if the process is still running
if ps -p $PID > /dev/null; then
    echo "Server started successfully!"
    echo "You can view the logs with: tail -f server.log"
else
    echo "Server failed to start. Check server.log for details."
    exit 1
fi
