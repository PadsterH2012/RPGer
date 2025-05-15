# RPGer Stack Architecture

This document provides an overview of the RPGer stack architecture, which separates the application components from the database components for improved maintainability, scalability, and security.

## Architecture Overview

The RPGer system is divided into two main stacks:

1. **Database Stack (`db_stack/`)**: Contains all database services and their management interfaces
2. **Application Stack (`app_stack/`)**: Contains the backend and frontend application components

```
RPGer/
├── app_stack/                # Application components
│   ├── backend/              # Backend API server
│   ├── frontend/             # React frontend application
│   ├── docker-compose.yml    # Application stack configuration
│   └── .env                  # Application environment variables
│
├── db_stack/                 # Database components
│   ├── init-scripts/         # Database initialization scripts
│   ├── backup-scripts/       # Database backup scripts
│   ├── health-check-scripts/ # Database health check scripts
│   ├── docker-compose.yml    # Database stack configuration
│   └── .env                  # Database environment variables
│
├── start-rpger.sh            # Master script to start/stop all components
└── STACK-README.md           # This file
```

## Benefits of This Architecture

1. **Independent Scaling**: Each stack can be scaled according to its specific resource needs
2. **Improved Security**: Database services can be more isolated from external networks
3. **Simplified Maintenance**: Update or restart application containers without affecting databases
4. **Better Resource Allocation**: Optimize resources for each stack's specific requirements
5. **Clearer Separation of Concerns**: Development teams can focus on their specific domain

## Shared Network

Both stacks communicate through a shared Docker network called `rpger-network`. This allows:

- Application containers to connect to database services using container names as hostnames
- Isolation of the entire system from other Docker containers on the host
- Secure internal communication between services

## Getting Started

### Prerequisites

- Docker and Docker Compose installed
- Git repository cloned

### Starting the Entire System

To start both the database and application stacks:

```bash
./start-rpger.sh start
```

This will:
1. Create the shared Docker network if it doesn't exist
2. Start the database stack and wait for services to be ready
3. Start the application stack
4. Display the status of all containers

### Starting Individual Stacks

To start only the database stack:

```bash
./start-rpger.sh db-only
```

To start only the application stack:

```bash
./start-rpger.sh app-only
```

### Stopping the System

To stop all stacks:

```bash
./start-rpger.sh stop
```

### Checking Status

To check the status of all containers:

```bash
./start-rpger.sh status
```

## Moving Existing Code

To migrate existing code into this structure:

1. **Backend**:
   ```bash
   cp -r App/server/* app_stack/backend/
   # or for Python backend
   cp -r App/backend/* app_stack/backend/
   ```

2. **Frontend**:
   ```bash
   cp -r App/client/* app_stack/frontend/
   ```

3. Create Dockerfiles in each directory (see README files in each stack for examples)

## Accessing Services

After starting the system, you can access:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **MongoDB Admin**: http://localhost:8081
- **Redis Admin**: http://localhost:8082

## Configuration

Each stack has its own `.env` file for configuration:

- `db_stack/.env`: Database credentials, ports, and admin interface settings
- `app_stack/.env`: Application settings, ports, and database connection information

Make sure the database credentials match between both `.env` files.

## Next Steps

1. Move existing backend and frontend code into the appropriate directories
2. Create Dockerfiles for the backend and frontend
3. Test the system with the new architecture
4. Implement automated backups for the database stack
5. Set up monitoring and alerting for all services
