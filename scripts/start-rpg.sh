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

# Create .env file for backend
if [ -d "$APP_DIR/App/backend" ]; then
    echo "Creating .env file for Flask backend..."
    cat > "$APP_DIR/App/backend/.env" << EOL
# RPGer Backend Environment Variables

# Server Configuration
PORT=5002
DEBUG=true
SECRET_KEY=development_secret_key

# MongoDB Configuration
# Use the appropriate connection string for your environment
MONGODB_URI=mongodb://localhost:27017/rpger

# MongoDB Connection Options
MONGODB_CONNECT_TIMEOUT_MS=10000
MONGODB_SOCKET_TIMEOUT_MS=10000
MONGODB_SERVER_SELECTION_TIMEOUT_MS=10000
MONGODB_MAX_POOL_SIZE=50
MONGODB_MIN_POOL_SIZE=5
MONGODB_MAX_IDLE_TIME_MS=60000

# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_SOCKET_TIMEOUT=2
REDIS_SOCKET_CONNECT_TIMEOUT=2
REDIS_RETRY_ON_TIMEOUT=true

# Chroma Configuration
CHROMA_HOST=localhost
CHROMA_PORT=8000

# CORS Configuration
# Add additional origins as needed, separated by commas
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000

# Socket.IO Configuration
SOCKET_PING_TIMEOUT=60
SOCKET_PING_INTERVAL=25
SOCKET_ASYNC_MODE=eventlet

# Application Behavior
AUTO_CONTINUE_WITHOUT_MONGODB=true

# Logging Configuration
LOG_LEVEL=INFO
EOL
    echo "Created .env file for Flask backend"
else
    echo "⚠️ Backend directory not found at $APP_DIR/App/backend, skipping .env creation"
fi

# Start Docker Compose services
echo "Starting MongoDB and Redis with Docker Compose..."
cd "$APP_DIR/App" && docker compose up -d mongodb redis

# Wait for MongoDB and Redis to start
echo "Waiting for MongoDB and Redis to start..."
sleep 5

# Check if MongoDB is running
echo "Verifying MongoDB connection..."
MAX_RETRIES=5
RETRY_COUNT=0
MONGODB_READY=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ] && [ "$MONGODB_READY" = false ]; do
    if docker exec -it mongodb mongosh --eval "db.runCommand({ping:1})" > /dev/null 2>&1; then
        echo "✅ MongoDB is running and accepting connections"
        MONGODB_READY=true
    else
        RETRY_COUNT=$((RETRY_COUNT+1))
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            echo "⚠️ MongoDB not ready yet. Retrying in 3 seconds... (Attempt $RETRY_COUNT/$MAX_RETRIES)"
            sleep 3
        else
            echo "❌ MongoDB failed to start properly after $MAX_RETRIES attempts"
            echo "⚠️ The application will continue, but MongoDB features may not work correctly"
        fi
    fi
done

# Check if Redis is running
echo "Verifying Redis connection..."
MAX_RETRIES=5
RETRY_COUNT=0
REDIS_READY=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ] && [ "$REDIS_READY" = false ]; do
    if docker exec -it redis redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis is running and accepting connections"
        REDIS_READY=true
    else
        RETRY_COUNT=$((RETRY_COUNT+1))
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            echo "⚠️ Redis not ready yet. Retrying in 3 seconds... (Attempt $RETRY_COUNT/$MAX_RETRIES)"
            sleep 3
        else
            echo "❌ Redis failed to start properly after $MAX_RETRIES attempts"
            echo "⚠️ The application will continue, but Redis features may not work correctly"
        fi
    fi
done

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

# Check if requirements.txt exists and install dependencies if needed
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found in $(pwd)"
    echo "Creating minimal requirements.txt..."
    cat > requirements.txt << EOL
flask==2.2.3
flask-socketio==5.3.6
flask-cors==4.0.0
pymongo==4.6.1
redis==5.0.1
eventlet==0.33.3
requests==2.31.0
EOL
    echo "Created minimal requirements.txt"
    pip install -r requirements.txt
fi

# Start Flask-SocketIO in the background
echo "Starting rpg_web_app.py..."
python rpg_web_app.py > flask_output.log 2>&1 &
FLASK_PID=$!

# Set up trap to kill Flask when script exits
trap "echo 'Stopping Flask backend...'; kill $FLASK_PID 2>/dev/null" EXIT

# Wait a moment for Flask to start
echo "Waiting for Flask-SocketIO to start..."
sleep 5

# Check if Flask is running
MAX_RETRIES=5
RETRY_COUNT=0
FLASK_READY=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ] && [ "$FLASK_READY" = false ]; do
    if curl -s http://localhost:5002/api/socketio-status > /dev/null; then
        echo "✅ Flask-SocketIO backend started at http://localhost:5002"
        FLASK_READY=true
    else
        RETRY_COUNT=$((RETRY_COUNT+1))
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            echo "⚠️ Flask-SocketIO not ready yet. Retrying in 3 seconds... (Attempt $RETRY_COUNT/$MAX_RETRIES)"
            # Check if process is still running
            if ps -p $FLASK_PID > /dev/null; then
                echo "Process is still running with PID $FLASK_PID"
                # Show the last few lines of the log
                echo "Recent log output:"
                tail -n 5 flask_output.log
            else
                echo "❌ Process died! Check flask_output.log for errors."
                echo "Last 20 lines of log:"
                tail -n 20 flask_output.log
                exit 1
            fi
            sleep 3
        else
            echo "❌ Flask-SocketIO failed to start properly after $MAX_RETRIES attempts"
            echo "Checking if process is still running..."
            if ps -p $FLASK_PID > /dev/null; then
                echo "✅ Process is still running with PID $FLASK_PID but health check failed"
                echo "Check flask_output.log for errors"
                echo "Last 20 lines of log:"
                tail -n 20 flask_output.log
                echo "The application will continue, but some features may not work correctly"
            else
                echo "❌ Process is not running! Check flask_output.log for errors."
                echo "Last 20 lines of log:"
                tail -n 20 flask_output.log
                exit 1
            fi
        fi
    fi
done

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
