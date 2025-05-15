# RPGer Application Stack

This directory contains the containerized application infrastructure for the RPGer system.

## Overview

The application stack provides the following services:

1. **Backend**: Node.js/Express or Python-based backend API server
2. **Frontend**: React-based frontend application

## Directory Structure

```
app_stack/
├── docker-compose.yml       # Docker Compose configuration
├── .env                     # Environment variables
├── backend/                 # Backend application code
└── frontend/                # Frontend application code
```

## Configuration

The application stack is configured through the `.env` file, which contains environment variables for:

- Node.js environment (development/production)
- Backend port
- Frontend port
- API URL
- Database credentials (must match db_stack/.env)
- JWT secret for authentication

## Usage

### Starting the Application Stack

You can start the application stack using the master script from the root directory:

```bash
./start-rpger.sh app-only
```

Or directly using Docker Compose:

```bash
cd app_stack
docker-compose up -d
```

Note: The application stack depends on the database stack, so make sure the database stack is running first.

### Accessing the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000

## Development

### Backend Development

The backend code should be placed in the `backend/` directory. This will be mounted as a volume in the container, so changes will be reflected immediately without rebuilding the container.

### Frontend Development

The frontend code should be placed in the `frontend/` directory. This will be mounted as a volume in the container, so changes will be reflected immediately without rebuilding the container.

## Moving Existing Code

To move existing backend and frontend code into this structure:

1. **Backend**:
   ```bash
   # Create the backend directory if it doesn't exist
   mkdir -p app_stack/backend
   
   # Copy existing backend code
   cp -r App/server/* app_stack/backend/
   # or for Python backend
   cp -r App/backend/* app_stack/backend/
   ```

2. **Frontend**:
   ```bash
   # Create the frontend directory if it doesn't exist
   mkdir -p app_stack/frontend
   
   # Copy existing frontend code
   cp -r App/client/* app_stack/frontend/
   ```

## Docker Configuration

### Backend Dockerfile

Create a `Dockerfile` in the `backend/` directory:

```dockerfile
FROM node:18

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 5000

CMD ["npm", "start"]
```

### Frontend Dockerfile

Create a `Dockerfile` in the `frontend/` directory:

```dockerfile
FROM node:18

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
```

## Connecting to Databases

The backend service is configured to connect to the database services using the following connection strings:

- **MongoDB**: `mongodb://admin:password@mongodb:27017/rpger?authSource=admin`
- **Redis**: `redis://:password@redis:6379`

These connection strings use the container names as hostnames, which works because both stacks share the same Docker network.
