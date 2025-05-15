# Connection Status Widget Update

## Overview

The Connection Status Widget has been updated to include monitoring for the Chroma vector database in addition to MongoDB, Redis, and Socket.IO. This widget provides real-time status information for all critical services used by the RPGer application.

## Features

- **Color-coded status indicators**:
  - Green: Connected
  - Red: Disconnected
  - Amber: Connecting/Checking

- **Service-specific statistics**:
  - **MongoDB**: Collections count, database name, and size
  - **Redis**: Memory usage and key count
  - **Chroma**: Collections count, embeddings count, and version
  - **Socket.IO**: Connection status

- **Manual refresh**: Users can manually refresh the connection status by clicking the "Refresh" button

## Technical Implementation

### Frontend Component

The widget is implemented in `app_stack/frontend/src/components/widgets/ConnectionStatusWidget.tsx` and uses the following:

- React for the UI components
- Fetch API for making HTTP requests to the backend
- CSS for styling (defined in `app_stack/frontend/src/styles/widgets/ConnectionStatusWidget.css`)

### Backend API

The widget relies on the `/api/status` endpoint implemented in `app_stack/backend/rpg_web_app.py`. This endpoint checks the status of all services and returns a JSON response with the following structure:

```json
{
  "mongodb": {
    "connected": true,
    "collections": 5,
    "databaseName": "rpger",
    "databaseSize": "25 MB"
  },
  "redis": {
    "connected": true,
    "usedMemory": "12 MB",
    "totalKeys": 42,
    "uptime": 3600
  },
  "chroma": {
    "connected": true,
    "collections": 3,
    "embeddings": 150,
    "version": "latest"
  },
  "socketio": {
    "connected": true,
    "clients": 1
  }
}
```

## Usage

The Connection Status Widget is automatically included in the RPG Dashboard and can be toggled on/off through the dashboard settings panel.

## Troubleshooting

### MongoDB shows as disconnected

- **Cause**: MongoDB container is not running or the connection parameters are incorrect
- **Solution**: 
  1. Check if the MongoDB container is running: `docker ps | grep rpger-mongodb`
  2. Start the container if needed: `docker start rpger-mongodb`
  3. Verify MongoDB connection parameters in the backend code

### Redis shows as disconnected

- **Cause**: Redis container is not running or the connection parameters are incorrect
- **Solution**: 
  1. Check if the Redis container is running: `docker ps | grep rpger-redis`
  2. Start the container if needed: `docker start rpger-redis`
  3. Verify Redis connection parameters in the backend code

### Chroma shows as disconnected

- **Cause**: Chroma container is not running or the API endpoint is not accessible
- **Solution**: 
  1. Check if the Chroma container is running: `docker ps | grep rpger-chroma`
  2. Start the container if needed: `docker start rpger-chroma`
  3. Test the Chroma API directly: `curl -s http://localhost:8000/api/v2/heartbeat`

### Socket.IO shows as disconnected

- **Cause**: Socket.IO server is not running or there's a CORS issue
- **Solution**: 
  1. Check if the Flask-SocketIO server is running
  2. Verify CORS configuration in the backend code
  3. Check browser console for CORS-related errors

## Verification Steps

1. Check if the Flask-SocketIO server is running:
   ```bash
   ps aux | grep "python.*rpg_web_app.py"
   ```

2. Test the API endpoints directly:
   ```bash
   curl -s http://localhost:5002/api/status
   curl -s http://localhost:5002/api/socketio-status
   ```

3. Check if database containers are running:
   ```bash
   docker ps | grep -E 'rpger-mongodb|rpger-redis|rpger-chroma'
   ```

## Future Enhancements

- Add more detailed statistics for each service
- Implement automatic reconnection attempts
- Add historical status tracking
- Implement alerts for service outages
