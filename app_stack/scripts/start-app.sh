#!/bin/bash

# RPGer Application Stack Startup Script
# This script starts both the backend and frontend components

echo "=== Starting RPGer Application Stack ==="

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_STACK_DIR="$(dirname "$SCRIPT_DIR")"
echo "Working in app_stack directory: $APP_STACK_DIR"

# Create .env file for backend
echo "Creating .env file for backend..."
cat > "$APP_STACK_DIR/backend/.env" << EOL
# RPGer Backend Environment Variables

# OpenRouter API Key
# Get your API key from https://openrouter.ai/
OPENROUTER_API_KEY=your_api_key_here

# Socket.IO Configuration
SOCKET_PORT=5002
EOL
echo "Created .env file for backend"

# Create .env file for frontend
echo "Creating .env file for frontend..."
cat > "$APP_STACK_DIR/frontend/.env" << EOL
VITE_API_URL=http://localhost:5001
VITE_SOCKET_URL=http://localhost:5002
EOL
echo "Created .env file for frontend"

# Start the backend in the background
echo "Starting backend..."
"$SCRIPT_DIR/start-backend.sh" &
BACKEND_PID=$!

# Set up trap to kill backend when script exits
trap "echo 'Stopping backend...'; kill $BACKEND_PID 2>/dev/null" EXIT

# Wait for backend to start
echo "Waiting for backend to start..."
sleep 5

# Start the frontend
echo "Starting frontend..."
"$SCRIPT_DIR/start-frontend.sh"
