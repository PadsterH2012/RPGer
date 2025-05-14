import React, { useState, useEffect } from 'react';
import GridLayout, { Layout, WidthProvider } from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';
import '../styles/DashboardLayout.css';

// Import widget components
import PlayerStatsWidget from '../components/widgets/PlayerStatsWidget';
import EnvironmentWidget from '../components/widgets/EnvironmentWidget';
import ActionResultsWidget from '../components/widgets/ActionResultsWidget';
import DungeonMasterWidget from '../components/widgets/DungeonMasterWidget';
import AgentDebugWidget from '../components/widgets/AgentDebugWidget';

// Width provider for the grid layout
const ResponsiveGridLayout = WidthProvider(GridLayout);

// Define widget types
export type WidgetType = 
  | 'playerStats' 
  | 'environment' 
  | 'actionResults' 
  | 'dungeonMaster' 
  | 'agentDebug';

// Define widget data
export interface WidgetData {
  id: string;
  type: WidgetType;
  title: string;
  content?: any;
  isVisible: boolean;
}

// Default layout configuration
const defaultLayout: Layout[] = [
  { i: 'playerStats', x: 0, y: 0, w: 1, h: 2, minW: 1, maxW: 3, minH: 2 },
  { i: 'environment', x: 1, y: 0, w: 1, h: 1, minW: 1, maxW: 3, minH: 1 },
  { i: 'actionResults', x: 2, y: 0, w: 1, h: 1, minW: 1, maxW: 3, minH: 1 },
  { i: 'dungeonMaster', x: 0, y: 2, w: 2, h: 1, minW: 1, maxW: 3, minH: 1 },
  { i: 'agentDebug', x: 2, y: 2, w: 1, h: 1, minW: 1, maxW: 3, minH: 1 },
];

// Default widget data
const defaultWidgets: WidgetData[] = [
  { id: 'playerStats', type: 'playerStats', title: 'Player Stats', isVisible: true },
  { id: 'environment', type: 'environment', title: 'Environment', isVisible: true },
  { id: 'actionResults', type: 'actionResults', title: 'Action Results', isVisible: true },
  { id: 'dungeonMaster', type: 'dungeonMaster', title: 'Dungeon Master', isVisible: true },
  { id: 'agentDebug', type: 'agentDebug', title: 'Agent Debug', isVisible: true },
];

// Dashboard layout component
const DashboardLayout: React.FC = () => {
  // State for layout and widgets
  const [layout, setLayout] = useState<Layout[]>(defaultLayout);
  const [widgets, setWidgets] = useState<WidgetData[]>(defaultWidgets);
  
  // Load saved layout from localStorage on component mount
  useEffect(() => {
    const savedLayout = localStorage.getItem('rpgerDashboardLayout');
    const savedWidgets = localStorage.getItem('rpgerDashboardWidgets');
    
    if (savedLayout) {
      try {
        setLayout(JSON.parse(savedLayout));
      } catch (error) {
        console.error('Error loading saved layout:', error);
      }
    }
    
    if (savedWidgets) {
      try {
        setWidgets(JSON.parse(savedWidgets));
      } catch (error) {
        console.error('Error loading saved widgets:', error);
      }
    }
  }, []);
  
  // Save layout to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('rpgerDashboardLayout', JSON.stringify(layout));
  }, [layout]);
  
  // Save widgets to localStorage when they change
  useEffect(() => {
    localStorage.setItem('rpgerDashboardWidgets', JSON.stringify(widgets));
  }, [widgets]);
  
  // Handle layout change
  const handleLayoutChange = (newLayout: Layout[]) => {
    setLayout(newLayout);
  };
  
  // Toggle widget visibility
  const toggleWidgetVisibility = (widgetId: string) => {
    setWidgets(prevWidgets => 
      prevWidgets.map(widget => 
        widget.id === widgetId 
          ? { ...widget, isVisible: !widget.isVisible } 
          : widget
      )
    );
  };
  
  // Reset layout to default
  const resetLayout = () => {
    setLayout(defaultLayout);
    setWidgets(defaultWidgets);
  };
  
  // Render widget based on type
  const renderWidget = (widget: WidgetData) => {
    if (!widget.isVisible) return null;
    
    switch (widget.type) {
      case 'playerStats':
        return <PlayerStatsWidget />;
      case 'environment':
        return <EnvironmentWidget />;
      case 'actionResults':
        return <ActionResultsWidget />;
      case 'dungeonMaster':
        return <DungeonMasterWidget />;
      case 'agentDebug':
        return <AgentDebugWidget />;
      default:
        return <div>Unknown widget type</div>;
    }
  };
  
  return (
    <div className="dashboard-container">
      <div className="dashboard-controls">
        <button onClick={resetLayout} className="reset-button">
          Reset Layout
        </button>
        <div className="widget-toggles">
          {widgets.map(widget => (
            <label key={widget.id} className="widget-toggle">
              <input
                type="checkbox"
                checked={widget.isVisible}
                onChange={() => toggleWidgetVisibility(widget.id)}
              />
              {widget.title}
            </label>
          ))}
        </div>
      </div>
      
      <ResponsiveGridLayout
        className="layout"
        layout={layout}
        cols={3}
        rowHeight={200}
        width={1200}
        onLayoutChange={handleLayoutChange}
        draggableHandle=".widget-header"
        isBounded={true}
      >
        {widgets.map(widget => (
          widget.isVisible && (
            <div key={widget.id} className={`widget-container ${widget.type}-widget`}>
              <div className="widget-header">
                <h3>{widget.title}</h3>
                <button 
                  className="widget-close-button"
                  onClick={() => toggleWidgetVisibility(widget.id)}
                >
                  ×
                </button>
              </div>
              <div className="widget-content">
                {renderWidget(widget)}
              </div>
            </div>
          )
        ))}
      </ResponsiveGridLayout>
    </div>
  );
};

export default DashboardLayout;
