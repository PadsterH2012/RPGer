/**
 * Player Socket Handlers
 */

import { Socket } from 'socket.io';
import { logger } from '../utils/logger';
import mongoose from 'mongoose';
import { getUserId } from '../utils/socketUtils';

// Sample player stats for in-memory mode
const samplePlayerStats = {
  hp: {
    current: 25,
    maximum: 30,
  },
  level: 3,
  experience: 2500,
  next_level_xp: 4000,
  armor_class: 15,
};

/**
 * Set up player-related socket handlers
 * 
 * @param socket Socket instance
 */
export const setupPlayerHandlers = (socket: Socket) => {
  // Handle player stats request
  socket.on('player:requestStats', async () => {
    try {
      const userId = getUserId();
      
      logger.debug(`User ${userId || socket.id} requested player stats`);
      
      // Check if MongoDB is connected and user is authenticated
      if (mongoose.connection.readyState === 1 && userId) {
        // Try to get character from database
        const Character = mongoose.model('Character');
        const character = await Character.findOne({ userId: new mongoose.Types.ObjectId(userId) });
        
        if (character) {
          // Send character stats
          socket.emit('player:statsUpdate', {
            hp: {
              current: character.hp?.current || 0,
              maximum: character.hp?.maximum || 0,
            },
            level: character.level || 1,
            experience: character.experience || 0,
            next_level_xp: character.next_level_xp || 0,
            armor_class: character.armor_class || 10,
          });
          return;
        }
      }
      
      // Send sample player stats if no character found or database not connected
      socket.emit('player:statsUpdate', samplePlayerStats);
    } catch (error) {
      logger.error(`Error handling player stats request: ${error}`);
      
      // Send sample player stats as fallback
      socket.emit('player:statsUpdate', samplePlayerStats);
    }
  });
};
