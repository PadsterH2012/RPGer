# Dashboard Test

This directory contains scripts to test the integration between the Python backend and the React dashboard.

## Files

- `dashboard_test.py`: A Flask-SocketIO server that emits test data to the dashboard
- `test_client.py`: A Socket.IO client that connects to the server and listens for events
- `run_dashboard_test.sh`: A shell script to run the dashboard test server

## Prerequisites

Make sure you have the following Python packages installed:

```bash
pip install flask flask-socketio flask-cors python-socketio requests
```

## Running the Test

### Option 1: Test with the React Frontend

1. Start the dashboard test server:

```bash
./run_dashboard_test.sh
```

2. In another terminal, start the React frontend:

```bash
cd /mnt/network_repo/RPGer/App/client
npm start
```

3. Open your browser and navigate to the React app (usually http://localhost:3000)

4. Verify that the ConnectionStatusWidget shows the connection status for MongoDB, Redis, and SocketIO

### Option 2: Test with the Python Client

1. Start the dashboard test server:

```bash
./dashboard_test.py
```

2. In another terminal, run the test client:

```bash
./test_client.py
```

3. The test client will connect to the server, listen for events, and send test commands

4. Check the output of both the server and client to verify that events are being sent and received correctly

## Expected Results

### Server Output

The server should log messages like:

```
INFO:DashboardTest:Starting Flask-SocketIO server on http://0.0.0.0:5002
INFO:DashboardTest:Connecting to MongoDB...
INFO:DashboardTest:Connecting to Redis...
INFO:DashboardTest:Connected to MongoDB. Collections: 5
INFO:DashboardTest:Connected to Redis. Memory usage: 25 MB
INFO:DashboardTest:Emitting game state update
INFO:DashboardTest:Client connected: abc123
INFO:DashboardTest:Received get_game_state request from abc123
```

### Client Output

The test client should log messages like:

```
INFO:TestClient:Checking API status...
INFO:TestClient:API Status:
INFO:TestClient:MongoDB: True
INFO:TestClient:Redis: True
INFO:TestClient:SocketIO: True
INFO:TestClient:Checking Socket.IO status...
INFO:TestClient:Socket.IO Status: {'status': 'ok', 'version': '5.3.6', 'clients': 0}
INFO:TestClient:Connecting to Socket.IO server...
INFO:TestClient:Connected to server
INFO:TestClient:Received response: {'message': 'Connected to Dashboard Test Server'}
INFO:TestClient:Received game state update
INFO:TestClient:Player: Test Character, HP: 10/10
INFO:TestClient:Location: Test Dungeon
INFO:TestClient:Latest DM message: This is a test message from the DM.
```

### React Frontend

The React frontend should display:

1. The ConnectionStatusWidget with green indicators for MongoDB, Redis, and SocketIO
2. MongoDB collections and database size information
3. Redis memory usage and key count information
4. Real-time updates as the server emits new game state data

## Troubleshooting

If you encounter issues:

1. Check that the server is running on port 5002
2. Verify that the React frontend is configured to connect to http://localhost:5002
3. Check the browser console for any connection errors
4. Ensure that CORS is properly configured on the server
5. Check that the event names match between server and client
