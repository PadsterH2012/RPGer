import React, { useState, useEffect } from 'react';
import '../../styles/widgets/ConnectionStatusWidget.css';

// Connection status types: connected, disconnected, connecting
type ConnectionState = 'connected' | 'disconnected' | 'connecting';

interface ConnectionStatus {
  mongodb: ConnectionState;
  redis: ConnectionState;
  chroma: ConnectionState;
  socketio: ConnectionState;
}

interface ServiceStats {
  mongoDbCollections: number;
  mongoDbName: string;
  mongoDbSize: string;
  redisUsage: string;
  redisKeys: number;
  chromaCollections: number;
  chromaEmbeddings: number;
  chromaVersion: string;
}

// API response interface from Flask-SocketIO server
interface FlaskStatusResponse {
  mongodb: {
    connected: boolean;
    collections: number;
    databaseName: string;
    databaseSize: string;
  };
  redis: {
    connected: boolean;
    usedMemory: string;
    totalKeys: number;
    uptime: number;
  };
  chroma: {
    connected: boolean;
    collections: number;
    embeddings: number;
    version: string;
  };
  socketio: {
    connected: boolean;
    clients: number;
  };
}

const ConnectionStatusWidget: React.FC = () => {
  const [status, setStatus] = useState<ConnectionStatus>({
    mongodb: 'disconnected',
    redis: 'disconnected',
    chroma: 'disconnected',
    socketio: 'disconnected'
  });

  const [stats, setStats] = useState<ServiceStats>({
    mongoDbCollections: 0,
    mongoDbName: '',
    mongoDbSize: '0 MB',
    redisUsage: '0 MB',
    redisKeys: 0,
    chromaCollections: 0,
    chromaEmbeddings: 0,
    chromaVersion: ''
  });

  const [lastChecked, setLastChecked] = useState<string>('');
  const [isChecking, setIsChecking] = useState<boolean>(false);

  // Function to check connections
  const checkConnections = async () => {
    console.log('Checking connections...');
    // Set checking state
    setIsChecking(true);

    // Set all services to "connecting" state
    setStatus({
      mongodb: 'connecting',
      redis: 'connecting',
      chroma: 'connecting',
      socketio: 'connecting'
    });

    try {
      // Make API call to check all services directly from Flask-SocketIO server
      console.log('Fetching status from Flask-SocketIO server...');
      const response = await fetch('http://localhost:5002/api/status');

      if (response.status === 200) {
        const data = await response.json() as FlaskStatusResponse;
        console.log('Received status data:', data);

        // Update connection status
        setStatus({
          mongodb: data.mongodb.connected ? 'connected' : 'disconnected',
          redis: data.redis.connected ? 'connected' : 'disconnected',
          chroma: data.chroma.connected ? 'connected' : 'disconnected',
          socketio: data.socketio.connected ? 'connected' : 'disconnected'
        });

        // Update stats
        setStats({
          mongoDbCollections: data.mongodb.collections,
          mongoDbName: data.mongodb.databaseName,
          mongoDbSize: data.mongodb.databaseSize,
          redisUsage: data.redis.usedMemory,
          redisKeys: data.redis.totalKeys,
          chromaCollections: data.chroma.collections,
          chromaEmbeddings: data.chroma.embeddings,
          chromaVersion: data.chroma.version
        });
      } else {
        console.error(`API returned status ${response.status}`);
        throw new Error(`API returned status ${response.status}`);
      }

      // Update last checked timestamp
      setLastChecked(new Date().toLocaleTimeString());
    } catch (error) {
      console.error('Error checking connections:', error);

      // Try to check Socket.IO separately even if API fails
      let socketioConnected = false;
      try {
        console.log('Checking Socket.IO status separately...');
        const socketResponse = await fetch('http://localhost:5002/api/socketio-status');
        if (socketResponse.status === 200) {
          const socketData = await socketResponse.json();
          socketioConnected = socketData.status === 'ok';
          console.log('Socket.IO status:', socketioConnected ? 'connected' : 'disconnected');
        }
      } catch (socketError) {
        console.error('Error checking Socket.IO:', socketError);
        socketioConnected = false;
      }

      // Set status with Socket.IO result
      setStatus({
        mongodb: 'disconnected',
        redis: 'disconnected',
        socketio: socketioConnected ? 'connected' : 'disconnected'
      });
    } finally {
      setIsChecking(false);
    }
  };

  // Check connections on component mount
  useEffect(() => {
    // Check immediately on mount
    checkConnections();

    // Check again after 2 seconds (for initial quick feedback)
    const initialCheckTimeout = setTimeout(() => {
      checkConnections();
    }, 2000);

    // Set up periodic checks (every 15 seconds)
    const intervalId = setInterval(checkConnections, 15000);

    // Clean up interval and timeout on component unmount
    return () => {
      clearInterval(intervalId);
      clearTimeout(initialCheckTimeout);
    };
  }, []);

  // Helper function to get status color
  const getStatusColor = (status: ConnectionState): string => {
    switch (status) {
      case 'connected': return 'green';
      case 'disconnected': return 'red';
      case 'connecting': return 'amber';
      default: return 'gray';
    }
  };

  return (
    <div className="widget connection-status-widget">
      <div className="widget-header">
        <h3>Connection Status</h3>
        <button
          className="refresh-button"
          onClick={checkConnections}
          disabled={isChecking}
        >
          {isChecking ? 'Checking...' : 'Refresh'}
        </button>
      </div>
      <div className="widget-content">
        <div className="connection-boxes">
          <div className="connection-box">
            <div className={`status-indicator ${getStatusColor(status.mongodb)}`}>
              <span className="service-name">MongoDB</span>
            </div>
            <div className="service-stats">
              {status.mongodb === 'connected' && (
                <div className="stats-details">
                  <span className="stats-text">Collections: {stats.mongoDbCollections}</span>
                  {stats.mongoDbName && (
                    <span className="stats-text-small">DB: {stats.mongoDbName}</span>
                  )}
                  {stats.mongoDbSize && (
                    <span className="stats-text-small">Size: {stats.mongoDbSize}</span>
                  )}
                </div>
              )}
              {status.mongodb === 'connecting' && (
                <span className="stats-text">Checking...</span>
              )}
            </div>
          </div>

          <div className="connection-box">
            <div className={`status-indicator ${getStatusColor(status.redis)}`}>
              <span className="service-name">Redis</span>
            </div>
            <div className="service-stats">
              {status.redis === 'connected' && (
                <div className="stats-details">
                  <span className="stats-text">Memory: {stats.redisUsage}</span>
                  <span className="stats-text-small">Keys: {stats.redisKeys}</span>
                </div>
              )}
              {status.redis === 'connecting' && (
                <span className="stats-text">Checking...</span>
              )}
            </div>
          </div>

          <div className="connection-box">
            <div className={`status-indicator ${getStatusColor(status.chroma)}`}>
              <span className="service-name">Chroma</span>
            </div>
            <div className="service-stats">
              {status.chroma === 'connected' && (
                <div className="stats-details">
                  <span className="stats-text">Collections: {stats.chromaCollections}</span>
                  <span className="stats-text-small">Embeddings: {stats.chromaEmbeddings}</span>
                  {stats.chromaVersion && (
                    <span className="stats-text-small">Version: {stats.chromaVersion}</span>
                  )}
                </div>
              )}
              {status.chroma === 'connecting' && (
                <span className="stats-text">Checking...</span>
              )}
            </div>
          </div>

          <div className="connection-box">
            <div className={`status-indicator ${getStatusColor(status.socketio)}`}>
              <span className="service-name">SocketIO</span>
            </div>
            <div className="service-stats">
              {status.socketio === 'connected' && (
                <span className="stats-text">Active</span>
              )}
              {status.socketio === 'connecting' && (
                <span className="stats-text">Checking...</span>
              )}
            </div>
          </div>
        </div>

        {lastChecked && (
          <div className="last-checked">
            Last checked: {lastChecked}
          </div>
        )}
      </div>
    </div>
  );
};

export default ConnectionStatusWidget;
