/**
 * Status API routes
 * Provides endpoints for checking the status of various services
 */

import express from 'express';
import mongoose from 'mongoose';
import { createClient } from 'redis';
import { logger } from '../../utils/logger';

const router = express.Router();

/**
 * @route   GET /api/status
 * @desc    Get status of all services
 * @access  Public
 */
router.get('/', async (req, res) => {
  try {
    const status = {
      mongodb: {
        connected: mongoose.connection.readyState === 1,
        collections: 0,
        databaseName: '',
        databaseSize: '0 MB'
      },
      redis: {
        connected: false,
        usedMemory: '0 MB',
        totalKeys: 0,
        uptime: 0
      },
      socketio: {
        connected: req.app.get('socketio') !== undefined,
        clients: 0
      }
    };

    // Get MongoDB stats if connected
    if (status.mongodb.connected) {
      try {
        // Get list of collections
        const collections = await mongoose.connection.db.listCollections().toArray();
        status.mongodb.collections = collections.length;
        status.mongodb.databaseName = mongoose.connection.db.databaseName;

        // Get database stats
        const dbStats = await mongoose.connection.db.stats();
        status.mongodb.databaseSize = `${Math.round(dbStats.storageSize / (1024 * 1024) * 100) / 100} MB`;
      } catch (error) {
        logger.error(`Error getting MongoDB stats: ${error}`);
      }
    }

    // Get Redis stats if enabled
    if (process.env.REDIS_ENABLED !== 'false' && process.env.REDIS_URL) {
      try {
        const redisClient = createClient({
          url: process.env.REDIS_URL
        });

        // Connect to Redis
        await redisClient.connect();
        status.redis.connected = true;

        // Get Redis info
        const info = await redisClient.info();
        
        // Parse Redis info
        const usedMemory = info.match(/used_memory_human:(.*)/)?.[1]?.trim() || '0 MB';
        const uptime = info.match(/uptime_in_seconds:(.*)/)?.[1]?.trim() || '0';
        
        status.redis.usedMemory = usedMemory;
        status.redis.uptime = parseInt(uptime);
        
        // Get total keys
        const keys = await redisClient.keys('*');
        status.redis.totalKeys = keys.length;
        
        // Disconnect from Redis
        await redisClient.disconnect();
      } catch (error) {
        logger.error(`Error getting Redis stats: ${error}`);
        status.redis.connected = false;
      }
    }

    // Get Socket.IO stats if available
    if (status.socketio.connected) {
      const io = req.app.get('socketio');
      if (io) {
        status.socketio.clients = io.engine.clientsCount || 0;
      }
    }

    res.json(status);
  } catch (error) {
    logger.error(`Error in status route: ${error}`);
    res.status(500).json({ error: 'Server error' });
  }
});

export default router;
