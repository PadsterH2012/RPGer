#!/bin/bash

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Docker is not installed. Please install Docker and Docker Compose first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker compose &> /dev/null; then
    echo "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create .env file for database mode
cat > server/.env << EOL
# Server Configuration
PORT=5000
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

# Start Docker Compose services
echo "Starting MongoDB and Redis with Docker Compose..."
docker compose up -d

# Wait for MongoDB and Redis to start
echo "Waiting for MongoDB and Redis to start..."
sleep 5

# Seed the database
echo "Seeding the database..."
cd server && npm run seed && cd ..

# Start the application
echo "Starting application in database mode..."
npm run dev
