/**
 * ConnectionStatusIndicator Component
 *
 * A reusable component that displays connection status indicators for various services.
 * Can be added to any widget to show connection status to backend, MongoDB, Redis, etc.
 */

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useSocket } from '../../context/SocketContext';
import api from '../../services/api';

// Connection status types
export type ConnectionState = 'connected' | 'disconnected' | 'connecting';

// Services that can be monitored
export type ServiceType = 'backend' | 'mongodb' | 'redis' | 'chroma';

interface ConnectionStatusIndicatorProps {
  services: ServiceType[];
  showLabels?: boolean;
  size?: 'small' | 'medium' | 'large';
  refreshInterval?: number; // in milliseconds
  horizontal?: boolean;
}

// Container for the indicators
const IndicatorsContainer = styled.div<{ horizontal: boolean }>`
  display: flex;
  flex-direction: ${props => props.horizontal ? 'row' : 'column'};
  gap: 4px;
  align-items: center;
`;

// Individual indicator container
const IndicatorContainer = styled.div<{ size: string }>`
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: ${props =>
    props.size === 'small' ? '10px' :
    props.size === 'large' ? '14px' : '12px'
  };
`;

// Status dot
const StatusDot = styled.div<{ status: ConnectionState, size: string }>`
  width: ${props =>
    props.size === 'small' ? '6px' :
    props.size === 'large' ? '10px' : '8px'
  };
  height: ${props =>
    props.size === 'small' ? '6px' :
    props.size === 'large' ? '10px' : '8px'
  };
  border-radius: 50%;
  background-color: ${props =>
    props.status === 'connected' ? '#10b981' : // Green
    props.status === 'disconnected' ? '#ef4444' : // Red
    '#f59e0b' // Amber for connecting
  };
  transition: background-color 0.3s ease;
`;

// Service label
const ServiceLabel = styled.span<{ size: string }>`
  color: #6b7280;
  font-size: ${props =>
    props.size === 'small' ? '10px' :
    props.size === 'large' ? '14px' : '12px'
  };
  white-space: nowrap;
`;

