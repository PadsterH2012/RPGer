import { Server, Socket } from 'socket.io';
import { logger } from '../utils/logger';
import { setupWidgetHandlers } from './widgetHandlers';
import { setupPlayerHandlers } from './playerHandlers';
import { dashboardService } from '../services/DashboardService';
import { getRedisClient } from '../config/redis';
import { Character } from '../models/Character';
import { Note } from '../models/Note';
import mongoose from 'mongoose';
import { setUserId, removeUserId } from '../utils/socketUtils';

// Store connected clients
const connectedClients = new Map<string, Socket>();

// Store user sessions
export const userSessions = new Map<string, string>();

// Default player stats (used when no character is loaded)
const defaultPlayerStats = {
  hp: {
    current: 25,
    maximum: 30,
  },
  level: 3,
  experience: 2500,
  next_level_xp: 4000,
  armor_class: 15,
};

// Default character data (used when no character is loaded)
const defaultCharacterData = {
  name: 'Thalion',
  race: 'Human',
  class: 'Fighter',
  level: 3,
  abilities: {
    strength: 16,
    dexterity: 14,
    constitution: 15,
    intelligence: 12,
    wisdom: 10,
    charisma: 13
  },
  equipment: [
    { name: 'Longsword', type: 'Weapon', details: '1d8 slashing' },
    { name: 'Chain Mail', type: 'Armor', details: 'AC 16' },
    { name: 'Shield', type: 'Armor', details: '+2 AC' },
    { name: 'Backpack', type: 'Gear', details: 'Contains adventuring gear' }
  ],
  spells: [],
  skills: {
    'Athletics': 5,
    'Intimidation': 3,
    'Perception': 2,
    'Survival': 2
  }
};

