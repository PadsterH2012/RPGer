# AgentDebugWidget

## Overview

The AgentDebugWidget is a React component that provides a real-time debugging interface for the RPGer application. It connects to the backend Python logic via Socket.IO and displays debug messages from various agents in the system. The widget allows developers to monitor system activity, troubleshoot issues, and send custom debug messages.

## Features

- Real-time display of debug messages from the backend
- Filtering by agent type or message level
- Color-coded messages based on severity (info, warning, error, success)
- Expandable view for detailed debugging
- Message input form for sending custom debug messages
- Connection status indicator
- Dark mode support

## Technical Implementation

### Component Structure

The AgentDebugWidget is implemented as a functional React component with the following key elements:

- Socket.IO connection for real-time updates
- State management for debug messages
- Message filtering and display logic
- User interface for interaction

### Socket.IO Integration

The widget connects to the backend using the SocketContext provider and listens for the following events:

- `game_state_update`: Receives the full game state, including debug messages
- `debug_message`: Receives individual debug messages in real-time

The widget can also send debug messages to the backend using the `send_debug` event.

### Message Processing

Debug messages from the backend are processed to extract:

- Agent name (CMA, NEA, EEA, WEA, MSA, CaMA, System)
- Message level (info, warning, error, success)
- Message content
- Timestamp

### User Interface

The widget provides the following UI elements:

- Debug message list with color-coded entries
- Filter dropdown for selecting specific agents or message levels
- Expand/collapse button for maximizing the debug view
- Clear button for removing all messages
- Connection status indicator
- Debug message input form (in expanded view)

## Usage

### Basic Usage

The AgentDebugWidget is typically included in the main dashboard layout:

```tsx
import AgentDebugWidget from './widgets/AgentDebugWidget';

// In your component render method:
<div key="agentDebug">
  <AgentDebugWidget />
</div>
```

### Sending Debug Messages

Developers can send custom debug messages using the input form in the expanded view. Messages can be associated with specific agents and assigned different severity levels.

## Styling

The widget uses a dedicated CSS file (`AgentDebugWidget.css`) with the following key style features:

- Responsive layout that adapts to different screen sizes
- Expandable view for detailed debugging
- Color-coded messages based on severity
- Dark mode support
- Animation effects for a polished user experience

## Backend Integration

The widget connects to the following backend endpoints:

- Socket.IO event `game_state_update` for receiving the full game state
- Socket.IO event `debug_message` for receiving individual debug messages
- Socket.IO event `send_debug` for sending custom debug messages
- REST API endpoint `/api/debug` for adding debug messages via HTTP

## Example

```tsx
// Example of how the AgentDebugWidget processes messages
useEffect(() => {
  if (socket && isConnected) {
    socket.on('game_state_update', (gameState: GameState) => {
      if (gameState.agent_debug && gameState.agent_debug.length > 0) {
        // Process debug messages
        const newMessages = gameState.agent_debug.map((message, index) => {
          // Parse message to extract agent and level
          // ...
          return {
            id: `server-${Date.now()}-${index}`,
            agent,
            message: content,
            level,
            timestamp: new Date()
          };
        });
        
        // Update state with new messages
        setDebugMessages(prevMessages => [...prevMessages, ...newMessages]);
      }
    });
    
    // Cleanup on unmount
    return () => {
      socket.off('game_state_update');
    };
  }
}, [socket, isConnected]);
```
