/**
 * Redis configuration and connection setup
 */

import { createClient, RedisClientType } from 'redis';
import { logger } from '../utils/logger';

// Redis client instance
let redisClient: RedisClientType | null = null;

/**
 * Connect to Redis
 *
 * @param useInMemoryFallback Whether to use an in-memory fallback if Redis is not available
 * @returns Redis client or null if connection failed and no fallback is used
 */
export const connectToRedis = async (useInMemoryFallback: boolean = true): Promise<RedisClientType | null> => {
  try {
    // Skip Redis connection if REDIS_ENABLED is set to 'false'
    if (process.env.REDIS_ENABLED === 'false') {
      logger.info('Redis is disabled by configuration, using in-memory fallback');
      return null;
    }

    const redisUrl = process.env.REDIS_URL || 'redis://localhost:6379';

    // Create Redis client
    redisClient = createClient({
      url: redisUrl,
    });

    // Set up event handlers
    redisClient.on('error', (err) => {
      logger.error(`Redis error: ${err}`);
    });

    redisClient.on('connect', () => {
      logger.info('Connected to Redis');
    });

    redisClient.on('reconnecting', () => {
      logger.warn('Reconnecting to Redis');
    });

    redisClient.on('end', () => {
      logger.info('Redis connection closed');
    });

    // Connect to Redis
    await redisClient.connect();

    return redisClient;
  } catch (error) {
    logger.error(`Error connecting to Redis: ${error}`);

    if (useInMemoryFallback) {
      logger.info('Using in-memory fallback for Redis');
    }

    return null;
  }
};

/**
 * Get Redis client instance
 */
export const getRedisClient = (): RedisClientType | null => {
  return redisClient;
};

/**
 * Disconnect from Redis
 */
export const disconnectFromRedis = async (): Promise<void> => {
  if (redisClient) {
    try {
      await redisClient.quit();
      redisClient = null;
      logger.info('Disconnected from Redis');
    } catch (error) {
      logger.error(`Error disconnecting from Redis: ${error}`);
    }
  }
};
