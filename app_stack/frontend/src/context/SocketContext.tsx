import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { io, Socket } from 'socket.io-client';

interface SocketContextType {
  socket: Socket | null;
  isConnected: boolean;
  connect: () => void;
  disconnect: () => void;
}

const SocketContext = createContext<SocketContextType | undefined>(undefined);

interface SocketProviderProps {
  children: ReactNode;
}

export const SocketProvider: React.FC<SocketProviderProps> = ({ children }) => {
  const [socket, setSocket] = useState<Socket | null>(null);
  const [isConnected, setIsConnected] = useState<boolean>(false);

  const connect = () => {
    // Use environment variable for the server URL or default to the current server
    let serverUrl = import.meta.env.VITE_SOCKET_URL || 'http://localhost:5002';

    // If we're running in a browser and the URL contains 'rpger-backend', replace it with 'localhost'
    if (typeof window !== 'undefined' && serverUrl.includes('rpger-backend')) {
      serverUrl = serverUrl.replace('rpger-backend', 'localhost');
    }

    console.log('Connecting to socket server at:', serverUrl);

    // Reset any existing connection first
    if (socket) {
      console.log('Disconnecting existing socket before reconnecting');
      socket.disconnect();
    }

    // More basic configuration to reduce complexity
    console.log('Socket connection config:', {
      serverUrl,
      transports: ['polling', 'websocket'], // Try polling first, then websocket
      reconnectionAttempts: 10,
      reconnectionDelay: 1000,
      timeout: 30000 // Increased timeout further
    });

    const newSocket = io(serverUrl, {
      transports: ['polling', 'websocket'], // Try polling first, then websocket
      autoConnect: true,
      reconnection: true,
      reconnectionAttempts: 10,
      reconnectionDelay: 1000,
      timeout: 30000, // Increased timeout further
      forceNew: true, // Force a new connection
      multiplex: false, // Disable multiplexing
      withCredentials: true, // Send cookies
      extraHeaders: {
        "Access-Control-Allow-Origin": "*"
      }
    });

    newSocket.on('connect', () => {
      console.log('Socket connected - ID:', newSocket.id);
      setIsConnected(true);
    });

    newSocket.on('disconnect', (reason) => {
      console.log('Socket disconnected - Reason:', reason);
      // Log additional details about the disconnection
      console.log('Socket was connected:', newSocket.connected);
      console.log('Socket reconnection attempts:', newSocket.io.reconnectionAttempts);
      console.log('Socket backoff delay:', newSocket.io.backoff.duration);
      setIsConnected(false);
    });

    newSocket.on('connect_error', (error) => {
      console.error('Socket connection error:', error.message);
      console.log('Connection error details:', {
        type: error.type,
        description: error.description,
        context: error.context
      });
      setIsConnected(false);
    });

    // Add more event listeners for debugging
    newSocket.on('reconnect_attempt', (attemptNumber) => {
      console.log(`Socket reconnection attempt #${attemptNumber}`);
    });

    newSocket.on('reconnect', (attemptNumber) => {
      console.log(`Socket reconnected after ${attemptNumber} attempts`);
      setIsConnected(true);
    });

    newSocket.on('reconnect_error', (error) => {
      console.error('Socket reconnection error:', error);
    });

    newSocket.on('reconnect_failed', () => {
      console.error('Socket reconnection failed after all attempts');
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

export const useSocket = (): SocketContextType => {
  const context = useContext(SocketContext);
  if (context === undefined) {
    throw new Error('useSocket must be used within a SocketProvider');
  }
  return context;
};
