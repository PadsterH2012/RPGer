#!/bin/bash

# RPGer Startup Script
# This script starts MongoDB and Redis containers, Flask-SocketIO backend, and the React frontend

echo "=== Starting RPGer Application ==="

# Kill any existing Flask-SocketIO processes
echo "Checking for existing Flask-SocketIO processes..."
pkill -f "python.*rpg_web_app.py" || true

# Kill any existing Node.js server processes
echo "Checking for existing Node.js server processes..."
pkill -f "node.*src/index.ts" || true

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is installed and running"

# Navigate to the App directory
cd "$(dirname "$0")/.."
APP_DIR="$(pwd)"
echo "Working in directory: $APP_DIR"

# Check if docker-compose.yml exists
if [ ! -f "$APP_DIR/App/docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found at $APP_DIR/App/docker-compose.yml"
    exit 1
fi

# Create .env file for database mode
if [ -d "$APP_DIR/App/server" ]; then
    echo "Creating .env file for server..."
    cat > "$APP_DIR/App/server/.env" << EOL
# Server Configuration
PORT=5001
NODE_ENV=development

# Client URL
CLIENT_URL=http://localhost:3000

# Database Configuration
MONGODB_ENABLED=true
MONGODB_URI=mongodb://localhost:27017/rpger
REDIS_ENABLED=true
REDIS_URL=redis://localhost:6379

# JWT Secret (for authentication)
JWT_SECRET=your_jwt_secret_here

# Logging
LOG_LEVEL=debug
EOL
    echo "Created .env file for database mode"
else
    echo "⚠️ Server directory not found at $APP_DIR/App/server, skipping .env creation"
fi

# Start Docker Compose services
echo "Starting MongoDB and Redis with Docker Compose..."
cd "$APP_DIR/App" && docker compose up -d mongodb redis

# Wait for MongoDB and Redis to start
echo "Waiting for MongoDB and Redis to start..."
sleep 5

# Seed the database if server directory exists
if [ -d "$APP_DIR/App/server" ]; then
    echo "Seeding the database..."
    cd "$APP_DIR/App/server" && npm run seed
    cd "$APP_DIR"
else
    echo "⚠️ Server directory not found, skipping database seeding"
fi

# Create .env file for client to connect to Flask-SocketIO backend
if [ -d "$APP_DIR/App/client" ]; then
    echo "Configuring React client..."
    cat > "$APP_DIR/App/client/.env" << EOL
REACT_APP_API_URL=http://localhost:5001
REACT_APP_SOCKET_URL=http://localhost:5002
EOL
    echo "Created .env file for client"
else
    echo "⚠️ Client directory not found at $APP_DIR/App/client, skipping .env creation"
fi

# Start Flask-SocketIO backend in the background
echo "Starting Flask-SocketIO backend..."
if [ ! -d "$APP_DIR/App/backend" ]; then
    echo "❌ Backend directory not found at $APP_DIR/App/backend"
    exit 1
fi

cd "$APP_DIR/App/backend"
echo "Working in backend directory: $(pwd)"

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

# Start Flask-SocketIO in the background
echo "Starting rpg_web_app.py..."
python rpg_web_app.py &
FLASK_PID=$!

# Set up trap to kill Flask when script exits
trap "echo 'Stopping Flask backend...'; kill $FLASK_PID 2>/dev/null" EXIT

# Wait a moment for Flask to start
echo "Waiting for Flask-SocketIO to start..."
sleep 5

# Check if Flask is running
if curl -s http://localhost:5002/api/socketio-status > /dev/null; then
    echo "✅ Flask-SocketIO backend started at http://localhost:5002"
else
    echo "⚠️ Flask-SocketIO backend started but health check endpoint not available"
    echo "Checking if process is still running..."
    if ps -p $FLASK_PID > /dev/null; then
        echo "✅ Process is still running with PID $FLASK_PID"
    else
        echo "❌ Process is not running! Check for errors above."
        exit 1
    fi
fi

# Return to the App directory
cd "$APP_DIR/App"

# Wait for Flask backend to start
echo "Waiting for Flask backend to start..."
sleep 3

# Start the React frontend
if [ -d "$APP_DIR/App/client" ]; then
    echo "Starting React frontend..."
    cd "$APP_DIR/App/client" && npm start
else
    echo "❌ Client directory not found at $APP_DIR/App/client"
    exit 1
fi
