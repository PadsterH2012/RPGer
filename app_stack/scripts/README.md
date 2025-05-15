# RPGer Application Scripts

This directory contains scripts for managing the RPGer application stack.

## Available Scripts

### `start-app.sh`

This is the main script that starts both the backend and frontend components. It:
- Creates necessary environment files
- Starts the backend in the background
- Starts the frontend
- Handles proper shutdown of all components

Usage:
```bash
./start-app.sh
```

### `start-backend.sh`

This script starts only the Flask-SocketIO backend. It:
- Sets up a Python virtual environment if needed
- Installs required dependencies
- Starts the Flask-SocketIO server

Usage:
```bash
./start-backend.sh
```

### `start-frontend.sh`

This script starts only the React frontend. It:
- Installs Node.js dependencies if needed
- Starts the React development server

Usage:
```bash
./start-frontend.sh
```

### `debug.sh`

This script shows the logs from the backend for debugging purposes.

Usage:
```bash
./debug.sh
```

## Integration with Docker

When using the Docker Compose setup, these scripts are not needed as the containers will handle starting the services. However, they can still be useful for local development without containers.
