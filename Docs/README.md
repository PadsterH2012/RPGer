# RPGer Dashboard

A modern React-based dashboard for RPG game management with real-time updates, customizable layouts, and persistent user configurations.

## Features

- **Customizable Dashboard**: Drag, resize, and snap UI components
- **Real-time Updates**: Live data synchronization via Socket.IO
- **Persistent Layouts**: Save and load dashboard configurations
- **Visual Customization**: Themes, typography controls, and component styling
- **Responsive Design**: Works on desktop and mobile devices

## Technology Stack

### Frontend
- React
- TypeScript
- React Grid Layout
- Socket.IO Client
- Styled Components

### Backend
- Node.js
- Express
- Socket.IO
- MongoDB (persistent storage)
- Redis (caching and real-time data)
- Vector Database (advanced queries)

## Getting Started

### Prerequisites
- Node.js (v18+)
- npm or yarn

#### Optional Dependencies (for database mode)
- Docker and Docker Compose (for MongoDB and Redis)
- MongoDB (for persistent storage)
- Redis (for caching and real-time data)

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/RPGer.git
cd RPGer
```

2. Install dependencies
```bash
# Install root dependencies
npm install

# Install client dependencies
cd client
npm install

# Install server dependencies
cd ../server
npm install
```

3. Set up environment variables
```bash
# Create .env file in the server directory
cp server/.env.example server/.env
# Edit the .env file with your configuration
```

4. Choose your mode:

#### In-Memory Mode (No Database Required)
```bash
# Use the provided script to start in in-memory mode
./start-in-memory.sh

# Or manually:
# - Make sure server/.env has MONGODB_ENABLED=false and REDIS_ENABLED=false
# - Run: npm run dev
```

#### Database Mode (MongoDB and Redis Required)
```bash
# Use the provided script to start with database mode
./start-with-db.sh

# Or manually:
# - Start the databases: docker compose up -d
# - Make sure server/.env has MONGODB_ENABLED=true and REDIS_ENABLED=true
# - Seed the database: cd server && npm run seed && cd ..
# - Run: npm run dev
```

## Development

### Client
The client is a React application created with Create React App and TypeScript.

```bash
# Start client development server
cd client
npm start
```

### Server
The server is a Node.js/Express application with Socket.IO for real-time communication.

```bash
# Start server in development mode
cd server
npm run dev
```

## Project Structure

```
RPGer/
├── client/                 # React frontend
│   ├── public/             # Static assets
│   └── src/                # Source code
├── server/                 # Node.js/Express backend
│   └── src/                # Source code
└── shared/                 # Shared code between client and server
```

## Running Modes

### In-Memory Mode
The application can run in in-memory mode, which doesn't require any external databases. This is useful for development and testing. In this mode:

- All data is stored in memory and will be lost when the server restarts
- Sample data is provided for testing
- No MongoDB or Redis installation is required
- Perfect for quick setup and development

To enable in-memory mode, set the following in your `.env` file:
```
MONGODB_ENABLED=false
REDIS_ENABLED=false
```

### Database Mode
For persistent storage and better performance, the application can run in database mode. This requires MongoDB and Redis. In this mode:

- Data is stored in MongoDB and persists between server restarts
- Redis is used for caching and real-time data
- Better performance and scalability
- Required for production use

To enable database mode, set the following in your `.env` file:
```
MONGODB_ENABLED=true
REDIS_ENABLED=true
MONGODB_URI=mongodb://localhost:27017/rpger
REDIS_URL=redis://localhost:6379
```

## Docker Compose Services

- **MongoDB**: Main database (port 27017)
- **Redis**: Caching and real-time data (port 6379)
- **MongoDB Express**: Web-based MongoDB admin interface (port 8081)
- **Redis Commander**: Web-based Redis admin interface (port 8082)

## Admin Interfaces

- MongoDB Express: http://localhost:8081
  - Username: admin
  - Password: password
- Redis Commander: http://localhost:8082

## API Endpoints

- `GET /api/health`: Health check endpoint
- `GET /api/db-status`: Database status endpoint
- `GET /api/characters`: Get all characters
- `GET /api/campaigns`: Get all campaigns
- `GET /api/notes`: Get all notes
- `GET /api/dashboards`: Get all dashboards
- `GET /api/widgets`: Get all widgets

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Original Flask application that inspired this project
- React Grid Layout for the dashboard functionality
- Socket.IO for real-time capabilities
- MongoDB for persistent storage
- Redis for caching and real-time data
- Docker and Docker Compose for containerization
