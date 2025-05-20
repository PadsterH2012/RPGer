# RPGer

A modern React-based dashboard for RPG game management with AI-powered Dungeon Master capabilities.

## Project Structure

- `App/client/`: React frontend application
- `App/server/`: Node.js/Express backend server
- `App/shared/`: Shared code between client and server
- `App/backend/`: Python-based backend (alternative to Node.js server)
- `App/prompts/`: Prompt files for AI agents (DMA, CMA, CRA, etc.)

## Prerequisites

- Node.js (v18+)
- npm or yarn
- Docker and Docker Compose (for containerized database and Redis)
- OpenRouter API key (for AI capabilities)

## Getting Started

### Option 1: Run with Containerized Backend (Recommended)

This option uses Docker containers for MongoDB and Redis while running the main application normally.

1. Make sure Docker and Docker Compose are installed and running
2. Run the start script:

```bash
./start-with-containers.sh
```

This will:
- Start MongoDB and Redis in Docker containers
- Configure the application to use these containers
- Start the application in development mode

### Option 2: Run in In-Memory Mode (No Database)

If you don't want to use a database, you can run the application in in-memory mode:

```bash
./App/start-in-memory.sh
```

### Option 3: Run with Local Database

If you have MongoDB and Redis installed locally, you can run:

```bash
./App/start-with-db.sh
```

## Testing the Setup

To verify that the application can connect to the containerized MongoDB and Redis:

```bash
./test-rpger.sh
```

## Stopping the Containers

When you're done working with the application, you can stop the containers:

```bash
cd App
docker compose down
```

## Development

### Client

The client is a React application created with Create React App and TypeScript.

```bash
# Start client development server
cd App/client
npm start
```

### Server

The server is a Node.js/Express application with Socket.IO for real-time communication.

```bash
# Start server in development mode
cd App/server
npm run dev
```

## Available Scripts

### Node.js Scripts
- `npm run dev`: Start both client and server in development mode
- `npm run client`: Start only the client
- `npm run server`: Start only the server
- `npm run build`: Build both client and server
- `npm run test`: Run tests for both client and server
- `npm run lint`: Run linting for both client and server

### Bash Scripts
- `scripts/start-rpg.sh`: Start all components of the RPG web app (MongoDB, Redis, Flask backend, React frontend)
- `scripts/backup_db.sh`: Create backups of MongoDB and Redis databases
- `scripts/restore_db.sh`: Restore MongoDB and Redis databases from backups
- `scripts/setup_backup_cron.sh`: Set up automated database backups using cron
- `scripts/check_mongodb.sh`: Check if MongoDB is running and start it if needed
- `scripts/test_db_stack.sh`: Test database connections (MongoDB, Redis, Chroma)
- `scripts/test_api.sh`: Test API endpoints
- `scripts/test_all.sh`: Run all tests (database and API)

## Accessing Admin Interfaces

When running with containers, you can access:

- MongoDB admin interface: http://localhost:8081
- Redis admin interface: http://localhost:8082

## Environment Configuration

RPGer uses environment variables for configuration. You can set these in a `.env` file in the appropriate directory.

### Backend Environment Variables

Create a `.env` file in the `app_stack/backend/` directory with the following content:

```
# Server Configuration
PORT=5002
DEBUG=true
SECRET_KEY=change_this_in_production

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/rpger

# Redis Configuration
REDIS_URL=redis://localhost:6379

# Chroma Configuration
CHROMA_HOST=localhost
CHROMA_PORT=8000

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001,http://127.0.0.1:3000

# OpenRouter API Key
OPENROUTER_API_KEY=your_api_key_here
```

Replace `your_api_key_here` with your actual OpenRouter API key.

### Database Configuration

RPGer supports multiple database configurations:

1. **Local MongoDB and Redis**: Set the appropriate connection strings in your `.env` file
2. **Containerized Databases**: The `start-rpg.sh` script will automatically configure and start MongoDB and Redis containers
3. **Custom Database Servers**: Set the `MONGODB_URI` and `REDIS_URL` environment variables to point to your custom servers