const ConnectionStatusIndicator: React.FC<ConnectionStatusIndicatorProps> = ({
  services,
  showLabels = true,
  size = 'medium',
  refreshInterval = 30000, // Default to 30 seconds
  horizontal = false
}) => {
  const { isConnected: socketConnected } = useSocket();
  const [status, setStatus] = useState<Record<ServiceType, ConnectionState>>({
    backend: socketConnected ? 'connected' : 'disconnected',
    mongodb: 'connecting',
    redis: 'connecting',
    chroma: 'connecting'
  });
  const [isChecking, setIsChecking] = useState<boolean>(false);

  // Function to check connections
  const checkConnections = async () => {
    if (isChecking) return;

    setIsChecking(true);

    // Update backend status from socket context
    setStatus(prev => ({
      ...prev,
      backend: socketConnected ? 'connected' : 'disconnected'
    }));

    // Only check other services if they're requested
    const needsApiCheck = services.some(service => service !== 'backend');

    if (needsApiCheck) {
      try {
        // Get the API URL from environment variables or use default
        let apiBaseUrl = import.meta.env.VITE_API_URL || 'http://localhost:5002';

        // If we're accessing from a different machine, use the server's IP address
        if (typeof window !== 'undefined' && window.location.hostname !== 'localhost' && apiBaseUrl.includes('localhost')) {
          // Try to use the current window location's hostname instead of localhost
          const serverHostname = window.location.hostname;
          apiBaseUrl = apiBaseUrl.replace('localhost', serverHostname);
          console.log('ConnectionStatusIndicator: Adjusted API URL:', apiBaseUrl);
        }

        // Use direct fetch with more robust error handling
        const apiUrl = `${apiBaseUrl}/api/status`;
        console.log('ConnectionStatusIndicator: Fetching status from', apiUrl);

        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

        const response = await fetch(apiUrl, {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
            'Cache-Control': 'no-cache'
          },
          credentials: 'omit',
          mode: 'cors',
          signal: controller.signal
        });

        clearTimeout(timeoutId);

        if (response.status === 200) {
          const data = await response.json();
          console.log('ConnectionStatusIndicator: Status response:', data);

          // Update status based on API response
          const newStatus = { ...status };

          if (services.includes('mongodb') && data.mongodb) {
            // Check if MongoDB is connected - use the explicit connected flag
            const isConnected = data.mongodb.connected;

            // Log detailed MongoDB status
            console.log('ConnectionStatusIndicator: MongoDB status details:', {
              connected: isConnected,
              collections: data.mongodb.collections || 0,
              databaseName: data.mongodb.databaseName || '',
              collectionNames: data.mongodb.collectionNames || []
            });

            // Set status based on the connected flag only for consistency
            newStatus.mongodb = isConnected ? 'connected' : 'disconnected';
            console.log(`ConnectionStatusIndicator: Setting MongoDB status to ${newStatus.mongodb}`);
          }

          if (services.includes('redis') && data.redis) {
            // Check if Redis is connected - use the explicit connected flag
            const isConnected = data.redis.connected;

            // Log detailed Redis status
            console.log('ConnectionStatusIndicator: Redis status details:', {
              connected: isConnected,
              usedMemory: data.redis.usedMemory || '0 MB',
              totalKeys: data.redis.totalKeys || 0,
              uptime: data.redis.uptime || 0
            });

            // Set status based on the connected flag only for consistency
            newStatus.redis = isConnected ? 'connected' : 'disconnected';
            console.log(`ConnectionStatusIndicator: Setting Redis status to ${newStatus.redis}`);
          }

          if (services.includes('chroma') && data.chroma) {
            // Check if Chroma is connected - use the explicit connected flag
            const isConnected = data.chroma.connected;

            // Log detailed Chroma status
            console.log('ConnectionStatusIndicator: Chroma status details:', {
              connected: isConnected,
              collections: data.chroma.collections || 0,
              embeddings: data.chroma.embeddings || 0,
              version: data.chroma.version || ''
            });

            // Set status based on the connected flag only for consistency
            newStatus.chroma = isConnected ? 'connected' : 'disconnected';
            console.log(`ConnectionStatusIndicator: Setting Chroma status to ${newStatus.chroma}`);
          }

          setStatus(newStatus);
        } else {
          throw new Error(`API returned status ${response.status}`);
        }
      } catch (error) {
        console.error('Error checking service connections:', error);

        // Set all services to disconnected on error
        const newStatus = { ...status };
        services.forEach(service => {
          if (service !== 'backend') {
            newStatus[service] = 'disconnected';
          }
        });

        setStatus(newStatus);
      }
    }

    setIsChecking(false);
  };

  // Check connections on mount and when socket connection changes
  useEffect(() => {
    console.log('ConnectionStatusIndicator: Socket connection changed, checking connections');
    checkConnections();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [socketConnected]);

  // Set up periodic checks
  useEffect(() => {
    console.log(`ConnectionStatusIndicator: Setting up periodic checks every ${refreshInterval}ms`);

    // Check immediately on mount
    checkConnections();

    // Then set up interval
    const intervalId = setInterval(() => {
      console.log('ConnectionStatusIndicator: Running periodic connection check');
      checkConnections();
    }, refreshInterval);

    return () => {
      console.log('ConnectionStatusIndicator: Clearing interval');
      clearInterval(intervalId);
    };
  }, [refreshInterval]);

  // Get service display name
  const getServiceDisplayName = (service: ServiceType): string => {
    switch (service) {
      case 'backend':
        return 'Backend';
      case 'mongodb':
        return 'MongoDB';
      case 'redis':
        return 'Redis';
      case 'chroma':
        return 'Chroma';
      default:
        return service;
    }
  };

  return (
    <IndicatorsContainer horizontal={horizontal}>
      {services.map(service => (
        <IndicatorContainer key={service} size={size}>
          <StatusDot status={status[service]} size={size} />
          {showLabels && (
            <ServiceLabel size={size}>
              {getServiceDisplayName(service)}
            </ServiceLabel>
          )}
        </IndicatorContainer>
      ))}
    </IndicatorsContainer>
  );
};

export default ConnectionStatusIndicator;
