# RPG Dashboard Component

## Overview

The RPG Dashboard is a core component of the RPGer application that provides a customizable interface for users to arrange and interact with various widgets. It uses React Grid Layout to enable drag-and-drop functionality and resizing of widgets.

## Key Features

- **Responsive Layout**: Adapts to different screen sizes with predefined layouts for large, medium, and small screens
- **Persistent Widget Layouts**: Saves widget positions and sizes across sessions and server restarts
- **Widget Visibility Control**: Allows toggling visibility of individual widgets
- **Theme Support**: Integrates with the application's theming system
- **Real-time Synchronization**: Uses Socket.IO to sync dashboard state with the server

## Technical Implementation

### State Management

The dashboard component manages several pieces of state:
- `layouts`: Stores the positions and dimensions of widgets for different screen sizes
- `widgetVisibility`: Tracks which widgets are currently visible
- `isSettingsOpen`: Controls the visibility of the settings panel

### Persistence Mechanism

The dashboard implements a multi-layered persistence approach:

1. **Client-side Storage**:
   - Uses `localStorage` to save layouts and widget visibility
   - Provides immediate access to saved layouts on page load
   - Serves as a fallback if server connection is unavailable

2. **Server-side Storage**:
   - Syncs layouts with the server via Socket.IO
   - Server stores layouts in MongoDB for long-term persistence
   - Redis caching is used for quick access to frequently used layouts

3. **Synchronization Flow**:
   - On component mount, loads layouts from localStorage first
   - Then requests the latest layout from the server
   - When layouts change, saves to both localStorage and server
   - Server broadcasts changes to other connected clients

### Socket.IO Integration

The dashboard uses the following Socket.IO events:

| Event | Direction | Purpose |
|-------|-----------|---------|
| `dashboard:request` | Client → Server | Request saved dashboard layout |
| `dashboard:update` | Server → Client | Send saved layout to client |
| `dashboard:layoutChange` | Client → Server | Notify server of layout changes |
| `widgets:sync` | Client → Server | Sync active widgets and their configs |

## Code Structure

```jsx
// Key component structure
const RPG_Dashboard: React.FC = () => {
  // Hooks for theme, socket, and widgets
  const { theme } = useTheme();
  const { socket, isConnected } = useSocket();
  const { activeWidgets, addWidget, removeWidget } = useWidgets();
  
  // State management
  const [layouts, setLayouts] = useState<any>(null);
  const [isSettingsOpen, setIsSettingsOpen] = useState<boolean>(false);
  const [widgetVisibility, setWidgetVisibility] = useState<WidgetVisibility>({...});
  
  // Load layouts from localStorage and server
  useEffect(() => {
    // Load from localStorage
    // Request from server if connected
  }, [socket, isConnected]);
  
  // Save layout changes
  const handleLayoutChange = (currentLayout: any, allLayouts: any) => {
    // Save to localStorage
    // Sync with server if connected
  };
  
  // Render grid layout with widgets
  return (
    <div className={`rpg-dashboard ${theme}`}>
      {/* Settings button */}
      {/* Settings panel */}
      <ResponsiveGridLayout
        layouts={layouts}
        onLayoutChange={handleLayoutChange}
        {...layoutProps}
      >
        {/* Widgets */}
      </ResponsiveGridLayout>
    </div>
  );
};
```

## Widget Integration

The dashboard renders the following widgets when they are visible:

- PlayerStatsWidget
- EnvironmentWidget
- ActionResultsWidget
- DungeonMasterWidget
- AgentDebugWidget
- ConnectionStatusWidget

Each widget is wrapped in a grid item with a unique key that corresponds to its position in the layout.

## Settings Panel

The dashboard includes a settings panel that allows users to:

- Toggle widget visibility
- Customize theme settings
- Adjust animation settings

Settings are applied through the `handleApplySettings` function, which updates the widget visibility state and applies theme customizations.

## Usage

To use the RPG Dashboard component:

```jsx
import RPG_Dashboard from './components/RPG_Dashboard';

function App() {
  return (
    <ThemeProvider>
      <SocketProvider>
        <WidgetProvider>
          <RPG_Dashboard />
        </WidgetProvider>
      </SocketProvider>
    </ThemeProvider>
  );
}
```

## Dependencies

- react-grid-layout: For the responsive grid layout system
- socket.io-client: For real-time communication with the server
- ThemeContext: For theme management
- SocketContext: For Socket.IO connection management
- WidgetContext: For widget state management
