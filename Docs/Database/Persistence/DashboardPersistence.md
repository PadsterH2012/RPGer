# Dashboard Persistence

## Overview

The Dashboard Persistence layer manages the storage and retrieval of dashboard layouts and widget configurations in the RPGer application. It provides a robust mechanism for persisting user customizations across sessions and server restarts.

## Key Components

- **Dashboard Model**: Defines the schema for storing dashboard layouts
- **Widget Model**: Defines the schema for storing widget configurations
- **Dashboard Service**: Provides methods for CRUD operations on dashboards and widgets
- **Redis Cache**: Provides fast access to frequently used dashboard data

## Technical Implementation

### Database Schema

#### Dashboard Schema

```typescript
// Dashboard document interface
export interface IDashboard extends Document {
  userId: mongoose.Types.ObjectId;
  name: string;
  description?: string;
  layouts: Record<string, any>;
  isDefault: boolean;
  createdAt: Date;
  updatedAt: Date;
}

// Dashboard schema
const DashboardSchema = new Schema<IDashboard>(
  {
    userId: {
      type: Schema.Types.ObjectId,
      ref: 'User',
      required: true,
    },
    name: {
      type: String,
      required: true,
      trim: true,
    },
    description: {
      type: String,
      trim: true,
    },
    layouts: {
      type: Schema.Types.Mixed,
      required: true,
    },
    isDefault: {
      type: Boolean,
      default: false,
    },
  },
  {
    timestamps: true,
  }
);
```

#### Widget Schema

```typescript
// Widget document interface
export interface IWidget extends Document {
  userId: mongoose.Types.ObjectId;
  widgetId: string;
  name: string;
  type: string;
  config: Record<string, any>;
  layout: Record<string, WidgetLayout>;
  active: boolean;
  createdAt: Date;
  updatedAt: Date;
}

// Widget schema
const WidgetSchema = new Schema<IWidget>(
  {
    userId: {
      type: Schema.Types.ObjectId,
      ref: 'User',
      required: true,
    },
    widgetId: {
      type: String,
      required: true,
    },
    name: {
      type: String,
      required: true,
      trim: true,
    },
    type: {
      type: String,
      required: true,
    },
    config: {
      type: Schema.Types.Mixed,
      default: {},
    },
    layout: {
      type: Map,
      of: {
        x: Number,
        y: Number,
        w: Number,
        h: Number,
        minW: Number,
        minH: Number,
        maxW: Number,
        maxH: Number,
      },
      default: {},
    },
    active: {
      type: Boolean,
      default: true,
    },
  },
  {
    timestamps: true,
  }
);

// Create compound index for userId and widgetId
WidgetSchema.index({ userId: 1, widgetId: 1 }, { unique: true });
```

### Dashboard Service

The Dashboard Service provides methods for managing dashboards and widgets:

#### Dashboard Methods

- `getDashboards(userId)`: Get all dashboards for a user
- `getDashboard(dashboardId, userId)`: Get a specific dashboard
- `getDefaultDashboard(userId)`: Get the default dashboard for a user
- `createDashboard(dashboard)`: Create a new dashboard
- `updateDashboard(dashboardId, userId, updates)`: Update a dashboard
- `deleteDashboard(dashboardId, userId)`: Delete a dashboard

#### Widget Methods

- `getWidgets(userId)`: Get all widgets for a user
- `getActiveWidgets(userId)`: Get active widgets for a user
- `getWidget(widgetId, userId)`: Get a specific widget
- `saveWidget(widget)`: Create or update a widget
- `deleteWidget(widgetId, userId)`: Delete a widget

### Caching Strategy

The application uses Redis for caching frequently accessed dashboard data:

#### Cache Keys

- `dashboard:default:{userId}`: The default dashboard for a user
- `dashboard:layouts:{userId}`: Dashboard layouts for a user
- `user:{userId}:widgets`: Active widgets and their configurations for a user

#### Cache Operations

- **Set**: Store data in the cache with an expiration time (typically 1 hour)
- **Get**: Retrieve data from the cache
- **Del**: Remove data from the cache (e.g., when a dashboard is deleted)

### Data Flow

1. **Read Path**:
   - Check Redis cache first for the requested data
   - If not found in cache, query MongoDB
   - If found in MongoDB, store in Redis cache for future requests
   - Return the data to the client

2. **Write Path**:
   - Update MongoDB with the new data
   - Update Redis cache to reflect the changes
   - Broadcast changes to connected clients via Socket.IO

## Code Examples

### Getting the Default Dashboard

```typescript
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
```

### Saving a Widget

```typescript
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
```

## Dependencies

- mongoose: For MongoDB database operations
- redis: For Redis caching operations
- logger: For logging events and errors
