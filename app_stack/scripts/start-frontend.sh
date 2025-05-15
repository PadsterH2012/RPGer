#!/bin/bash

# RPGer Frontend Startup Script
# This script starts the React frontend for the RPGer application

echo "=== Starting RPGer Frontend ==="

# Navigate to the frontend directory
cd "$(dirname "$0")/../frontend"
FRONTEND_DIR="$(pwd)"
echo "Working in frontend directory: $FRONTEND_DIR"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start the React frontend
echo "Starting React frontend..."
npm start
