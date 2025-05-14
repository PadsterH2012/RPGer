import express from 'express';
import http from 'http';
import cors from 'cors';
import helmet from 'helmet';
import { Server } from 'socket.io';
import dotenv from 'dotenv';
import { setupSocketHandlers } from './socket';
import { logger } from './utils/logger';
import { connectToMongoDB } from './config/database';
import { connectToRedis } from './config/redis';
import { vectorService } from './services/VectorService';
import apiRoutes from './routes/api';

// Load environment variables
dotenv.config();

// Create Express app
const app = express();
const server = http.createServer(app);

// Set up middleware
app.use(cors());
app.use(helmet());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Set up Socket.IO
const io = new Server(server, {
  cors: {
    origin: process.env.CLIENT_URL || 'http://localhost:3000',
    methods: ['GET', 'POST'],
    credentials: true
  }
});

// Set up socket handlers
setupSocketHandlers(io);

// API routes
app.use('/api', apiRoutes);

// Error handling middleware
app.use((err: Error, req: express.Request, res: express.Response, next: express.NextFunction) => {
  logger.error(`Error: ${err.message}`);
  res.status(500).json({ error: 'Internal Server Error' });
});

// Connect to databases
const initDatabases = async () => {
  try {
    let mongoConnected = false;
    let redisConnected = false;

    // Connect to MongoDB if enabled
    if (process.env.MONGODB_ENABLED !== 'false') {
      if (process.env.MONGODB_URI) {
        mongoConnected = await connectToMongoDB();
      } else {
        logger.warn('MongoDB URI not provided, skipping connection');
      }
    } else {
      logger.info('MongoDB is disabled by configuration, using in-memory mode');
    }

    // Connect to Redis if enabled
    if (process.env.REDIS_ENABLED !== 'false') {
      if (process.env.REDIS_URL) {
        const redisClient = await connectToRedis();
        redisConnected = redisClient !== null;

        // Load vector collections from Redis if connected
        if (redisConnected) {
          await vectorService.loadFromRedis();
        }
      } else {
        logger.warn('Redis URL not provided, skipping connection');
      }
    } else {
      logger.info('Redis is disabled by configuration, using in-memory mode');
    }

    // Log database status
    logger.info(`Database status: MongoDB ${mongoConnected ? 'connected' : 'disconnected'}, Redis ${redisConnected ? 'connected' : 'disconnected'}`);

    if (!mongoConnected && !redisConnected) {
      logger.info('Running in full in-memory mode');
    }
  } catch (error) {
    logger.error(`Error initializing databases: ${error}`);
    logger.info('Falling back to in-memory mode');
  }
};

// Start server
const PORT = process.env.PORT || 5000;
server.listen(PORT, async () => {
  logger.info(`Server running on port ${PORT}`);

  // Initialize databases
  await initDatabases();
});
