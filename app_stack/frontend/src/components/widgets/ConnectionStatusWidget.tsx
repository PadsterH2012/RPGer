import React, { useState, useEffect } from 'react';
import { useTheme } from '../../context/ThemeContext';
import styled from 'styled-components';
import ConnectionStatusIndicator from '../common/ConnectionStatusIndicator';
import '../../styles/widgets/ConnectionStatusWidget.css';

// Widget header
const WidgetHeader = styled.div<{ theme: string }>`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: var(--${props => props.theme}-widget-header-bg);
  border-bottom: 1px solid var(--${props => props.theme}-border);
`;

// Widget title
const WidgetTitle = styled.h3<{ theme: string }>`
  margin: 0;
  color: var(--${props => props.theme}-text-primary);
  font-size: var(--font-size-md);
  font-weight: 600;
`;

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
  mongoDbCollectionNames: string[];
  mongoDbName: string;
  mongoDbSize: string;
  mongoDbMonsterCount: number;
  redisUsage: string;
  redisKeys: number;
  redisKeyTypes: { [key: string]: number };
  chromaCollections: number;
  chromaCollectionNames: string[];
  chromaEmbeddings: number;
  chromaVersion: string;
}

// API response interface from Flask-SocketIO server
interface FlaskStatusResponse {
  mongodb: {
    connected: boolean;
    collections: number;
    collectionNames: string[];
    databaseName: string;
    databaseSize: string;
    monsterCount: number;
  };
  redis: {
    connected: boolean;
    usedMemory: string;
    totalKeys: number;
    keyTypes: { [key: string]: number };
    uptime: number;
  };
  chroma: {
    connected: boolean;
    collections: number;
    collectionNames: string[];
    embeddings: number;
    version: string;
  };
  socketio: {
    connected: boolean;
    clients: number;
  };
}

const ConnectionStatusWidget: React.FC = () => {
  const { theme } = useTheme();
  const [status, setStatus] = useState<ConnectionStatus>({
    mongodb: 'disconnected',
    redis: 'disconnected',
    chroma: 'disconnected',
    socketio: 'disconnected'
  });

  const [stats, setStats] = useState<ServiceStats>({
    mongoDbCollections: 0,
    mongoDbCollectionNames: [],
    mongoDbName: '',
    mongoDbSize: '0 MB',
    mongoDbMonsterCount: 0,
    redisUsage: '0 MB',
    redisKeys: 0,
    redisKeyTypes: {},
    chromaCollections: 0,
    chromaCollectionNames: [],
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
          mongoDbCollectionNames: data.mongodb.collectionNames || [],
          mongoDbName: data.mongodb.databaseName,
          mongoDbSize: data.mongodb.databaseSize,
          mongoDbMonsterCount: data.mongodb.monsterCount || 0,
          redisUsage: data.redis.usedMemory,
          redisKeys: data.redis.totalKeys,
          redisKeyTypes: data.redis.keyTypes || {},
          chromaCollections: data.chroma.collections,
          chromaCollectionNames: data.chroma.collectionNames || [],
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
      <WidgetHeader theme={theme}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <WidgetTitle theme={theme}>Connection Status</WidgetTitle>
          <ConnectionStatusIndicator
            services={['backend']}
            size="small"
            horizontal={true}
            refreshInterval={15000}
          />
        </div>
        <button
          className="refresh-button"
          onClick={checkConnections}
          disabled={isChecking}
        >
          {isChecking ? 'Checking...' : 'Refresh'}
        </button>
      </WidgetHeader>
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
                  {stats.mongoDbMonsterCount > 0 && (
                    <span className="stats-text-small highlight">Monsters: {stats.mongoDbMonsterCount}</span>
                  )}
                  {stats.mongoDbName && (
                    <span className="stats-text-small">DB: {stats.mongoDbName}</span>
                  )}
                  {stats.mongoDbSize && (
                    <span className="stats-text-small">Size: {stats.mongoDbSize}</span>
                  )}
                  {stats.mongoDbCollectionNames && stats.mongoDbCollectionNames.length > 0 && (
                    <div className="collection-details">
                      <span className="stats-text-small collection-title">Collection Names:</span>
                      <div className="collection-list">
                        {stats.mongoDbCollectionNames.map((name, index) => (
                          <span key={index} className="collection-name">{name}</span>
                        ))}
                      </div>
                    </div>
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
                  {Object.keys(stats.redisKeyTypes).length > 0 && (
                    <div className="collection-details">
                      <span className="stats-text-small collection-title">Key Types:</span>
                      <div className="collection-list">
                        {Object.entries(stats.redisKeyTypes).map(([type, count], index) => (
                          <span key={index} className="collection-name">{type}: {count}</span>
                        ))}
                      </div>
                    </div>
                  )}
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
                  {stats.chromaCollectionNames && stats.chromaCollectionNames.length > 0 && (
                    <div className="collection-details">
                      <span className="stats-text-small collection-title">Collection Names:</span>
                      <div className="collection-list">
                        {stats.chromaCollectionNames.map((name, index) => (
                          <span key={index} className="collection-name">{name}</span>
                        ))}
                      </div>
                    </div>
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