export const setupSocketHandlers = (io: Server) => {
  io.on('connection', (socket: Socket) => {
    const clientId = socket.id;
    logger.info(`Client connected: ${clientId}`);
    connectedClients.set(clientId, socket);

    // Send connected clients count to all clients
    io.emit('clients:count', connectedClients.size);

    // Set up widget handlers
    setupWidgetHandlers(io, socket);

    // Set up player handlers
    setupPlayerHandlers(socket);

    // Handle user authentication
    socket.on('auth:login', async (data: { userId: string }) => {
      try {
        // Store user ID in session
        userSessions.set(clientId, data.userId);
        logger.info(`User ${data.userId} authenticated for client: ${clientId}`);

        // Set user ID for socket
        setUserId(socket, data.userId);

        // Send success response
        socket.emit('auth:loginSuccess', { userId: data.userId });
      } catch (error) {
        logger.error(`Error authenticating user: ${error}`);
        socket.emit('auth:loginError', { error: 'Authentication failed' });
      }
    });

    // Handle dashboard layout changes
    socket.on('dashboard:layoutChange', async (layouts: any) => {
      try {
        const userId = userSessions.get(clientId);

        if (!userId) {
          // For development/testing, create a default user ID if not authenticated
          // In production, you would want to require authentication
          const defaultUserId = 'default-user-id';
          userSessions.set(clientId, defaultUserId);
          logger.info(`Using default user ID for unauthenticated client: ${defaultUserId}`);

          // Get default dashboard or create one if it doesn't exist
          let dashboard = await dashboardService.getDefaultDashboard(defaultUserId);

          if (!dashboard) {
            dashboard = await dashboardService.createDashboard({
              userId: new mongoose.Types.ObjectId(defaultUserId),
              name: 'Default Dashboard',
              layouts,
              isDefault: true,
            });
          } else {
            // Update existing dashboard
            dashboard = await dashboardService.updateDashboard(
              dashboard._id.toString(),
              defaultUserId,
              { layouts }
            );
          }

          // Store in Redis for quick access
          const redisClient = getRedisClient();
          if (redisClient) {
            await redisClient.set(
              `dashboard:layouts:${defaultUserId}`,
              JSON.stringify(layouts),
              { EX: 3600 } // Expire after 1 hour
            );
          }

          return;
        }

        // Get default dashboard or create one if it doesn't exist
        let dashboard = await dashboardService.getDefaultDashboard(userId);

        if (!dashboard) {
          dashboard = await dashboardService.createDashboard({
            userId: new mongoose.Types.ObjectId(userId),
            name: 'Default Dashboard',
            layouts,
            isDefault: true,
          });
        } else {
          // Update existing dashboard
          dashboard = await dashboardService.updateDashboard(
            dashboard._id.toString(),
            userId,
            { layouts }
          );
        }

        // Broadcast to other clients of the same user
        socket.to(`user:${userId}`).emit('dashboard:layoutUpdate', layouts);

        // Store in Redis for quick access
        const redisClient = getRedisClient();
        if (redisClient) {
          await redisClient.set(
            `dashboard:layouts:${userId}`,
            JSON.stringify(layouts),
            { EX: 3600 } // Expire after 1 hour
          );
        }
      } catch (error) {
        logger.error(`Error handling dashboard layout change: ${error}`);
        socket.emit('error', { message: 'Failed to save dashboard layout' });
      }
    });

    // Handle dashboard layout save
    socket.on('dashboard:saveLayout', async (data: { name: string, layouts: any }) => {
      try {
        const userId = userSessions.get(clientId);

        if (!userId) {
          socket.emit('error', { message: 'Not authenticated' });
          return;
        }

        // Create a new dashboard
        const dashboard = await dashboardService.createDashboard({
          userId: new mongoose.Types.ObjectId(userId),
          name: data.name,
          layouts: data.layouts,
          isDefault: false,
        });

        if (dashboard) {
          logger.info(`Dashboard saved for user: ${userId}`);
          socket.emit('dashboard:saveSuccess', { dashboardId: dashboard._id });
        } else {
          socket.emit('error', { message: 'Failed to save dashboard' });
        }
      } catch (error) {
        logger.error(`Error saving dashboard: ${error}`);
        socket.emit('error', { message: 'Failed to save dashboard' });
      }
    });

    // Handle dashboard request
    socket.on('dashboard:request', async () => {
      try {
        const userId = userSessions.get(clientId);

        if (!userId) {
          // For development/testing, create a default user ID if not authenticated
          const defaultUserId = 'default-user-id';
          userSessions.set(clientId, defaultUserId);
          logger.info(`Using default user ID for unauthenticated client: ${defaultUserId}`);

          // Try to get from Redis first
          const redisClient = getRedisClient();
          if (redisClient) {
            const cachedLayouts = await redisClient.get(`dashboard:layouts:${defaultUserId}`);
            if (cachedLayouts) {
              socket.emit('dashboard:update', JSON.parse(cachedLayouts));
              return;
            }
          }

          // Get from database
          const dashboard = await dashboardService.getDefaultDashboard(defaultUserId);

          if (dashboard) {
            socket.emit('dashboard:update', dashboard.layouts);

            // Cache in Redis
            if (redisClient) {
              await redisClient.set(
                `dashboard:layouts:${defaultUserId}`,
                JSON.stringify(dashboard.layouts),
                { EX: 3600 } // Expire after 1 hour
              );
            }
          } else {
            // No dashboard found, send default layouts
            socket.emit('dashboard:update', {});
          }

          return;
        }

        // Try to get from Redis first
        const redisClient = getRedisClient();
        if (redisClient) {
          const cachedLayouts = await redisClient.get(`dashboard:layouts:${userId}`);
          if (cachedLayouts) {
            socket.emit('dashboard:update', JSON.parse(cachedLayouts));
            return;
          }
        }

        // Get from database
        const dashboard = await dashboardService.getDefaultDashboard(userId);

        if (dashboard) {
          socket.emit('dashboard:update', dashboard.layouts);

          // Cache in Redis
          if (redisClient) {
            await redisClient.set(
              `dashboard:layouts:${userId}`,
              JSON.stringify(dashboard.layouts),
              { EX: 3600 } // Expire after 1 hour
            );
          }
        } else {
          // No dashboard found, send empty layout
          socket.emit('dashboard:update', {});
        }
      } catch (error) {
        logger.error(`Error handling dashboard request: ${error}`);
        socket.emit('error', { message: 'Failed to load dashboard' });
      }
    });

    // Player stats request is now handled in playerHandlers.ts

    // Handle notes request
    socket.on('notes:request', async () => {
      try {
        const userId = userSessions.get(clientId);

        if (!userId) {
          socket.emit('notes:update', '');
          return;
        }

        // Get notes from database
        const notes = await Note.find({
          userId: new mongoose.Types.ObjectId(userId),
        }).sort({ updatedAt: -1 }).limit(10);

        if (notes.length > 0) {
          // Send notes to client
          socket.emit('notes:update', notes.map(note => ({
            id: note._id,
            title: note.title,
            content: note.content,
            category: note.category,
            tags: note.tags,
            pinned: note.pinned,
            updatedAt: note.updatedAt,
          })));
        } else {
          // No notes found
          socket.emit('notes:update', []);
        }
      } catch (error) {
        logger.error(`Error handling notes request: ${error}`);
        socket.emit('notes:update', []);
      }
    });

    // Handle notes save
    socket.on('notes:save', async (data: { title: string, content: string, category?: string, tags?: string[] }) => {
      try {
        const userId = userSessions.get(clientId);

        if (!userId) {
          socket.emit('error', { message: 'Not authenticated' });
          return;
        }

        // Create note
        const note = await Note.create({
          userId: new mongoose.Types.ObjectId(userId),
          title: data.title,
          content: data.content,
          category: data.category,
          tags: data.tags,
          pinned: false,
        });

        if (note) {
          logger.info(`Note saved for user: ${userId}`);
          socket.emit('notes:saveSuccess', { noteId: note._id });

          // Broadcast to other clients of the same user
          socket.to(`user:${userId}`).emit('notes:new', {
            id: note._id,
            title: note.title,
            content: note.content,
            category: note.category,
            tags: note.tags,
            pinned: note.pinned,
            updatedAt: note.updatedAt,
          });
        } else {
          socket.emit('error', { message: 'Failed to save note' });
        }
      } catch (error) {
        logger.error(`Error saving note: ${error}`);
        socket.emit('error', { message: 'Failed to save note' });
      }
    });

    // Handle character request
    socket.on('character:request', async () => {
      try {
        const userId = userSessions.get(clientId);

        if (!userId) {
          socket.emit('character:update', defaultCharacterData);
          return;
        }

        // Get active character from Redis
        const redisClient = getRedisClient();
        let characterId: string | null = null;

        if (redisClient) {
          characterId = await redisClient.get(`user:${userId}:activeCharacter`);
        }

        if (characterId) {
          // Get character from database
          const character = await Character.findById(characterId);

          if (character) {
            socket.emit('character:update', character);
            return;
          }
        }

        // No character found, send default character
        socket.emit('character:update', defaultCharacterData);
      } catch (error) {
        logger.error(`Error handling character request: ${error}`);
        socket.emit('character:update', defaultCharacterData);
      }
    });

    // Handle disconnection
    socket.on('disconnect', () => {
      logger.info(`Client disconnected: ${clientId}`);

      // Remove from user sessions
      userSessions.delete(clientId);

      // Remove user ID for socket
      removeUserId(socket);

      // Remove from connected clients
      connectedClients.delete(clientId);

      // Send connected clients count to all clients
      io.emit('clients:count', connectedClients.size);
    });
  });
};
