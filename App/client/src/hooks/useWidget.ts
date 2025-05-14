/**
 * useWidget Hook
 * 
 * Custom hook for widget lifecycle management and configuration.
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useSocket } from '../context/SocketContext';
import { useWidgets } from '../context/WidgetContext';
import widgetRegistry from '../services/WidgetRegistry';
import { WidgetProps, WidgetConfig, WidgetEventType } from '../types/widget';

interface UseWidgetOptions {
  defaultConfig?: WidgetConfig;
  onInit?: () => void | Promise<void>;
  onUpdate?: () => void | Promise<void>;
  onDestroy?: () => void | Promise<void>;
  onConfigChange?: (config: WidgetConfig) => void | Promise<void>;
  onDataUpdate?: (data: any) => void | Promise<void>;
}

interface UseWidgetResult {
  config: WidgetConfig;
  updateConfig: (newConfig: Partial<WidgetConfig>) => void;
  isLoading: boolean;
  error: Error | null;
  resetError: () => void;
  sendEvent: (eventType: string, payload?: any) => void;
}

/**
 * Custom hook for widget lifecycle management
 * 
 * @param widgetId Widget ID
 * @param options Widget options
 * @returns Widget state and methods
 */
export const useWidget = (
  widgetId: string,
  options: UseWidgetOptions = {}
): UseWidgetResult => {
  const { socket, isConnected } = useSocket();
  const { getWidgetConfig, updateWidgetConfig } = useWidgets();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const initialized = useRef(false);
  
  // Get config from context or use default
  const savedConfig = getWidgetConfig(widgetId);
  const [config, setConfig] = useState<WidgetConfig>(
    savedConfig || options.defaultConfig || {}
  );
  
  // Initialize widget
  useEffect(() => {
    const init = async () => {
      try {
        setIsLoading(true);
        
        // Call onInit handler if provided
        if (options.onInit && !initialized.current) {
          await options.onInit();
          initialized.current = true;
        }
        
        // Request data from server if connected
        if (socket && isConnected) {
          socket.emit('widget:init', { widgetId });
        }
        
        setIsLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err : new Error(String(err)));
        setIsLoading(false);
      }
    };
    
    init();
    
    // Cleanup on unmount
    return () => {
      if (options.onDestroy) {
        options.onDestroy();
      }
    };
  }, [widgetId, socket, isConnected]);
  
  // Listen for config changes
  useEffect(() => {
    if (savedConfig && JSON.stringify(savedConfig) !== JSON.stringify(config)) {
      setConfig(savedConfig);
      
      // Call onConfigChange handler if provided
      if (options.onConfigChange) {
        options.onConfigChange(savedConfig);
      }
    }
  }, [savedConfig]);
  
  // Listen for data updates from server
  useEffect(() => {
    if (socket && isConnected) {
      const handleDataUpdate = (data: any) => {
        if (data.widgetId === widgetId) {
          // Call onDataUpdate handler if provided
          if (options.onDataUpdate) {
            options.onDataUpdate(data.payload);
          }
        }
      };
      
      socket.on('widget:dataUpdate', handleDataUpdate);
      
      return () => {
        socket.off('widget:dataUpdate', handleDataUpdate);
      };
    }
  }, [socket, isConnected, widgetId]);
  
  // Update config
  const updateConfig = useCallback((newConfig: Partial<WidgetConfig>) => {
    const updatedConfig = {
      ...config,
      ...newConfig
    };
    
    setConfig(updatedConfig);
    updateWidgetConfig(widgetId, updatedConfig);
    
    // Call onConfigChange handler if provided
    if (options.onConfigChange) {
      options.onConfigChange(updatedConfig);
    }
  }, [widgetId, config, updateWidgetConfig]);
  
  // Reset error
  const resetError = useCallback(() => {
    setError(null);
  }, []);
  
  // Send event to server
  const sendEvent = useCallback((eventType: string, payload?: any) => {
    if (socket && isConnected) {
      socket.emit('widget:event', {
        widgetId,
        eventType,
        payload
      });
    }
  }, [socket, isConnected, widgetId]);
  
  return {
    config,
    updateConfig,
    isLoading,
    error,
    resetError,
    sendEvent
  };
};

export default useWidget;
