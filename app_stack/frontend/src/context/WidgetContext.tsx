/**
 * Widget Context
 * 
 * Provides widget-related functionality throughout the application.
 */

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useSocket } from './SocketContext';
import widgetRegistry from '../services/WidgetRegistry';
import { 
  WidgetRegistration, 
  WidgetMetadata, 
  WidgetEventType, 
  WidgetEvent,
  WidgetConfig
} from '../types/widget';

interface WidgetContextProps {
  widgets: WidgetRegistration[];
  activeWidgets: string[];
  addWidget: (widgetId: string, initialConfig?: WidgetConfig) => void;
  removeWidget: (widgetId: string) => void;
  updateWidgetConfig: (widgetId: string, config: WidgetConfig) => void;
  getWidgetConfig: (widgetId: string) => WidgetConfig | undefined;
  isWidgetActive: (widgetId: string) => boolean;
}

const WidgetContext = createContext<WidgetContextProps>({
  widgets: [],
  activeWidgets: [],
  addWidget: () => {},
  removeWidget: () => {},
  updateWidgetConfig: () => {},
  getWidgetConfig: () => undefined,
  isWidgetActive: () => false,
});

interface WidgetProviderProps {
  children: ReactNode;
}

export const WidgetProvider: React.FC<WidgetProviderProps> = ({ children }) => {
  const { socket, isConnected } = useSocket();
  const [widgets, setWidgets] = useState<WidgetRegistration[]>([]);
  const [activeWidgets, setActiveWidgets] = useState<string[]>([]);
  const [widgetConfigs, setWidgetConfigs] = useState<Record<string, WidgetConfig>>({});
  
  // Load widgets from registry
  useEffect(() => {
    const updateWidgets = () => {
      setWidgets(widgetRegistry.getAllWidgets());
    };
    
    // Initial load
    updateWidgets();
    
    // Listen for widget registry changes
    const handleWidgetInit = (event: WidgetEvent) => {
      updateWidgets();
    };
    
    const handleWidgetDestroy = (event: WidgetEvent) => {
      updateWidgets();
      // Remove from active widgets if present
      setActiveWidgets(prev => prev.filter(id => id !== event.widgetId));
    };
    
    widgetRegistry.addEventListener(WidgetEventType.INIT, handleWidgetInit);
    widgetRegistry.addEventListener(WidgetEventType.DESTROY, handleWidgetDestroy);
    
    return () => {
      widgetRegistry.removeEventListener(WidgetEventType.INIT, handleWidgetInit);
      widgetRegistry.removeEventListener(WidgetEventType.DESTROY, handleWidgetDestroy);
    };
  }, []);
  
  // Load active widgets and configs from localStorage
  useEffect(() => {
    try {
      const savedActiveWidgets = localStorage.getItem('activeWidgets');
      if (savedActiveWidgets) {
        setActiveWidgets(JSON.parse(savedActiveWidgets));
      }
      
      const savedWidgetConfigs = localStorage.getItem('widgetConfigs');
      if (savedWidgetConfigs) {
        setWidgetConfigs(JSON.parse(savedWidgetConfigs));
      }
    } catch (error) {
      console.error('Error loading widget data from localStorage:', error);
    }
  }, []);
  
  // Save active widgets and configs to localStorage when they change
  useEffect(() => {
    try {
      localStorage.setItem('activeWidgets', JSON.stringify(activeWidgets));
    } catch (error) {
      console.error('Error saving active widgets to localStorage:', error);
    }
  }, [activeWidgets]);
  
  useEffect(() => {
    try {
      localStorage.setItem('widgetConfigs', JSON.stringify(widgetConfigs));
    } catch (error) {
      console.error('Error saving widget configs to localStorage:', error);
    }
  }, [widgetConfigs]);
  
  // Socket.IO integration for widget sync
  useEffect(() => {
    if (socket && isConnected) {
      // Listen for widget updates from server
      socket.on('widgets:update', (data: { activeWidgets: string[], configs: Record<string, WidgetConfig> }) => {
        if (data.activeWidgets) {
          setActiveWidgets(data.activeWidgets);
        }
        
        if (data.configs) {
          setWidgetConfigs(prev => ({
            ...prev,
            ...data.configs
          }));
        }
      });
      
      // Send current widget state to server
      socket.emit('widgets:sync', {
        activeWidgets,
        configs: widgetConfigs
      });
      
      return () => {
        socket.off('widgets:update');
      };
    }
  }, [socket, isConnected, activeWidgets, widgetConfigs]);
  
  const addWidget = (widgetId: string, initialConfig?: WidgetConfig) => {
    if (!activeWidgets.includes(widgetId)) {
      setActiveWidgets(prev => [...prev, widgetId]);
      
      if (initialConfig) {
        setWidgetConfigs(prev => ({
          ...prev,
          [widgetId]: initialConfig
        }));
      }
      
      // Sync with server
      if (socket && isConnected) {
        socket.emit('widgets:add', {
          widgetId,
          config: initialConfig
        });
      }
    }
  };
  
  const removeWidget = (widgetId: string) => {
    setActiveWidgets(prev => prev.filter(id => id !== widgetId));
    
    // Sync with server
    if (socket && isConnected) {
      socket.emit('widgets:remove', {
        widgetId
      });
    }
  };
  
  const updateWidgetConfig = (widgetId: string, config: WidgetConfig) => {
    setWidgetConfigs(prev => ({
      ...prev,
      [widgetId]: {
        ...prev[widgetId],
        ...config
      }
    }));
    
    // Update in registry
    widgetRegistry.updateWidgetConfig(widgetId, config);
    
    // Sync with server
    if (socket && isConnected) {
      socket.emit('widgets:updateConfig', {
        widgetId,
        config
      });
    }
  };
  
  const getWidgetConfig = (widgetId: string): WidgetConfig | undefined => {
    return widgetConfigs[widgetId];
  };
  
  const isWidgetActive = (widgetId: string): boolean => {
    return activeWidgets.includes(widgetId);
  };
  
  return (
    <WidgetContext.Provider
      value={{
        widgets,
        activeWidgets,
        addWidget,
        removeWidget,
        updateWidgetConfig,
        getWidgetConfig,
        isWidgetActive
      }}
    >
      {children}
    </WidgetContext.Provider>
  );
};

export const useWidgets = () => useContext(WidgetContext);
