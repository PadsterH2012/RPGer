# Socket.IO Context and Hooks

## Overview

The Socket.IO Context and Hooks provide a centralized way to manage Socket.IO connections throughout the RPGer application. They enable components to establish real-time communication with the server and handle connection state.

## Key Components

- **SocketContext**: React context that provides Socket.IO connection and state
- **SocketProvider**: Provider component that manages the Socket.IO connection
- **useSocket**: Custom hook for consuming the Socket.IO context

## Technical Implementation

### SocketContext

The SocketContext is a React context that provides the following values:

- `socket`: The Socket.IO client instance
- `isConnected`: Boolean indicating whether the socket is connected
- `connect`: Function to establish a connection
- `disconnect`: Function to close the connection

```typescript
interface SocketContextType {
  socket: Socket | null;
  isConnected: boolean;
  connect: () => void;
  disconnect: () => void;
}

const SocketContext = createContext<SocketContextType | undefined>(undefined);
```

### SocketProvider

The SocketProvider is a React component that manages the Socket.IO connection and provides the context values to its children:

```typescript
export const SocketProvider: React.FC<SocketProviderProps> = ({ children }) => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);

  const connect = () => {
    // Use environment variable for the server URL or default to the current server
    const serverUrl = process.env.REACT_APP_SOCKET_URL || 'http://localhost:5000';
    console.log('Connecting to socket server at:', serverUrl);
    const newSocket = io(serverUrl, {
      transports: ['websocket', 'polling'],
      autoConnect: true,
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    });

    newSocket.on('connect', () => {
      console.log('Socket connected');
      setIsConnected(true);
    });

    newSocket.on('disconnect', () => {
      console.log('Socket disconnected');
      setIsConnected(false);
    });

    newSocket.on('connect_error', (error) => {
      console.error('Socket connection error:', error);
      setIsConnected(false);
    });

    setSocket(newSocket);
  };

  const disconnect = () => {
    if (socket) {
      socket.disconnect();
      setSocket(null);
      setIsConnected(false);
    }
  };

  // Connect to socket when component mounts
  useEffect(() => {
    connect();

    // Cleanup on unmount
    return () => {
      if (socket) {
        socket.disconnect();
      }
    };
  }, []);

  const value = {
    socket,
    isConnected,
    connect,
    disconnect,
  };

  return (
    <SocketContext.Provider value={value}>
      {children}
    </SocketContext.Provider>
  );
};
```

### useSocket Hook

The useSocket hook provides a convenient way to access the Socket.IO context:

```typescript
export const useSocket = (): SocketContextType => {
  const context = useContext(SocketContext);
  if (context === undefined) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
};
```

## Usage

### Setting Up the Provider

Wrap your application or component tree with the SocketProvider:

```jsx
import { SocketProvider } from './context/SocketContext';

function App() {
  return (
    <SocketProvider>
      <YourComponent />
    </SocketProvider>
  );
}
```

### Using the Hook in Components

Use the useSocket hook to access the Socket.IO connection in your components:

```jsx
import { useSocket } from './context/SocketContext';

function YourComponent() {
  const { socket, isConnected } = useSocket();

  useEffect(() => {
    if (socket && isConnected) {
      // Listen for events
      socket.on('some-event', handleEvent);

      // Emit events
      socket.emit('client-event', { data: 'some data' });

      // Cleanup
      return () => {
        socket.off('some-event', handleEvent);
      };
    }
  }, [socket, isConnected]);

  return (
    <div>
      <p>Socket status: {isConnected ? 'Connected' : 'Disconnected'}</p>
      {/* Your component content */}
    </div>
  );
}
```

## Connection Configuration

The Socket.IO connection is configured with the following options:

- **transports**: Uses WebSocket as the primary transport with polling as fallback
- **autoConnect**: Automatically connects when the socket is created
- **reconnection**: Enables automatic reconnection
- **reconnectionAttempts**: Limits reconnection attempts to 5
- **reconnectionDelay**: Sets a 1-second delay between reconnection attempts

## Event Handling

The SocketProvider sets up the following event handlers:

- **connect**: Updates the connection state when the socket connects
- **disconnect**: Updates the connection state when the socket disconnects
- **connect_error**: Handles connection errors

Components using the useSocket hook can set up their own event handlers for application-specific events.

## Dependencies

- socket.io-client: For Socket.IO client functionality
- react: For React context and hooks
