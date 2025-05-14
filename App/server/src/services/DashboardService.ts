/**
 * Dashboard Service
 * 
 * Handles dashboard-related operations
 */

import mongoose from 'mongoose';
import { Dashboard, IDashboard } from '../models/Dashboard';
import { Widget, IWidget } from '../models/Widget';
import { getRedisClient } from '../config/redis';
import { logger } from '../utils/logger';

class DashboardService {
  /**
   * Get all dashboards for a user
   * 
   * @param userId User ID
   * @returns Array of dashboards
   */
  public async getDashboards(userId: string): Promise<IDashboard[]> {
    try {
      return await Dashboard.find({ userId: new mongoose.Types.ObjectId(userId) });
    } catch (error) {
      logger.error(`Error getting dashboards: ${error}`);
      return [];
    }
  }
  
  /**
   * Get a dashboard by ID
   * 
   * @param dashboardId Dashboard ID
   * @param userId User ID
   * @returns Dashboard or null
   */
  public async getDashboard(dashboardId: string, userId: string): Promise<IDashboard | null> {
    try {
      return await Dashboard.findOne({
        _id: new mongoose.Types.ObjectId(dashboardId),
        userId: new mongoose.Types.ObjectId(userId),
      });
    } catch (error) {
      logger.error(`Error getting dashboard: ${error}`);
      return null;
    }
  }
  
  /**
   * Get the default dashboard for a user
   * 
   * @param userId User ID
   * @returns Default dashboard or null
   */
  public async getDefaultDashboard(userId: string): Promise<IDashboard | null> {
    try {
      // Try to get from Redis cache first
      const redisClient = getRedisClient();
      if (redisClient) {
        const cachedDashboard = await redisClient.get(`dashboard:default:${userId}`);
        if (cachedDashboard) {
          return JSON.parse(cachedDashboard);
        }
      }
      
      // Get from database
      const dashboard = await Dashboard.findOne({
        userId: new mongoose.Types.ObjectId(userId),
        isDefault: true,
      });
      
      // Cache in Redis if available
      if (dashboard && redisClient) {
        await redisClient.set(
          `dashboard:default:${userId}`,
          JSON.stringify(dashboard),
          { EX: 3600 } // Expire after 1 hour
        );
      }
      
      return dashboard;
    } catch (error) {
      logger.error(`Error getting default dashboard: ${error}`);
      return null;
    }
  }
  
  /**
   * Create a new dashboard
   * 
   * @param dashboard Dashboard data
   * @returns Created dashboard or null
   */
  public async createDashboard(dashboard: Partial<IDashboard>): Promise<IDashboard | null> {
    try {
      const newDashboard = await Dashboard.create(dashboard);
      
      // If this is the default dashboard, make sure no other dashboard is default
      if (newDashboard.isDefault) {
        await Dashboard.updateMany(
          {
            userId: newDashboard.userId,
            _id: { $ne: newDashboard._id },
          },
          { isDefault: false }
        );
        
        // Update Redis cache
        const redisClient = getRedisClient();
        if (redisClient) {
          await redisClient.set(
            `dashboard:default:${newDashboard.userId}`,
            JSON.stringify(newDashboard),
            { EX: 3600 } // Expire after 1 hour
          );
        }
      }
      
      return newDashboard;
    } catch (error) {
      logger.error(`Error creating dashboard: ${error}`);
      return null;
    }
  }
  
  /**
   * Update a dashboard
   * 
   * @param dashboardId Dashboard ID
   * @param userId User ID
   * @param updates Dashboard updates
   * @returns Updated dashboard or null
   */
  public async updateDashboard(
    dashboardId: string,
    userId: string,
    updates: Partial<IDashboard>
  ): Promise<IDashboard | null> {
    try {
      const dashboard = await Dashboard.findOneAndUpdate(
        {
          _id: new mongoose.Types.ObjectId(dashboardId),
          userId: new mongoose.Types.ObjectId(userId),
        },
        updates,
        { new: true }
      );
      
      // If this is now the default dashboard, make sure no other dashboard is default
      if (dashboard && updates.isDefault) {
        await Dashboard.updateMany(
          {
            userId: dashboard.userId,
            _id: { $ne: dashboard._id },
          },
          { isDefault: false }
        );
        
        // Update Redis cache
        const redisClient = getRedisClient();
        if (redisClient) {
          await redisClient.set(
            `dashboard:default:${userId}`,
            JSON.stringify(dashboard),
            { EX: 3600 } // Expire after 1 hour
          );
        }
      }
      
      return dashboard;
    } catch (error) {
      logger.error(`Error updating dashboard: ${error}`);
      return null;
    }
  }
  
