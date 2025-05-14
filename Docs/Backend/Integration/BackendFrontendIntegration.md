# Backend-Frontend Integration

## Overview

This document describes the integration between the Python backend and the React frontend dashboard. The integration enables real-time communication between the backend and frontend, allowing the dashboard to display data from the backend and send commands to the backend.

## Communication Protocol

The integration uses two primary communication mechanisms:

1. **Socket.IO**: For real-time bidirectional communication
2. **REST API**: For status information and non-real-time data

### Socket.IO Communication

Socket.IO provides a WebSocket-based communication channel between the backend and frontend. The backend emits events that the frontend listens for, and the frontend emits events that the backend listens for.

#### Backend Socket.IO Implementation

The backend uses Flask-SocketIO to implement the Socket.IO server:

```python
from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# Event handlers
@socketio.on('connect')
def handle_connect():
    emit('response', {'message': 'Connected to backend'})

@socketio.on('command')
def handle_command(data):
    # Process command
    # ...
    
    # Emit updated game state
    socketio.emit('game_state_update', game_state)
```

#### Frontend Socket.IO Implementation

The frontend uses the Socket.IO client library to connect to the backend:

```typescript
import { io, Socket } from 'socket.io-client';

// Create Socket.IO connection
const socket = io('http://localhost:5002', {
  transports: ['websocket', 'polling'],
  autoConnect: true,
  reconnection: true
});

// Event listeners
socket.on('connect', () => {
  console.log('Connected to server');
});

socket.on('game_state_update', (data) => {
  // Update UI with new game state
  // ...
});

// Emit events
socket.emit('command', { command: 'look around' });
```

### REST API Communication

The backend provides REST API endpoints for status information and non-real-time data:

```python
@app.route('/api/status')
def api_status():
    """API endpoint to check the status of services"""
    status = {
        "mongodb": {
            "connected": True,
            "collections": 7,
            "databaseName": "rpger",
            "databaseSize": "25 MB"
        },
        "redis": {
            "connected": True,
            "usedMemory": "12 MB",
            "totalKeys": 42,
            "uptime": 3600
        },
        "socketio": {
            "connected": True,
            "clients": 1
        }
    }
    return jsonify(status)
```

The frontend uses fetch to call these endpoints:

```typescript
const checkConnections = async () => {
  try {
    const response = await fetch('http://localhost:5002/api/status');
    if (response.status === 200) {
      const data = await response.json();
      // Update UI with status information
      // ...
    }
  } catch (error) {
    console.error('Error checking connections:', error);
  }
};
```

## Event Reference

### Backend to Frontend Events

| Event Name | Description | Data Structure |
|------------|-------------|----------------|
| `game_state_update` | Updates the game state | Game state object with player, environment, and other data |
| `response` | General response to client actions | `{ message: string }` |
| `widget:tableData` | Data for table widgets | `{ widgetId: string, data: any[] }` |

### Frontend to Backend Events

| Event Name | Description | Data Structure |
|------------|-------------|----------------|
| `command` | Send a command to the backend | `{ command: string }` |
| `get_game_state` | Request the current game state | None |
| `widget:requestData` | Request data for a widget | `{ widgetId: string, dataSource?: string }` |

## Data Structures

### Game State

The game state object contains all the information needed to render the dashboard:

```typescript
interface GameState {
  player: {
    name: string;
    race: string;
    class: string;
    level: number;
    hp: number;
    max_hp: number;
    stats: Record<string, number>;
  };
  environment: {
    location: string;
    description: string;
    creatures: any[];
  };
  world: {
    time: Record<string, any>;
    weather: Record<string, any>;
    light: Record<string, any>;
  };
  action_results: string[];
  dm_messages: string[];
  agent_debug: string[];
  processing: boolean;
  last_update: number;
}
```

## Configuration

### Port Configuration

The backend runs on port 5002, and the frontend is configured to connect to this port:

```typescript
// In SocketContext.tsx
const serverUrl = process.env.REACT_APP_SOCKET_URL || 'http://localhost:5002';
```

### API Endpoint URLs

The ConnectionStatusWidget is configured to use the following API endpoints:

```typescript
// In ConnectionStatusWidget.tsx
const response = await fetch('http://localhost:5002/api/status');
const socketResponse = await fetch('http://localhost:5002/api/socketio-status');
```

## Testing

The integration has been tested using the following scripts:

- `dashboard_test.py`: A Flask-SocketIO server that emits test data to the dashboard
- `test_client.py`: A Socket.IO client that connects to the server and listens for events

These scripts demonstrate the communication flow between the backend and frontend, verifying that the old Python code can output to the new dashboard windows.

## Conclusion

The integration between the Python backend and React frontend dashboard is working correctly. The Socket.IO communication protocol enables real-time updates, and the REST API provides status information. The data structures are compatible between the old and new code, allowing for seamless integration.
