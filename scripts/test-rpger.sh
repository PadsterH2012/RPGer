#!/bin/bash

# Test script for RPGer in new location
# This script starts MongoDB and Redis containers and tests if the application can connect to them

echo "=== RPGer Test Script ==="
echo "Testing if RPGer works in the new location"

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

echo "✅ Docker and Docker Compose are installed and running"

# Navigate to the App directory
cd "$(dirname "$0")/App"
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found. Make sure the App directory contains docker-compose.yml."
    exit 1
fi

# Stop any existing containers
echo "Stopping any existing containers..."
docker compose down

# Start MongoDB and Redis containers
echo "Starting MongoDB and Redis containers..."
docker compose up -d mongodb redis

# Wait for containers to start
echo "Waiting for containers to start..."
sleep 5

# Check if containers are running
if ! docker ps | grep -q "rpger-mongodb"; then
    echo "❌ MongoDB container failed to start"
    docker compose logs mongodb
    exit 1
fi

if ! docker ps | grep -q "rpger-redis"; then
    echo "❌ Redis container failed to start"
    docker compose logs redis
    exit 1
fi

echo "✅ MongoDB and Redis containers are running"

# Create .env file for server
echo "Creating .env file for server..."
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

echo "✅ Server .env file created"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "✅ Node.js and npm are installed"

# Check if node_modules exists in server directory
if [ ! -d "server/node_modules" ]; then
    echo "Installing server dependencies..."
    (cd server && npm install)
fi

# Check if node_modules exists in client directory
if [ ! -d "client/node_modules" ]; then
    echo "Installing client dependencies..."
    (cd client && npm install)
fi

# Seed the database
echo "Seeding the database..."
(cd server && npm run seed)

# Test server connection
echo "Testing server connection..."
node -e "
const mongoose = require('mongoose');
const Redis = require('redis');

async function testConnections() {
  console.log('Testing MongoDB connection...');
  try {
    await mongoose.connect('mongodb://localhost:27017/rpger');
    console.log('✅ MongoDB connection successful');
    await mongoose.disconnect();
  } catch (error) {
    console.error('❌ MongoDB connection failed:', error.message);
    process.exit(1);
  }

  console.log('Testing Redis connection...');
  try {
    const client = Redis.createClient({
      url: 'redis://localhost:6379'
    });
    await client.connect();
    console.log('✅ Redis connection successful');
    await client.disconnect();
  } catch (error) {
    console.error('❌ Redis connection failed:', error.message);
    process.exit(1);
  }

  console.log('All connection tests passed!');
}

testConnections();
"

# If we got here, the test was successful
echo "=== Test Completed Successfully ==="
echo "✅ RPGer can connect to MongoDB and Redis containers"
echo ""
echo "To start the application with database support, run:"
echo "  npm run dev"
echo ""
echo "To stop the containers when you're done, run:"
echo "  docker compose down"
