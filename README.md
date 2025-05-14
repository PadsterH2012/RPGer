# RPGer

A modern React-based dashboard for RPG game management with AI-powered Dungeon Master capabilities.

## Project Structure

- `client/`: React frontend application
- `server/`: Node.js/Express backend server
- `shared/`: Shared code between client and server
- `backend/`: Python-based backend (alternative to Node.js server)
- `prompts/`: Prompt files for AI agents

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

- `npm run dev`: Start both client and server in development mode
- `npm run client`: Start only the client
- `npm run server`: Start only the server
- `npm run build`: Build both client and server
- `npm run test`: Run tests for both client and server
- `npm run lint`: Run linting for both client and server

## Accessing Admin Interfaces

When running with containers, you can access:

- MongoDB admin interface: http://localhost:8081
- Redis admin interface: http://localhost:8082

## OpenRouter Integration

RPGer uses OpenRouter to connect to various AI models for the Dungeon Master Agent (DMA) and other AI agents. To use this feature:

1. Sign up for an account at [OpenRouter](https://openrouter.ai/)
2. Get your API key from the OpenRouter dashboard
3. Create a `.env` file in the `App/backend/` directory with the following content:
   ```
   OPENROUTER_API_KEY=your_api_key_here
   ```
4. Replace `your_api_key_here` with your actual OpenRouter API key

### Available Models

RPGer uses a tiered approach to AI models:

- **Tier 1** (Default): `mistralai/mistral-7b-instruct` - Fast and cost-effective
- **Tier 2**: `anthropic/claude-instant-1.2` - Better quality, slightly higher cost
- **Tier 3**: `anthropic/claude-3-haiku-20240307` - Highest quality, highest cost

For more details on the OpenRouter integration, see [OpenRouter Integration](Docs/Backend/Integration/OpenRouterIntegration.md).

## License

This project is licensed under the MIT License - see the LICENSE file for details.
