#!/bin/bash
# Master script to start both database and application stacks

# Set the base directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_STACK_DIR="$BASE_DIR/db_stack"
APP_STACK_DIR="$BASE_DIR/app_stack"

# Function to display messages
log() {
    echo -e "\e[1;34m[RPGer]\e[0m $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        log "\e[1;31mError: Docker is not running. Please start Docker and try again.\e[0m"
        exit 1
    fi
}

# Function to create the shared network if it doesn't exist
create_network() {
    # Check if the network exists
    if docker network inspect rpger-network > /dev/null 2>&1; then
        log "Removing existing rpger-network to avoid conflicts..."
        docker network rm rpger-network
    fi

    # Create a new network
    log "Creating shared Docker network: rpger-network"
    docker network create rpger-network
}

# Function to clean up existing containers
cleanup_containers() {
    log "Cleaning up any existing containers..."

    # List of container names to check and remove
    containers=("rpger-mongodb" "rpger-redis" "rpger-chroma" "rpger-mongo-express" "rpger-redis-commander" "rpger-backend" "rpger-frontend")

    for container in "${containers[@]}"; do
        if docker ps -a --format '{{.Names}}' | grep -q "^$container$"; then
            log "Removing container: $container"
            docker rm -f "$container" > /dev/null 2>&1
        fi
    done
}

# Function to start the database stack
start_db_stack() {
    log "Starting database stack..."
    cd "$DB_STACK_DIR" || exit 1

    # Clean up existing containers first
    cleanup_containers

    # Start the database containers
    docker compose up -d

    # Check if containers started successfully
    if [ $? -eq 0 ]; then
        # Wait for databases to be ready
        log "Waiting for database services to be ready..."
        sleep 10

        # Check if MongoDB is running
        if ! docker ps | grep -q "rpger-mongodb"; then
            log "\e[1;31mMongoDB container failed to start\e[0m"
            check_container_logs "rpger-mongodb"
            exit 1
        fi

        # Check if Redis is running
        if ! docker ps | grep -q "rpger-redis"; then
            log "\e[1;31mRedis container failed to start\e[0m"
            check_container_logs "rpger-redis"
            exit 1
        fi

        log "\e[1;32mDatabase stack started successfully\e[0m"
    else
        log "\e[1;31mError starting database stack\e[0m"

        # Check logs of containers that might have failed
        if docker ps -a | grep -q "rpger-mongodb"; then
            check_container_logs "rpger-mongodb"
        fi

        if docker ps -a | grep -q "rpger-redis"; then
            check_container_logs "rpger-redis"
        fi

        exit 1
    fi
}

# Function to start the application stack
start_app_stack() {
    log "Starting application stack..."
    cd "$APP_STACK_DIR" || exit 1

    # We don't need to clean up containers here as it's already done in start_db_stack
    # which is always called before this function

    # Start the application containers
    log "Building and starting containers (this may take a few minutes)..."
    docker compose up -d --build

    # Check if containers started successfully
    if [ $? -eq 0 ]; then
        log "\e[1;32mApplication stack started successfully\e[0m"
    else
        log "\e[1;31mError starting application stack\e[0m"
        log "Note: If you're seeing TypeScript compatibility errors, the Dockerfile has been updated to use --legacy-peer-deps"
        log "Try running './start-rpger.sh cleanup' and then './start-rpger.sh start' again"
        exit 1
    fi
}

# Function to start the application in development mode (non-containerized)
start_app_dev() {
    log "Starting application in development mode..."

    # Start the database stack first
    start_db_stack

    # Start the application using the app_stack scripts
    log "Starting backend and frontend..."
    "$APP_STACK_DIR/scripts/start-app.sh"
}

# Function to display status of all containers
show_status() {
    log "Container Status:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep rpger
}

# Function to check logs of a specific container
check_container_logs() {
    local container_name=$1
    log "Checking logs for container: $container_name"
    docker logs "$container_name"
}

# Function to stop all stacks
stop_stacks() {
    log "Stopping all stacks..."

    # Stop application stack
    cd "$APP_STACK_DIR" || exit 1
    docker compose down

    # Stop database stack
    cd "$DB_STACK_DIR" || exit 1
    docker compose down

    # Clean up any remaining containers
    cleanup_containers

    # Remove the network
    if docker network inspect rpger-network > /dev/null 2>&1; then
        log "Removing rpger-network..."
        docker network rm rpger-network
    fi

    log "\e[1;32mAll stacks stopped and cleaned up\e[0m"
}

# Main execution
case "$1" in
    start)
        check_docker
        create_network
        start_db_stack
        start_app_stack
        show_status
        log "\e[1;32mRPGer system is now running\e[0m"
        log "MongoDB Admin: http://localhost:8081"
        log "Redis Admin: http://localhost:8082"
        log "Frontend: http://localhost:3001"
        log "Backend API: http://localhost:5000"
        ;;
    dev)
        start_app_dev
        ;;
    stop)
        check_docker
        stop_stacks
        ;;
    cleanup)
        check_docker
        stop_stacks
        ;;
    debug)
        check_docker
        log "Debugging containers..."
        if docker ps -a | grep -q "rpger-mongodb"; then
            check_container_logs "rpger-mongodb"
        else
            log "MongoDB container not found"
        fi

        if docker ps -a | grep -q "rpger-redis"; then
            check_container_logs "rpger-redis"
        else
            log "Redis container not found"
        fi

        if docker ps -a | grep -q "rpger-chroma"; then
            check_container_logs "rpger-chroma"
        else
            log "Chroma container not found"
        fi
        ;;
    restart)
        check_docker
        stop_stacks
        create_network
        start_db_stack
        start_app_stack
        show_status
        log "\e[1;32mRPGer system restarted successfully\e[0m"
        log "MongoDB Admin: http://localhost:8081"
        log "Redis Admin: http://localhost:8082"
        log "Frontend: http://localhost:3001"
        log "Backend API: http://localhost:5000"
        ;;
    status)
        check_docker
        show_status
        ;;
    db-only)
        check_docker
        create_network
        start_db_stack
        show_status
        log "\e[1;32mDatabase stack is now running\e[0m"
        log "MongoDB Admin: http://localhost:8081"
        log "Redis Admin: http://localhost:8082"
        ;;
    app-only)
        check_docker
        create_network
        start_app_stack
        show_status
        log "\e[1;32mApplication stack is now running\e[0m"
        log "Frontend: http://localhost:3001"
        log "Backend API: http://localhost:5000"
        ;;
    *)
        log "Usage: $0 {start|dev|stop|cleanup|debug|restart|status|db-only|app-only}"
        log "  start     - Start both database and application stacks in containers"
        log "  dev       - Start database in containers and application in development mode"
        log "  stop      - Stop all stacks"
        log "  cleanup   - Stop all stacks and clean up containers and networks"
        log "  debug     - Show logs from containers for debugging"
        log "  restart   - Restart all stacks"
        log "  status    - Show status of all containers"
        log "  db-only   - Start only the database stack"
        log "  app-only  - Start only the application stack"
        exit 1
        ;;
esac

exit 0
