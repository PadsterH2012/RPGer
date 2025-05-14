import React, { useState, useEffect } from 'react';
import { Responsive, WidthProvider } from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';
import '../styles/NewDashboard.css';

// Import widgets
import PlayerStatsWidget from './widgets/PlayerStatsWidget';
import EnvironmentWidget from './widgets/EnvironmentWidget';
import ActionResultsWidget from './widgets/ActionResultsWidget';
import DungeonMasterWidget from './widgets/DungeonMasterWidget';
import AgentDebugWidget from './widgets/AgentDebugWidget';

// Import settings panel
import SettingsPanel from './SettingsPanel';
import { useTheme } from '../context/ThemeContext';

const ResponsiveGridLayout = WidthProvider(Responsive);

interface WidgetVisibility {
  playerStats: boolean;
  environment: boolean;
  actionResults: boolean;
  dungeonMaster: boolean;
  agentDebug: boolean;
}

const NewDashboard: React.FC = () => {
  const { theme } = useTheme();
  const [layouts, setLayouts] = useState<any>(null);
  const [isSettingsOpen, setIsSettingsOpen] = useState<boolean>(false);
  const [widgetVisibility, setWidgetVisibility] = useState<WidgetVisibility>({
    playerStats: true,
    environment: true,
    actionResults: true,
    dungeonMaster: true,
    agentDebug: true,
  });
  const [isConnected, setIsConnected] = useState<boolean>(false);

  // Load layouts and widget visibility from localStorage on mount
  useEffect(() => {
    const savedLayouts = localStorage.getItem('rpgerDashboardLayout');
    if (savedLayouts) {
      try {
        setLayouts(JSON.parse(savedLayouts));
      } catch (error) {
        console.error('Error loading saved layouts:', error);
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
        console.error('Error loading saved widget visibility:', error);
      }
    }

    // Simulate connection status (replace with actual connection logic)
    setTimeout(() => {
      setIsConnected(true);
    }, 1000);
  }, []);

  // Default layouts for different breakpoints
  const defaultLayouts = {
    lg: [
      { i: 'playerStats', x: 0, y: 0, w: 6, h: 8, minW: 3, minH: 4 },
      { i: 'environment', x: 6, y: 0, w: 6, h: 4, minW: 3, minH: 3 },
      { i: 'actionResults', x: 6, y: 4, w: 6, h: 4, minW: 3, minH: 3 },
      { i: 'dungeonMaster', x: 0, y: 8, w: 6, h: 6, minW: 3, minH: 4 },
      { i: 'agentDebug', x: 6, y: 8, w: 6, h: 6, minW: 3, minH: 4 },
    ],
    md: [
      { i: 'playerStats', x: 0, y: 0, w: 6, h: 8, minW: 3, minH: 4 },
      { i: 'environment', x: 6, y: 0, w: 6, h: 4, minW: 3, minH: 3 },
      { i: 'actionResults', x: 6, y: 4, w: 6, h: 4, minW: 3, minH: 3 },
      { i: 'dungeonMaster', x: 0, y: 8, w: 6, h: 6, minW: 3, minH: 4 },
      { i: 'agentDebug', x: 6, y: 8, w: 6, h: 6, minW: 3, minH: 4 },
    ],
    sm: [
      { i: 'playerStats', x: 0, y: 0, w: 6, h: 6, minW: 3, minH: 4 },
      { i: 'environment', x: 0, y: 6, w: 6, h: 4, minW: 3, minH: 3 },
      { i: 'actionResults', x: 0, y: 10, w: 6, h: 4, minW: 3, minH: 3 },
      { i: 'dungeonMaster', x: 0, y: 14, w: 6, h: 6, minW: 3, minH: 4 },
      { i: 'agentDebug', x: 0, y: 20, w: 6, h: 6, minW: 3, minH: 4 },
    ],
  };

  // Save layout changes to localStorage
  const handleLayoutChange = (currentLayout: any, allLayouts: any) => {
    localStorage.setItem('rpgerDashboardLayout', JSON.stringify(allLayouts));
    setLayouts(allLayouts);
  };

  // Toggle settings panel
  const toggleSettings = () => {
    setIsSettingsOpen(!isSettingsOpen);
  };

  // Apply settings
  const handleApplySettings = (settings: any) => {
    // Update widget visibility
    setWidgetVisibility({
      playerStats: settings.layout.showPlayerStats,
      environment: settings.layout.showEnvironment,
      actionResults: settings.layout.showActionResults,
      dungeonMaster: settings.layout.showDungeonMaster,
      agentDebug: settings.layout.showAgentDebug,
    });

    // Apply other settings as needed
    // This could include theme changes, animation settings, etc.
  };

  if (!layouts) {
    return <div>Loading dashboard...</div>;
  }

  return (
    <div className={`new-dashboard ${theme}`}>
      {/* Settings button */}
      <button className="floating-settings-button" onClick={toggleSettings}>
        <span className="settings-icon">⚙</span>
        <div className={`connection-indicator ${isConnected ? 'connected' : 'disconnected'}`} />
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
      </ResponsiveGridLayout>
    </div>
  );
};

export default NewDashboard;