  /**
   * Delete a dashboard
   * 
   * @param dashboardId Dashboard ID
   * @param userId User ID
   * @returns Boolean indicating success
   */
  public async deleteDashboard(dashboardId: string, userId: string): Promise<boolean> {
    try {
      const dashboard = await Dashboard.findOneAndDelete({
        _id: new mongoose.Types.ObjectId(dashboardId),
        userId: new mongoose.Types.ObjectId(userId),
      });
      
      // If this was the default dashboard, clear Redis cache
      if (dashboard && dashboard.isDefault) {
        const redisClient = getRedisClient();
        if (redisClient) {
          await redisClient.del(`dashboard:default:${userId}`);
        }
      }
      
      return !!dashboard;
    } catch (error) {
      logger.error(`Error deleting dashboard: ${error}`);
      return false;
    }
  }
  
  /**
   * Get all widgets for a user
   * 
   * @param userId User ID
   * @returns Array of widgets
   */
  public async getWidgets(userId: string): Promise<IWidget[]> {
    try {
      return await Widget.find({ userId: new mongoose.Types.ObjectId(userId) });
    } catch (error) {
      logger.error(`Error getting widgets: ${error}`);
      return [];
    }
  }
  
  /**
   * Get active widgets for a user
   * 
   * @param userId User ID
   * @returns Array of active widgets
   */
  public async getActiveWidgets(userId: string): Promise<IWidget[]> {
    try {
      return await Widget.find({
        userId: new mongoose.Types.ObjectId(userId),
        active: true,
      });
    } catch (error) {
      logger.error(`Error getting active widgets: ${error}`);
      return [];
    }
  }
  
  /**
   * Get a widget by ID
   * 
   * @param widgetId Widget ID
   * @param userId User ID
   * @returns Widget or null
   */
  public async getWidget(widgetId: string, userId: string): Promise<IWidget | null> {
    try {
      return await Widget.findOne({
        widgetId,
        userId: new mongoose.Types.ObjectId(userId),
      });
    } catch (error) {
      logger.error(`Error getting widget: ${error}`);
      return null;
    }
  }
  
  /**
   * Create or update a widget
   * 
   * @param widget Widget data
   * @returns Created or updated widget or null
   */
  public async saveWidget(widget: Partial<IWidget>): Promise<IWidget | null> {
    try {
      // Check if widget already exists
      const existingWidget = await Widget.findOne({
        widgetId: widget.widgetId,
        userId: widget.userId,
      });
      
      if (existingWidget) {
        // Update existing widget
        return await Widget.findOneAndUpdate(
          {
            widgetId: widget.widgetId,
            userId: widget.userId,
          },
          widget,
          { new: true }
        );
      } else {
        // Create new widget
        return await Widget.create(widget);
      }
    } catch (error) {
      logger.error(`Error saving widget: ${error}`);
      return null;
    }
  }
  
  /**
   * Delete a widget
   * 
   * @param widgetId Widget ID
   * @param userId User ID
   * @returns Boolean indicating success
   */
  public async deleteWidget(widgetId: string, userId: string): Promise<boolean> {
    try {
      const result = await Widget.deleteOne({
        widgetId,
        userId: new mongoose.Types.ObjectId(userId),
      });
      
      return result.deletedCount > 0;
    } catch (error) {
      logger.error(`Error deleting widget: ${error}`);
      return false;
    }
  }
}

// Export singleton instance
export const dashboardService = new DashboardService();
