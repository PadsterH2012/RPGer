/**
 * Widget Socket.IO Event Handlers
 */

import { Server, Socket } from 'socket.io';
import { logger } from '../utils/logger';
import { dashboardService } from '../services/DashboardService';
import { getRedisClient } from '../config/redis';
import mongoose from 'mongoose';
import { userSessions } from './index';

/**
 * Set up widget-related Socket.IO event handlers
 *
 * @param io Socket.IO server instance
 * @param socket Socket connection
 */
export const setupWidgetHandlers = (io: Server, socket: Socket): void => {
  // Get user ID from session or use default for development
  const getUserId = (): string => {
    const userId = userSessions.get(socket.id);
    if (!userId) {
      // For development/testing, create a default user ID if not authenticated
      const defaultUserId = 'default-user-id';
      userSessions.set(socket.id, defaultUserId);
      logger.info(`Using default user ID for unauthenticated client: ${defaultUserId}`);
      return defaultUserId;
    }
    return userId;
  };

  // Handle widget sync
  socket.on('widgets:sync', async (data: { activeWidgets: string[]; configs: Record<string, any> }) => {
    try {
      const userId = getUserId();

      logger.debug(`User ${userId} synced widget state: ${JSON.stringify(data)}`);

      // Join rooms for each active widget
      data.activeWidgets.forEach(widgetId => {
        socket.join(`widget:${widgetId}`);
      });

      // Save widgets to database
      for (const widgetId of data.activeWidgets) {
        const config = data.configs[widgetId] || {};

        await dashboardService.saveWidget({
          userId: new mongoose.Types.ObjectId(userId),
          widgetId,
          name: widgetId, // Use widget ID as name for now
          type: widgetId.split('-')[0], // Extract type from ID
          config,
          active: true,
        });
      }

      // Cache in Redis for quick access
      const redisClient = getRedisClient();
      if (redisClient) {
        await redisClient.set(
          `user:${userId}:widgets`,
          JSON.stringify({
            activeWidgets: data.activeWidgets,
            configs: data.configs,
          }),
          { EX: 3600 } // Expire after 1 hour
        );
      }
    } catch (error) {
      logger.error(`Error handling widget sync: ${error}`);
    }
  });

  // Handle widget add
  socket.on('widgets:add', async (data: { widgetId: string; config?: any }) => {
    try {
      const userId = getUserId();

      logger.debug(`User ${userId} added widget: ${data.widgetId}`);

      // Save widget to database
      await dashboardService.saveWidget({
        userId: new mongoose.Types.ObjectId(userId),
        widgetId: data.widgetId,
        name: data.widgetId, // Use widget ID as name for now
        type: data.widgetId.split('-')[0], // Extract type from ID
        config: data.config || {},
        active: true,
      });

      // Join room for the widget
      socket.join(`widget:${data.widgetId}`);

      // Update Redis cache
      const redisClient = getRedisClient();
      if (redisClient) {
        const cachedWidgets = await redisClient.get(`user:${userId}:widgets`);

        if (cachedWidgets) {
          const widgets = JSON.parse(cachedWidgets);

          // Add widget to active widgets
          if (!widgets.activeWidgets.includes(data.widgetId)) {
            widgets.activeWidgets.push(data.widgetId);
          }

          // Add widget config if provided
          if (data.config) {
            widgets.configs[data.widgetId] = data.config;
          }

          // Update cache
          await redisClient.set(
            `user:${userId}:widgets`,
            JSON.stringify(widgets),
            { EX: 3600 } // Expire after 1 hour
          );
        }
      }

      // Broadcast to other clients of the same user
      socket.to(`user:${userId}`).emit('widgets:add', {
        widgetId: data.widgetId,
        config: data.config,
      });
    } catch (error) {
      logger.error(`Error handling widget add: ${error}`);
    }
  });

  // Handle widget remove
  socket.on('widgets:remove', async (data: { widgetId: string }) => {
    try {
      const userId = getUserId();

      logger.debug(`User ${userId} removed widget: ${data.widgetId}`);

      // Update widget in database
      await dashboardService.saveWidget({
        userId: new mongoose.Types.ObjectId(userId),
        widgetId: data.widgetId,
        active: false,
      });

      // Leave room for the widget
      socket.leave(`widget:${data.widgetId}`);

      // Update Redis cache
      const redisClient = getRedisClient();
      if (redisClient) {
        const cachedWidgets = await redisClient.get(`user:${userId}:widgets`);

        if (cachedWidgets) {
          const widgets = JSON.parse(cachedWidgets);

          // Remove widget from active widgets
          widgets.activeWidgets = widgets.activeWidgets.filter(id => id !== data.widgetId);

          // Remove widget config
          delete widgets.configs[data.widgetId];

          // Update cache
          await redisClient.set(
            `user:${userId}:widgets`,
            JSON.stringify(widgets),
            { EX: 3600 } // Expire after 1 hour
          );
        }
      }

      // Broadcast to other clients of the same user
      socket.to(`user:${userId}`).emit('widgets:remove', {
        widgetId: data.widgetId,
      });
    } catch (error) {
      logger.error(`Error handling widget remove: ${error}`);
    }
  });

  // Handle widget config update
  socket.on('widgets:updateConfig', async (data: { widgetId: string; config: any }) => {
    try {
      const userId = getUserId();

      logger.debug(`User ${userId} updated widget config: ${data.widgetId}`);

      // Get existing widget from database
      const widget = await dashboardService.getWidget(data.widgetId, userId);

      if (widget) {
        // Update widget config
        await dashboardService.saveWidget({
          userId: new mongoose.Types.ObjectId(userId),
          widgetId: data.widgetId,
          config: {
            ...widget.config,
            ...data.config,
          },
        });
      } else {
        // Create new widget
        await dashboardService.saveWidget({
          userId: new mongoose.Types.ObjectId(userId),
          widgetId: data.widgetId,
          name: data.widgetId, // Use widget ID as name for now
          type: data.widgetId.split('-')[0], // Extract type from ID
          config: data.config,
          active: true,
        });
      }

      // Update Redis cache
      const redisClient = getRedisClient();
      if (redisClient) {
        const cachedWidgets = await redisClient.get(`user:${userId}:widgets`);

        if (cachedWidgets) {
          const widgets = JSON.parse(cachedWidgets);

          // Update widget config
          widgets.configs[data.widgetId] = {
            ...widgets.configs[data.widgetId],
            ...data.config,
          };

          // Update cache
          await redisClient.set(
            `user:${userId}:widgets`,
            JSON.stringify(widgets),
            { EX: 3600 } // Expire after 1 hour
          );
        }
      }

      // Broadcast config update to other clients of the same user
      socket.to(`user:${userId}`).emit('widgets:configUpdate', {
        widgetId: data.widgetId,
        config: data.config,
      });
    } catch (error) {
      logger.error(`Error handling widget config update: ${error}`);
    }
  });

  // Handle widget data request
  socket.on('widget:requestData', async (data: { widgetId: string; dataSource?: string }) => {
    try {
      const userId = getUserId();

      logger.debug(`User ${userId} requested data for widget: ${data.widgetId}`);

      // Generate data based on data source
      let responseData: any[] = [];

      // Try to get real data
      switch (data.dataSource) {
        case 'characters':
          // Get characters from database
          const characters = await mongoose.model('Character').find({
            userId: new mongoose.Types.ObjectId(userId),
          }).select('name race class level').limit(10);

          if (characters.length > 0) {
            responseData = characters.map((char, index) => ({
              id: char._id,
              name: char.name,
              class: char.class,
              level: char.level,
            }));
            break;
          }
          // Fall through to default if no characters found

        case 'inventory':
          // Get character equipment from database
          const character = await mongoose.model('Character').findOne({
            userId: new mongoose.Types.ObjectId(userId),
          }).select('equipment');

          if (character && character.equipment && character.equipment.length > 0) {
            responseData = character.equipment.map((item, index) => ({
              id: index + 1,
              name: item.name,
              quantity: item.quantity || 1,
              value: 0, // Value not stored in database
            }));
            break;
          }
          // Fall through to default if no inventory found

        default:
          // Use sample data for now
          responseData = getSampleData(data.dataSource);
      }

      // Send data to the client
      socket.emit('widget:tableData', {
        widgetId: data.widgetId,
        data: responseData,
      });
    } catch (error) {
      logger.error(`Error handling widget data request: ${error}`);

      // Send sample data as fallback
      socket.emit('widget:tableData', {
        widgetId: data.widgetId,
        data: getSampleData(data.dataSource),
      });
    }
  });

  // Handle widget event
  socket.on('widget:event', async (data: { widgetId: string; eventType: string; payload?: any }) => {
    try {
      const userId = getUserId();

      logger.debug(`User ${userId} sent event for widget: ${data.widgetId}, type: ${data.eventType}`);

      // Broadcast event to other clients of the same user
      socket.to(`user:${userId}`).emit('widget:event', {
        widgetId: data.widgetId,
        eventType: data.eventType,
        payload: data.payload,
      });
    } catch (error) {
      logger.error(`Error handling widget event: ${error}`);
    }
  });

  // Handle widget init
  socket.on('widget:init', async (data: { widgetId: string }) => {
    try {
      const userId = getUserId();

      logger.debug(`User ${userId} initialized widget: ${data.widgetId}`);

      // Join room for the widget
      socket.join(`widget:${data.widgetId}`);

      // Get widget from database
      const widget = await dashboardService.getWidget(data.widgetId, userId);

      if (widget) {
        // Send initial data
        socket.emit('widget:dataUpdate', {
          widgetId: data.widgetId,
          payload: widget.config,
        });
      } else {
        // Try to get from Redis
        const redisClient = getRedisClient();
        if (redisClient) {
          const cachedWidgets = await redisClient.get(`user:${userId}:widgets`);

          if (cachedWidgets) {
            const widgets = JSON.parse(cachedWidgets);

            if (widgets.configs[data.widgetId]) {
              socket.emit('widget:dataUpdate', {
                widgetId: data.widgetId,
                payload: widgets.configs[data.widgetId],
              });
            }
          }
        }
      }
    } catch (error) {
      logger.error(`Error handling widget init: ${error}`);
    }
  });

  // Handle dice roll
  socket.on('dice:roll', (roll: any) => {
    try {
      const userId = getUserId();

      logger.debug(`User ${userId} rolled dice: ${JSON.stringify(roll)}`);

      // Broadcast dice roll to other clients of the same user
      socket.to(`user:${userId}`).emit('dice:roll', roll);
    } catch (error) {
      logger.error(`Error handling dice roll: ${error}`);
    }
  });
};

