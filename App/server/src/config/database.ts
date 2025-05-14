/**
 * Database configuration and connection setup
 */

import mongoose from 'mongoose';
import { logger } from '../utils/logger';

/**
 * Connect to MongoDB
 *
 * @param exitOnError Whether to exit the process on connection error
 * @returns Boolean indicating whether the connection was successful
 */
export const connectToMongoDB = async (exitOnError: boolean = false): Promise<boolean> => {
  try {
    const mongoURI = process.env.MONGODB_URI || 'mongodb://localhost:27017/rpger';

    // Set mongoose options
    mongoose.set('strictQuery', false);

    // Connect to MongoDB
    await mongoose.connect(mongoURI);

    logger.info('Connected to MongoDB');

    // Handle connection events
    mongoose.connection.on('error', (err) => {
      logger.error(`MongoDB connection error: ${err}`);
    });

    mongoose.connection.on('disconnected', () => {
      logger.warn('MongoDB disconnected');
    });

    // Handle process termination
    process.on('SIGINT', async () => {
      await mongoose.connection.close();
      logger.info('MongoDB connection closed due to app termination');
      process.exit(0);
    });

    return true;
  } catch (error) {
    logger.error(`Error connecting to MongoDB: ${error}`);

    if (exitOnError) {
      process.exit(1);
    }

    return false;
  }
};

/**
 * Disconnect from MongoDB
 */
export const disconnectFromMongoDB = async (): Promise<void> => {
  try {
    await mongoose.connection.close();
    logger.info('Disconnected from MongoDB');
  } catch (error) {
    logger.error(`Error disconnecting from MongoDB: ${error}`);
  }
};
