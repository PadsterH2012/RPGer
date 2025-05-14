# Widget Context

## Overview

The Widget Context provides a centralized way to manage widgets throughout the RPGer application. It handles widget registration, activation, configuration, and synchronization with the server.

## Key Components

- **WidgetContext**: React context that provides widget-related functionality
- **WidgetProvider**: Provider component that manages widget state
- **useWidgets**: Custom hook for consuming the Widget context

## Technical Implementation

### WidgetContext

The WidgetContext is a React context that provides the following values:

- `widgets`: Array of available widget registrations
- `activeWidgets`: Array of active widget IDs
- `addWidget`: Function to add a widget
- `removeWidget`: Function to remove a widget
- `updateWidgetConfig`: Function to update a widget's configuration
- `getWidgetConfig`: Function to get a widget's configuration
- `isWidgetActive`: Function to check if a widget is active

```typescript
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
```

### WidgetProvider

The WidgetProvider is a React component that manages widget state and provides the context values to its children:

```typescript
export const WidgetProvider: React.FC<WidgetProviderProps> = ({ children }) => {
  const { socket, isConnected } = useSocket();
  const [widgets, setWidgets] = useState<WidgetRegistration[]>([]);
  const [activeWidgets, setActiveWidgets] = useState<string[]>([]);
  const [widgetConfigs, setWidgetConfigs] = useState<Record<string, WidgetConfig>>({});
  
  // Load available widgets from registry
  useEffect(() => {
    setWidgets(widgetRegistry.getWidgets());
  }, []);
  
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
```

### useWidgets Hook

The useWidgets hook provides a convenient way to access the Widget context:

```typescript
export const useWidgets = (): WidgetContextProps => {
  const context = useContext(WidgetContext);
  if (context === undefined) {
    throw new Error('useWidgets must be used within a WidgetProvider');
  }
  return context;
};
```

## Widget Types and Interfaces

The Widget context uses several TypeScript interfaces to define widget-related data:

```typescript
// Widget metadata
export interface WidgetMetadata extends WidgetSizeConstraints {
  id: string;
  name: string;
  description: string;
  category: WidgetCategory;
  icon?: string;
  version: string;
  author?: string;
  defaultSize: {
    w: number;
    h: number;
  };
}

// Widget category
export enum WidgetCategory {
  GAME = 'game',
  CHARACTER = 'character',
  UTILITY = 'utility',
  SYSTEM = 'system',
  CUSTOM = 'custom',
}

// Widget configuration options
export interface WidgetConfig {
  [key: string]: any;
}

// Widget registration
export interface WidgetRegistration {
  metadata: WidgetMetadata;
  component: React.ComponentType<WidgetProps>;
  defaultConfig?: WidgetConfig;
}
```

## Socket.IO Integration

The Widget context integrates with Socket.IO to synchronize widget state with the server:

### Events Sent to Server

- `widgets:sync`: Synchronize active widgets and their configurations
- `widgets:add`: Add a new widget
- `widgets:remove`: Remove a widget
- `widgets:updateConfig`: Update a widget's configuration

### Events Received from Server

- `widgets:update`: Update widget state from server
- `widget:dataUpdate`: Update widget data from server

## Usage

### Setting Up the Provider

Wrap your application or component tree with the WidgetProvider:

```jsx
import { WidgetProvider } from './context/WidgetContext';

function App() {
  return (
    <SocketProvider>
      <WidgetProvider>
        <YourComponent />
      </WidgetProvider>
    </SocketProvider>
  );
}
```

### Using the Hook in Components

Use the useWidgets hook to access widget functionality in your components:

```jsx
import { useWidgets } from './context/WidgetContext';

function YourComponent() {
  const { activeWidgets, addWidget, removeWidget, updateWidgetConfig } = useWidgets();

  const handleAddWidget = (widgetId) => {
    addWidget(widgetId, { /* initial config */ });
  };

  const handleRemoveWidget = (widgetId) => {
    removeWidget(widgetId);
  };

  const handleUpdateConfig = (widgetId, config) => {
    updateWidgetConfig(widgetId, config);
  };

  return (
    <div>
      <h2>Active Widgets</h2>
      <ul>
        {activeWidgets.map(widgetId => (
          <li key={widgetId}>
            {widgetId}
            <button onClick={() => handleRemoveWidget(widgetId)}>Remove</button>
          </li>
        ))}
      </ul>
      <button onClick={() => handleAddWidget('new-widget')}>Add Widget</button>
    </div>
  );
}
```

## Dependencies

- react: For React context and hooks
- socket.io-client: For Socket.IO client functionality
- widgetRegistry: For registering and retrieving available widgets