/**
 * Get sample data for widget
 *
 * @param dataSource Data source
 * @returns Sample data
 */
function getSampleData(dataSource?: string): any[] {
  switch (dataSource) {
    case 'characters':
      return [
        { id: 1, name: 'Aragorn', class: 'Ranger', level: 8 },
        { id: 2, name: 'Gandalf', class: 'Wizard', level: 15 },
        { id: 3, name: 'Legolas', class: 'Ranger', level: 7 },
        { id: 4, name: 'Gimli', class: 'Fighter', level: 6 },
        { id: 5, name: 'Frodo', class: 'Rogue', level: 4 },
      ];
    case 'inventory':
      return [
        { id: 1, name: 'Healing Potion', quantity: 5, value: 50 },
        { id: 2, name: 'Longsword', quantity: 1, value: 15 },
        { id: 3, name: 'Chain Mail', quantity: 1, value: 75 },
        { id: 4, name: 'Rations', quantity: 10, value: 5 },
        { id: 5, name: 'Rope', quantity: 1, value: 1 },
      ];
    default:
      return [
        { id: 1, name: 'Item 1', value: 100 },
        { id: 2, name: 'Item 2', value: 200 },
        { id: 3, name: 'Item 3', value: 300 },
        { id: 4, name: 'Item 4', value: 400 },
        { id: 5, name: 'Item 5', value: 500 },
      ];
  }
}
