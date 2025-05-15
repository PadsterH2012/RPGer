#!/bin/bash

# RPGer Backend Startup Script
# This script starts the Flask-SocketIO backend for the RPGer application

echo "=== Starting RPGer Backend ==="

# Kill any existing Flask-SocketIO processes
echo "Checking for existing Flask-SocketIO processes..."
pkill -f "python.*rpg_web_app.py" || true

# Navigate to the backend directory
cd "$(dirname "$0")/../backend"
BACKEND_DIR="$(pwd)"
echo "Working in backend directory: $BACKEND_DIR"

# Check if Python virtual environment exists
if [ -d "venv" ]; then
    echo "Activating existing Python virtual environment..."
    source venv/bin/activate
else
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
fi

# Start Flask-SocketIO backend
echo "Starting Flask-SocketIO backend..."
python rpg_web_app.py

# This script will stay running until the Flask app is stopped with Ctrl+C
# The trap below ensures we deactivate the virtual environment when exiting
trap "echo 'Deactivating virtual environment...'; deactivate" EXIT
