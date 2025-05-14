# Connection Status Widget

## Overview

The Connection Status Widget displays the current connection status of critical services used by the RPGer application:
- MongoDB database
- Redis cache
- Socket.IO real-time communication

The widget provides visual indicators for each service's connection state and displays relevant statistics when connected.

## Technical Implementation

The Connection Status Widget is implemented in `App/client/src/components/widgets/ConnectionStatusWidget.tsx` and uses the following technologies:
- React for the UI components
- Fetch API for making HTTP requests to the backend
- CSS for styling (defined in `App/client/src/styles/widgets/ConnectionStatusWidget.css`)

## API Dependencies

The widget relies on two backend API endpoints:
- `http://localhost:5002/api/status` - Provides status information for all services
- `http://localhost:5002/api/socketio-status` - Fallback endpoint for checking Socket.IO status

These endpoints are implemented in the Flask-SocketIO backend (`App/backend/rpg_web_app.py`).

## Connection States

The widget displays three possible connection states for each service:
1. **Connected** (green) - The service is running and accessible
2. **Disconnected** (red) - The service is not running or not accessible
3. **Connecting** (amber) - The widget is attempting to connect to the service

## Service Statistics

When connected, the widget displays the following statistics:
- **MongoDB**: Collections count, database name, and database size
- **Redis**: Memory usage and keys count
- **Socket.IO**: Active status

## Troubleshooting

### Common Issues

1. **All services show as disconnected**
   - **Cause**: The Flask-SocketIO server is not running
   - **Solution**: Start the server using `scripts/start-rpg.sh` or directly with `python App/backend/rpg_web_app.py`

2. **MongoDB shows as disconnected**
   - **Cause**: MongoDB container is not running
   - **Solution**: Start the MongoDB container with `docker start rpger-mongodb` or using the start script

3. **Redis shows as disconnected**
   - **Cause**: Redis container is not running
   - **Solution**: Start the Redis container with `docker start rpger-redis` or using the start script

4. **Socket.IO shows as disconnected**
   - **Cause**: Socket.IO server is not running or there's a CORS issue
   - **Solution**: Check that the Flask-SocketIO server is running and CORS is properly configured

### Verification Steps

1. Check if the Flask-SocketIO server is running:
   ```bash
   ps aux | grep "python.*rpg_web_app.py"
   ```

2. Test the API endpoints directly:
   ```bash
   curl -s http://localhost:5002/api/status
   curl -s http://localhost:5002/api/socketio-status
   ```

3. Check if MongoDB and Redis containers are running:
   ```bash
   docker ps | grep -E 'rpger-mongodb|rpger-redis'
   ```

4. Check browser console for any error messages related to API calls or CORS issues

## Maintenance

The widget automatically refreshes every 15 seconds, but users can manually refresh by clicking the "Refresh" button. The last check time is displayed at the bottom of the widget.

To modify the refresh interval, update the `setInterval` call in the `useEffect` hook in the `ConnectionStatusWidget.tsx` file.
