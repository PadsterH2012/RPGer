#!/bin/bash

# Create .env file for in-memory mode
cat > server/.env << EOL
# Server Configuration
PORT=5000
NODE_ENV=development

# Client URL
CLIENT_URL=http://localhost:3000

# Database Configuration - Disabled for in-memory mode
MONGODB_ENABLED=false
REDIS_ENABLED=false

# JWT Secret (for authentication)
JWT_SECRET=your_jwt_secret_here

# Logging
LOG_LEVEL=debug
EOL

echo "Created .env file for in-memory mode"
echo "Starting application in in-memory mode..."

# Start the application
npm run dev
