# Dashboard Socket.IO Handlers

## Overview

The Dashboard Socket.IO handlers manage real-time communication between the client and server for dashboard-related operations. They handle saving and loading dashboard layouts, widget configurations, and user preferences.

## Key Features

- **Dashboard Layout Persistence**: Saves and loads dashboard layouts from MongoDB and Redis
- **Widget State Management**: Tracks active widgets and their configurations
- **Real-time Synchronization**: Broadcasts changes to all connected clients for the same user
- **Fallback Mechanisms**: Provides default layouts when no saved layouts exist
- **Caching Strategy**: Uses Redis for quick access to frequently used layouts

## Technical Implementation

### Socket Event Handlers

The server implements the following Socket.IO event handlers for dashboard operations:

#### Dashboard Layout Handlers

| Event | Purpose | Parameters | Response |
|-------|---------|------------|----------|
| `dashboard:layoutChange` | Save changes to dashboard layout | `layouts`: Object containing layout configurations for different breakpoints | None |
| `dashboard:request` | Request saved dashboard layout | None | `dashboard:update` event with saved layouts |
| `dashboard:saveLayout` | Save a named dashboard layout | `{ name: string, layouts: Object }` | `dashboard:saveSuccess` event with dashboardId |

#### Widget Handlers

| Event | Purpose | Parameters | Response |
|-------|---------|------------|----------|
| `widgets:sync` | Synchronize active widgets and their configs | `{ activeWidgets: string[], configs: Object }` | None |
| `widgets:add` | Add a new widget | `{ widgetId: string, config?: Object }` | None |
| `widgets:remove` | Remove a widget | `{ widgetId: string }` | None |
| `widgets:updateConfig` | Update widget configuration | `{ widgetId: string, config: Object }` | None |
| `widget:requestData` | Request data for a widget | `{ widgetId: string, dataSource?: string }` | `widget:tableData` event with requested data |
| `widget:event` | Send a widget-specific event | `{ widgetId: string, eventType: string, payload?: any }` | None |
| `widget:init` | Initialize a widget | `{ widgetId: string }` | `widget:dataUpdate` event with widget config |

### Authentication Handling

The handlers support both authenticated and unauthenticated users:

- For authenticated users, the user ID is retrieved from the session
- For unauthenticated users (development/testing), a default user ID is used
- User-specific rooms are created for broadcasting events to the same user's clients

### Persistence Strategy

The dashboard state is persisted using a multi-layered approach:

1. **MongoDB Storage**:
   - Dashboard layouts are stored in the `Dashboard` collection
   - Widget configurations are stored in the `Widget` collection
   - Provides long-term persistence across server restarts

2. **Redis Caching**:
   - Frequently accessed data is cached in Redis
   - Dashboard layouts: `dashboard:layouts:{userId}`
   - Default dashboard: `dashboard:default:{userId}`
   - Widget configurations: `user:{userId}:widgets`
   - Cache expiration is set to 1 hour by default

3. **Client-side Storage**:
   - Layouts and widget visibility are also stored in localStorage
   - Provides fallback when offline or during initial load

## Code Structure

### Dashboard Layout Handlers

```typescript
// Handle dashboard layout changes
socket.on('dashboard:layoutChange', async (layouts: any) => {
  try {
    const userId = getUserId();
    
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
```

### Widget Handlers

```typescript
// Handle widget sync
socket.on('widgets:sync', async (data: { activeWidgets: string[]; configs: Record<string, any> }) => {
  try {
    const userId = getUserId();
    
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
        name: widgetId,
        type: widgetId.split('-')[0],
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
        { EX: 3600 }
      );
    }
  } catch (error) {
    logger.error(`Error handling widget sync: ${error}`);
  }
});
```

## Dependencies

- socket.io: For real-time bidirectional communication
- mongoose: For MongoDB database operations
- redis: For Redis caching operations
- logger: For logging events and errors
