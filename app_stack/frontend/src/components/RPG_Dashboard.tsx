import React, { useState, useEffect } from 'react';
import { Responsive, WidthProvider } from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';
import '../styles/RPG_Dashboard.css';

// Import widgets
import PlayerStatsWidget from './widgets/PlayerStatsWidget';
import EnvironmentWidget from './widgets/EnvironmentWidget';
import ActionResultsWidget from './widgets/ActionResultsWidget';
import DungeonMasterWidget from './widgets/DungeonMasterWidget';
import AgentDebugWidget from './widgets/AgentDebugWidget';
import ConnectionStatusWidget from './widgets/ConnectionStatusWidget';

// Import settings panel
import SettingsPanel from './SettingsPanel';
import { useTheme } from '../context/ThemeContext';
import { useSocket } from '../context/SocketContext';
import { useWidgets } from '../context/WidgetContext';

const ResponsiveGridLayout = WidthProvider(Responsive);

interface WidgetVisibility {
  playerStats: boolean;
  environment: boolean;
  actionResults: boolean;
  dungeonMaster: boolean;
  agentDebug: boolean;
  connectionStatus: boolean;
}

const RPG_Dashboard: React.FC = () => {
  const { theme } = useTheme();
  const { socket, isConnected } = useSocket();
  const { activeWidgets, addWidget, removeWidget } = useWidgets();
  const [layouts, setLayouts] = useState<any>(null);
  const [isSettingsOpen, setIsSettingsOpen] = useState<boolean>(false);
  const [widgetVisibility, setWidgetVisibility] = useState<WidgetVisibility>({
    playerStats: true,
    environment: true,
    actionResults: true,
    dungeonMaster: true,
    agentDebug: true,
    connectionStatus: true,
  });

  // Load layouts and widget visibility from localStorage and server on mount
  useEffect(() => {
    // First try to load from localStorage as a fallback
    const savedLayouts = localStorage.getItem('rpgerDashboardLayout');
    if (savedLayouts) {
      try {
        setLayouts(JSON.parse(savedLayouts));
      } catch (error) {
        console.error('Error loading saved layouts from localStorage:', error);
        setLayouts(defaultLayouts);
      }
    } else {
      setLayouts(defaultLayouts);
    }

    const savedVisibility = localStorage.getItem('rpgerWidgetVisibility');
    if (savedVisibility) {
      try {
        setWidgetVisibility(JSON.parse(savedVisibility));
      } catch (error) {
        console.error('Error loading saved widget visibility from localStorage:', error);
      }
    }

    // If connected to socket, request dashboard layout from server
    if (socket && isConnected) {
      console.log('Requesting dashboard layout from server');
      socket.emit('dashboard:request');

      // Listen for dashboard updates from server
      socket.on('dashboard:update', (serverLayouts) => {
        console.log('Received dashboard layout from server:', serverLayouts);
        if (serverLayouts && Object.keys(serverLayouts).length > 0) {
          setLayouts(serverLayouts);
          localStorage.setItem('rpgerDashboardLayout', JSON.stringify(serverLayouts));
        }
      });

      return () => {
        socket.off('dashboard:update');
      };
    }
  }, [socket, isConnected]);

  // Default layouts for different breakpoints
  const defaultLayouts = {
    lg: [
      { i: 'playerStats', x: 0, y: 0, w: 6, h: 8, minW: 3, minH: 4 },
      { i: 'environment', x: 6, y: 0, w: 6, h: 4, minW: 3, minH: 3 },
      { i: 'actionResults', x: 6, y: 4, w: 6, h: 4, minW: 3, minH: 3 },
      { i: 'dungeonMaster', x: 0, y: 8, w: 6, h: 6, minW: 3, minH: 4 },
      { i: 'agentDebug', x: 6, y: 8, w: 6, h: 6, minW: 3, minH: 4 },
      { i: 'connectionStatus', x: 0, y: 14, w: 4, h: 4, minW: 3, minH: 3 },
    ],
    md: [
      { i: 'playerStats', x: 0, y: 0, w: 6, h: 8, minW: 3, minH: 4 },
      { i: 'environment', x: 6, y: 0, w: 6, h: 4, minW: 3, minH: 3 },
      { i: 'actionResults', x: 6, y: 4, w: 6, h: 4, minW: 3, minH: 3 },
      { i: 'dungeonMaster', x: 0, y: 8, w: 6, h: 6, minW: 3, minH: 4 },
      { i: 'agentDebug', x: 6, y: 8, w: 6, h: 6, minW: 3, minH: 4 },
      { i: 'connectionStatus', x: 0, y: 14, w: 4, h: 4, minW: 3, minH: 3 },
    ],
    sm: [
      { i: 'playerStats', x: 0, y: 0, w: 6, h: 6, minW: 3, minH: 4 },
      { i: 'environment', x: 0, y: 6, w: 6, h: 4, minW: 3, minH: 3 },
      { i: 'actionResults', x: 0, y: 10, w: 6, h: 4, minW: 3, minH: 3 },
      { i: 'dungeonMaster', x: 0, y: 14, w: 6, h: 6, minW: 3, minH: 4 },
      { i: 'agentDebug', x: 0, y: 20, w: 6, h: 6, minW: 3, minH: 4 },
      { i: 'connectionStatus', x: 0, y: 26, w: 6, h: 4, minW: 3, minH: 3 },
    ],
  };

  // Save layout changes to localStorage and server
  const handleLayoutChange = (currentLayout: any, allLayouts: any) => {
    // Save to localStorage
    localStorage.setItem('rpgerDashboardLayout', JSON.stringify(allLayouts));
    setLayouts(allLayouts);

    // Sync with server if connected
    if (socket && isConnected) {
      console.log('Syncing layout changes with server');
      socket.emit('dashboard:layoutChange', allLayouts);

      // Also sync active widgets
      const activeWidgetIds = currentLayout.map((item: any) => item.i);
      socket.emit('widgets:sync', {
        activeWidgets: activeWidgetIds,
        configs: {} // We'll handle configs separately
      });
    }
  };

  // Toggle settings panel
  const toggleSettings = () => {
    setIsSettingsOpen(!isSettingsOpen);
  };

  // Apply settings
  const handleApplySettings = (settings: any) => {
    console.log("Applying settings:", settings);

    // Check if settings has the expected structure
    if (settings && settings.widgets) {
      // Update widget visibility
      const newWidgetVisibility = {
        playerStats: settings.widgets.playerStats,
        environment: settings.widgets.environment,
        actionResults: settings.widgets.actionResults,
        dungeonMaster: settings.widgets.dungeonMaster,
        agentDebug: settings.widgets.agentDebug,
        connectionStatus: settings.widgets.connectionStatus ?? true,
      };

      setWidgetVisibility(newWidgetVisibility);

      // Save widget visibility to localStorage
      localStorage.setItem('rpgerWidgetVisibility', JSON.stringify(newWidgetVisibility));

      // Sync active widgets with server if connected
      if (socket && isConnected) {
        const activeWidgetIds = Object.entries(newWidgetVisibility)
          .filter(([_, isVisible]) => isVisible)
          .map(([widgetId]) => widgetId);

        socket.emit('widgets:sync', {
          activeWidgets: activeWidgetIds,
          configs: {} // We'll handle configs separately
        });
      }
    } else {
      console.error("Settings object is missing the widgets property:", settings);
    }

    // Apply theme settings if available
    if (settings && settings.theme) {
      const root = document.documentElement;

      // Helper function to convert hex to rgb
      const hexToRgb = (hex: string): string => {
        // Remove the # if present
        hex = hex.replace('#', '');

        // Parse the hex values
        const r = parseInt(hex.substring(0, 2), 16);
        const g = parseInt(hex.substring(2, 4), 16);
        const b = parseInt(hex.substring(4, 6), 16);

        return `${r}, ${g}, ${b}`;
      };

      // Set color variables
      root.style.setProperty('--primary-color', settings.theme.primaryColor);
      root.style.setProperty('--primary-color-rgb', hexToRgb(settings.theme.primaryColor));

      root.style.setProperty('--secondary-color', settings.theme.secondaryColor);
      root.style.setProperty('--secondary-color-rgb', hexToRgb(settings.theme.secondaryColor));

      root.style.setProperty('--background-color', settings.theme.backgroundColor);
      root.style.setProperty('--background-color-rgb', hexToRgb(settings.theme.backgroundColor));

      root.style.setProperty('--text-color', settings.theme.textColor);
      root.style.setProperty('--text-color-rgb', hexToRgb(settings.theme.textColor));

      root.style.setProperty('--font-family', settings.theme.fontFamily);

      // Apply font size
      const fontSizeMap: Record<string, string> = {
        'small': '14px',
        'medium': '16px',
        'large': '18px',
        'x-large': '20px',
      };
      root.style.setProperty('--font-size', fontSizeMap[settings.theme.fontSize] || '16px');
    }

    // Apply animation settings if available
    if (settings && settings.animation) {
      const animationSpeedMap: Record<string, string> = {
        'slow': '0.5s',
        'medium': '0.3s',
        'fast': '0.1s',
      };
      const root = document.documentElement;
      root.style.setProperty('--animation-speed', animationSpeedMap[settings.animation.speed] || '0.3s');
      root.style.setProperty('--animations-enabled', settings.animation.enabled ? '1' : '0');
    }
  };

  if (!layouts) {
    return <div>Loading dashboard...</div>;
  }

  return (
    <div className={`rpg-dashboard ${theme} fullscreen-dashboard`}>
      {/* Translucent settings button in top right */}
      <button className="translucent-settings-button" onClick={toggleSettings}>
        <span className="settings-icon">⚙</span>
        <div className={`connection-indicator ${isConnected ? 'connected' : 'disconnected'}`} data-connected={isConnected.toString()} />
      </button>

      {/* Settings panel */}
      <SettingsPanel
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
        onApplySettings={handleApplySettings}
      />

      {/* Grid layout */}
      <ResponsiveGridLayout
        className="layout"
        layouts={layouts}
        breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
        cols={{ lg: 12, md: 12, sm: 6, xs: 4, xxs: 2 }}
        rowHeight={30}
        onLayoutChange={handleLayoutChange}
        isDraggable
        isResizable
        margin={[10, 10]}
      >
        {/* Player Stats Widget */}
        {widgetVisibility.playerStats && (
          <div key="playerStats">
            <PlayerStatsWidget />
          </div>
        )}

        {/* Environment Widget */}
        {widgetVisibility.environment && (
          <div key="environment">
            <EnvironmentWidget />
          </div>
        )}

        {/* Action Results Widget */}
        {widgetVisibility.actionResults && (
          <div key="actionResults">
            <ActionResultsWidget />
          </div>
        )}

        {/* Dungeon Master Widget */}
        {widgetVisibility.dungeonMaster && (
          <div key="dungeonMaster">
            <DungeonMasterWidget />
          </div>
        )}

        {/* Agent Debug Widget */}
        {widgetVisibility.agentDebug && (
          <div key="agentDebug">
            <AgentDebugWidget />
          </div>
        )}

        {/* Connection Status Widget */}
        {widgetVisibility.connectionStatus && (
          <div key="connectionStatus">
            <ConnectionStatusWidget />
          </div>
        )}
      </ResponsiveGridLayout>
    </div>
  );
};

export default RPG_Dashboard;
