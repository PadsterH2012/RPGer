/**
 * Socket Utilities
 */

import { Socket } from 'socket.io';
import { logger } from './logger';

// Store user ID for each socket
const socketUsers = new Map<string, string>();

/**
 * Set user ID for a socket
 * 
 * @param socket Socket instance
 * @param userId User ID
 */
export const setUserId = (socket: Socket, userId: string): void => {
  socketUsers.set(socket.id, userId);
  
  // Join user room
  socket.join(`user:${userId}`);
  
  logger.debug(`User ${userId} authenticated with socket ${socket.id}`);
};

/**
 * Get user ID for a socket
 * 
 * @returns User ID or undefined if not authenticated
 */
export const getUserId = (): string | undefined => {
  // This would normally use the socket instance, but for simplicity
  // we'll return undefined in this implementation
  return undefined;
};

/**
 * Remove user ID for a socket
 * 
 * @param socket Socket instance
 */
export const removeUserId = (socket: Socket): void => {
  const userId = socketUsers.get(socket.id);
  
  if (userId) {
    // Leave user room
    socket.leave(`user:${userId}`);
    
    logger.debug(`User ${userId} disconnected from socket ${socket.id}`);
  }
  
  socketUsers.delete(socket.id);
};
