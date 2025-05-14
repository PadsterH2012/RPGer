# Debug Message System

## Overview

The Debug Message System is a component of the RPGer backend that provides real-time debugging information to the frontend. It captures, processes, and transmits debug messages from various agents and system components, allowing developers to monitor application behavior and troubleshoot issues.

## Features

- Real-time debug message transmission via Socket.IO
- Agent-specific message categorization
- Message severity levels (info, warning, error, success)
- REST API endpoint for adding debug messages
- Socket.IO event handler for receiving debug messages from clients
- Message history management with automatic pruning

## Technical Implementation

### Message Structure

Debug messages in the system follow this general structure:

```
[Agent]: [Message Content]
```

Where:
- `Agent` is the identifier of the agent generating the message (CMA, NEA, EEA, WEA, MSA, CaMA, System)
- `Message Content` is the actual debug information

For error and warning messages, an additional prefix is added:

```
ERROR: [Agent]: [Message Content]
WARNING: [Agent]: [Message Content]
```

### Game State Integration

Debug messages are stored in the `agent_debug` array within the game state:

```python
game_state = {
    # Other game state properties...
    "agent_debug": [
        "System: Agent debug interface initialized",
        "System: Waiting for game to start..."
    ],
    # More properties...
}
```

### Message Processing

The backend processes debug messages in the following ways:

1. **Message Capture**: Debug messages are captured from print statements, agent outputs, and direct API calls
2. **Agent Detection**: The system attempts to identify the source agent based on message content
3. **Level Detection**: Message severity (info, warning, error, success) is determined based on keywords
4. **Formatting**: Messages are formatted with appropriate prefixes
5. **Storage**: Messages are added to the game state's `agent_debug` array
6. **Pruning**: The array is limited to the most recent 50 messages
7. **Transmission**: Messages are sent to clients via Socket.IO

### Socket.IO Events

The system uses the following Socket.IO events:

- `game_state_update`: Sends the full game state, including all debug messages
- `debug_message`: Sends individual debug messages in real-time
- `send_debug`: Receives debug messages from clients

### REST API

The system provides a REST API endpoint for adding debug messages:

```
POST /api/debug
```

Request body:
```json
{
  "message": "Debug message content",
  "agent": "System",  // Optional, defaults to "System"
  "level": "info"     // Optional, defaults to "info"
}
```

## Usage

### Capturing Debug Messages

Debug messages are automatically captured from print statements that match certain patterns:

```python
# This will be captured as a debug message
print("Agent: Processing command")

# This will be captured as an error message
print("ERROR: Failed to process command")
```

### Adding Debug Messages Directly

Debug messages can be added directly to the game state:

```python
game_state["agent_debug"].append("System: Custom debug message")
```

### Sending Debug Messages via Socket.IO

The backend can emit debug messages directly:

```python
socketio.emit('debug_message', "System: Important debug information")
```

### Receiving Debug Messages from Clients

Clients can send debug messages to the backend:

```javascript
socket.emit('send_debug', {
  message: 'Client debug message',
  agent: 'CMA',
  level: 'warning'
});
```

## Configuration

The debug message system has the following configurable parameters:

- **Message History Limit**: Maximum number of messages stored in the game state (default: 50)
- **Agent Prefixes**: The prefixes used to identify different agents
- **Level Keywords**: The keywords used to determine message severity

## Example

```python
# Example of how debug messages are processed in the backend
def custom_print(*args, **kwargs):
    """Custom print function to capture output"""
    try:
        # Convert args to string
        output = " ".join(str(arg) for arg in args)

        # Check if this is an agent debug message
        if any(keyword in output for keyword in ["Agent", "Requesting", "Extracted JSON", "Updating game state"]):
            # Determine the agent type and message level
            agent_prefix = "System"
            level = "info"
            
            # Check for agent identifiers
            if "Character Management Agent" in output or "CMA" in output:
                agent_prefix = "CMA:"
            # More agent checks...
            
            # Check for message level
            if "ERROR" in output or "error" in output.lower():
                level = "error"
                if not output.startswith("ERROR:"):
                    output = f"ERROR: {output}"
            # More level checks...
            
            # Format the message with agent prefix if not already present
            if not output.startswith(agent_prefix):
                output = f"{agent_prefix} {output}"
            
            # Add to debug messages
            game_state["agent_debug"].append(output)
            
            # Limit to last 50 messages
            if len(game_state["agent_debug"]) > 50:
                game_state["agent_debug"] = game_state["agent_debug"][-50:]
                
            # Also emit a specific debug message event for real-time updates
            socketio.emit('debug_message', output)
    except Exception as e:
        # Error handling...
        pass
```