### Health Monitoring

RPGer includes health check endpoints to monitor the status of the application and its dependencies:

- `/api/health`: Returns the health status of the application and all connected services
- `/api/status`: Returns detailed status information about MongoDB, Redis, and Chroma
- `/api/socketio-status`: Returns the status of the Socket.IO server

## OpenRouter Integration

RPGer uses OpenRouter to connect to various AI models for the Dungeon Master Agent (DMA) and other AI agents. To use this feature:

1. Sign up for an account at [OpenRouter](https://openrouter.ai/)
2. Get your API key from the OpenRouter dashboard
3. Add your API key to the `.env` file as shown in the Environment Configuration section

### Available Models

RPGer uses a tiered approach to AI models:

- **Tier 1** (Default): `mistralai/mistral-7b-instruct` - Fast and cost-effective
- **Tier 2**: `anthropic/claude-instant-1.2` - Better quality, slightly higher cost
- **Tier 3**: `anthropic/claude-3-haiku-20240307` - Highest quality, highest cost

For more details on the OpenRouter integration, see [OpenRouter Integration](Docs/Backend/Integration/OpenRouterIntegration.md).

## Agent Prompts

RPGer uses a system of specialized AI agents, each with its own prompt file:

- **DMA (Dungeon Master Agent)**: Accepts player actions and provides basic responses
- **CMA (Character Management Agent)**: Handles character stats, inventory, and abilities
- **CRA (Combat Resolution Agent)**: Resolves combat actions and calculates damage
- And more...

All agent prompts are stored in the `App/prompts/` directory. Each prompt follows a naming convention:
```
{agent_code}_{tier}_prompt.txt
```

For example:
- `dma_tier1_prompt.txt` - Tier 1 prompt for the Dungeon Master Agent
- `cma_tier2_prompt.txt` - Tier 2 prompt for the Character Management Agent

For more details on agent prompts, see the [Prompt README](App/prompts/README.md).

## Database Management

### Backup and Restore

RPGer includes scripts for backing up and restoring MongoDB and Redis databases:

#### Creating a Backup

To create a backup of your databases:

```bash
./scripts/backup_db.sh
```

This will create compressed backup files in the `backups/` directory with timestamps in the filenames.

#### Restoring from a Backup

To restore your databases from a backup:

```bash
./scripts/restore_db.sh
```

This script will list available backups and prompt you to select which ones to restore.

#### Automated Backups

To set up automated backups using cron:

```bash
./scripts/setup_backup_cron.sh
```

This script will guide you through setting up a cron job to run backups automatically at your preferred schedule.

### Database Initialization

To initialize the database with required collections and indexes:

```bash
cd app_stack/backend
python init_db.py
```

To include sample data:

```bash
python init_db.py --with-test-data
```

## Testing

RPGer includes comprehensive testing scripts to verify that all components are working correctly.

### Testing Database Connections

To test database connections (MongoDB, Redis, Chroma):

```bash
./scripts/test_db_stack.sh
```

This script will:
- Test direct connections to MongoDB, Redis, and Chroma
- Test API endpoints that interact with the databases
- Provide detailed error messages if any connections fail

### Testing API Endpoints

To test API endpoints:

```bash
./scripts/test_api.sh
```

This script will:
- Test all documented API endpoints
- Verify that endpoints return the expected responses
- Test Socket.IO connection
- Provide detailed error messages if any endpoints fail

### Running All Tests

To run all tests (database and API):

```bash
./scripts/test_all.sh
```

### Test Options

All test scripts support the following options:

- `--host HOST`: Specify the host address (default: localhost)
- `--port PORT`: Specify the port (default: 5002)
- `--verbose`: Show detailed information about each test

Example:

```bash
./scripts/test_all.sh --host 192.168.1.100 --port 5002 --verbose
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
