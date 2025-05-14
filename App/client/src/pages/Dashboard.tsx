import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Responsive, WidthProvider } from 'react-grid-layout';
import 'react-grid-layout/css/styles.css';
import 'react-resizable/css/styles.css';
import { useSocket } from '../context/SocketContext';
import { useTheme } from '../context/ThemeContext';
import { useWidgets } from '../context/WidgetContext';

// Import widget components
import StatsWidget from '../components/widgets/StatsWidget';
import NotesWidget from '../components/widgets/NotesWidget';
import DiceRollerWidget from '../components/widgets/DiceRollerWidget';
import CharacterSheetWidget from '../components/widgets/CharacterSheetWidget';
import TextWidget from '../components/widgets/TextWidget';
import TableWidget from '../components/widgets/TableWidget';
import ClockWidget from '../components/widgets/ClockWidget';
import CountdownWidget from '../components/widgets/CountdownWidget';

// Enable responsive features
const ResponsiveGridLayout = WidthProvider(Responsive);

const DashboardContainer = styled.div`
  height: 100%;
  width: 100%;
`;

const ControlPanel = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
`;

const LayoutControls = styled.div`
  display: flex;
  gap: var(--spacing-sm);
`;

const Button = styled.button`
  background-color: var(--${props => props.theme}-primary);
  color: ${props => props.theme === 'dark' ? 'black' : 'white'};
  border: none;
  padding: var(--spacing-sm) var(--spacing-md);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-size: var(--font-size-sm);
  transition: background-color var(--transition-fast) ease;

  &:hover {
    background-color: var(--${props => props.theme}-primary-variant);
  }
`;

const WidgetSelectorModal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background-color: var(--${props => props.theme}-surface);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-lg);
  width: 80%;
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: var(--shadow-lg);
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-md);
  border-bottom: 1px solid var(--${props => props.theme}-border);
  padding-bottom: var(--spacing-sm);
`;

const ModalTitle = styled.h2`
  margin: 0;
  font-size: var(--font-size-lg);
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: var(--font-size-xl);
  cursor: pointer;
  color: var(--${props => props.theme}-text-secondary);

  &:hover {
    color: var(--${props => props.theme}-text-primary);
  }
`;

const WidgetGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--spacing-md);
`;

const WidgetCard = styled.div`
  background-color: ${props => props.theme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.02)'};
  border: 1px solid var(--${props => props.theme}-border);
  border-radius: var(--border-radius-md);
  padding: var(--spacing-md);
  cursor: pointer;
  transition: all var(--transition-fast) ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-md);
    border-color: var(--${props => props.theme}-primary);
  }
`;

const WidgetIcon = styled.div`
  font-size: var(--font-size-xl);
  margin-bottom: var(--spacing-sm);
  text-align: center;
`;

const WidgetName = styled.div`
  font-weight: 600;
  margin-bottom: var(--spacing-xs);
  text-align: center;
`;

const WidgetDescription = styled.div`
  font-size: var(--font-size-sm);
  color: var(--${props => props.theme}-text-secondary);
  text-align: center;
`;

const WidgetContainer = styled.div`
  background-color: var(--${props => props.theme}-surface);
  border: 1px solid var(--${props => props.theme}-border);
  border-radius: var(--border-radius-md);
  box-shadow: var(--shadow-md);
  overflow: hidden;
`;

const WidgetHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: ${props => props.theme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)'};
  border-bottom: 1px solid var(--${props => props.theme}-border);
`;

const WidgetTitle = styled.h3`
  margin: 0;
  font-size: var(--font-size-md);
  font-weight: 500;
`;

const WidgetContent = styled.div`
  padding: var(--spacing-md);
  height: calc(100% - 40px); /* Adjust based on header height */
  overflow: auto;
`;

// Define the initial layout
const initialLayouts = {
  lg: [
    { i: 'stats', x: 0, y: 0, w: 6, h: 2, minW: 3, minH: 2 },
    { i: 'notes', x: 6, y: 0, w: 6, h: 2, minW: 3, minH: 2 },
    { i: 'diceRoller', x: 0, y: 2, w: 4, h: 3, minW: 3, minH: 2 },
    { i: 'characterSheet', x: 4, y: 2, w: 8, h: 3, minW: 4, minH: 3 },
  ],
  md: [
    { i: 'stats', x: 0, y: 0, w: 5, h: 2, minW: 3, minH: 2 },
    { i: 'notes', x: 5, y: 0, w: 5, h: 2, minW: 3, minH: 2 },
    { i: 'diceRoller', x: 0, y: 2, w: 4, h: 3, minW: 3, minH: 2 },
    { i: 'characterSheet', x: 4, y: 2, w: 6, h: 3, minW: 4, minH: 3 },
  ],
  sm: [
    { i: 'stats', x: 0, y: 0, w: 6, h: 2, minW: 3, minH: 2 },
    { i: 'notes', x: 0, y: 2, w: 6, h: 2, minW: 3, minH: 2 },
    { i: 'diceRoller', x: 0, y: 4, w: 6, h: 3, minW: 3, minH: 2 },
    { i: 'characterSheet', x: 0, y: 7, w: 6, h: 3, minW: 4, minH: 3 },
  ],
};

// Define widget components mapping
const widgetComponents: Record<string, React.FC<any>> = {
  stats: StatsWidget,
  notes: NotesWidget,
  diceRoller: DiceRollerWidget,
  characterSheet: CharacterSheetWidget,
  text: TextWidget,
  table: TableWidget,
  clock: ClockWidget,
  countdown: CountdownWidget,
};

// Define widget titles
const widgetTitles: Record<string, string> = {
  stats: 'Game Stats',
  notes: 'Notes',
  diceRoller: 'Dice Roller',
  characterSheet: 'Character Sheet',
  text: 'Text',
  table: 'Table',
  clock: 'Clock',
  countdown: 'Countdown',
};

const Dashboard: React.FC = () => {
  const { theme } = useTheme();
  const { socket, isConnected } = useSocket();
  const { widgets, activeWidgets, addWidget, removeWidget } = useWidgets();
  const [layouts, setLayouts] = useState(initialLayouts);
  const [currentBreakpoint, setCurrentBreakpoint] = useState('lg');
  const [isAddingWidget, setIsAddingWidget] = useState(false);

  // Load saved layout from localStorage
  useEffect(() => {
    const savedLayouts = localStorage.getItem('dashboardLayouts');
    if (savedLayouts) {
      try {
        setLayouts(JSON.parse(savedLayouts));
      } catch (error) {
        console.error('Error loading saved layout:', error);
      }
    }
  }, []);

  // Save layout changes to localStorage and emit to server
  const handleLayoutChange = (layout: any, layouts: any) => {
    setLayouts(layouts);
    localStorage.setItem('dashboardLayouts', JSON.stringify(layouts));

    // Emit layout change to server if connected
    if (socket && isConnected) {
      socket.emit('dashboard:layoutChange', layouts);
    }
  };

  // Handle breakpoint change
  const handleBreakpointChange = (breakpoint: string) => {
    setCurrentBreakpoint(breakpoint);
  };

  // Reset layout to default
  const resetLayout = () => {
    setLayouts(initialLayouts);
    localStorage.setItem('dashboardLayouts', JSON.stringify(initialLayouts));

    // Emit layout reset to server if connected
    if (socket && isConnected) {
      socket.emit('dashboard:layoutChange', initialLayouts);
    }
  };

  // Save current layout
  const saveLayout = () => {
    localStorage.setItem('dashboardLayouts', JSON.stringify(layouts));
    alert('Layout saved successfully!');

    // Emit layout save to server if connected
    if (socket && isConnected) {
      socket.emit('dashboard:saveLayout', layouts);
    }
  };

  // Toggle widget selector modal
  const toggleWidgetSelector = () => {
    setIsAddingWidget(!isAddingWidget);
  };

  // Handle adding a new widget
  const handleAddWidget = (widgetId: string) => {
    // Add widget to active widgets
    addWidget(widgetId);

    // Add widget to layout
    const widgetMetadata = widgets.find(w => w.metadata.id === widgetId)?.metadata;

    if (widgetMetadata) {
      const { defaultSize, minW, minH } = widgetMetadata;

      // Create new layout item
      const newLayoutItem = {
        i: widgetId,
        x: 0,
        y: 0,
        w: defaultSize.w,
        h: defaultSize.h,
        minW: minW || 2,
        minH: minH || 1,
      };

      // Add to layouts for all breakpoints
      const updatedLayouts = { ...layouts };

      Object.keys(updatedLayouts).forEach(breakpoint => {
        updatedLayouts[breakpoint] = [
          ...updatedLayouts[breakpoint],
          { ...newLayoutItem }
        ];
      });

      setLayouts(updatedLayouts);

      // Save updated layouts
      localStorage.setItem('dashboardLayouts', JSON.stringify(updatedLayouts));

      // Emit layout change to server if connected
      if (socket && isConnected) {
        socket.emit('dashboard:layoutChange', updatedLayouts);
      }
    }

    // Close widget selector
    setIsAddingWidget(false);
  };

  // Handle removing a widget
  const handleRemoveWidget = (widgetId: string) => {
    // Remove widget from active widgets
    removeWidget(widgetId);

    // Remove widget from layouts
    const updatedLayouts = { ...layouts };

    Object.keys(updatedLayouts).forEach(breakpoint => {
      updatedLayouts[breakpoint] = updatedLayouts[breakpoint].filter(
        item => item.i !== widgetId
      );
    });

    setLayouts(updatedLayouts);

    // Save updated layouts
    localStorage.setItem('dashboardLayouts', JSON.stringify(updatedLayouts));

    // Emit layout change to server if connected
    if (socket && isConnected) {
      socket.emit('dashboard:layoutChange', updatedLayouts);
    }
  };

  return (
    <DashboardContainer>
      <ControlPanel>
        <h2>Dashboard</h2>
        <LayoutControls>
          <Button onClick={toggleWidgetSelector} theme={theme}>Add Widget</Button>
          <Button onClick={resetLayout} theme={theme}>Reset Layout</Button>
          <Button onClick={saveLayout} theme={theme}>Save Layout</Button>
        </LayoutControls>
      </ControlPanel>

      <ResponsiveGridLayout
        className="layout"
        layouts={layouts}
        breakpoints={{ lg: 1200, md: 996, sm: 768, xs: 480, xxs: 0 }}
        cols={{ lg: 12, md: 10, sm: 6, xs: 4, xxs: 2 }}
        rowHeight={100}
        margin={[16, 16]}
        onLayoutChange={handleLayoutChange}
        onBreakpointChange={handleBreakpointChange}
        isDraggable
        isResizable
        useCSSTransforms
      >
        {activeWidgets.map((widgetId) => {
          // Find the widget in the registry
          const widget = widgets.find(w => w.metadata.id === widgetId);

          if (!widget) {
            return null;
          }

          const WidgetComponent = widget.component;
          const widgetTitle = widget.metadata.name;

          return (
            <WidgetContainer key={widgetId} theme={theme}>
              <WidgetHeader theme={theme}>
                <WidgetTitle>{widgetTitle}</WidgetTitle>
                <CloseButton onClick={() => handleRemoveWidget(widgetId)}>×</CloseButton>
              </WidgetHeader>
              <WidgetContent>
                <WidgetComponent id={widgetId} />
              </WidgetContent>
            </WidgetContainer>
          );
        })}
      </ResponsiveGridLayout>

      {isAddingWidget && (
        <WidgetSelectorModal onClick={toggleWidgetSelector}>
          <ModalContent onClick={e => e.stopPropagation()} theme={theme}>
            <ModalHeader theme={theme}>
              <ModalTitle>Add Widget</ModalTitle>
              <CloseButton onClick={toggleWidgetSelector} theme={theme}>×</CloseButton>
            </ModalHeader>

            <WidgetGrid>
              {widgets.map(widget => (
                <WidgetCard
                  key={widget.metadata.id}
                  onClick={() => handleAddWidget(widget.metadata.id)}
                  theme={theme}
                >
                  <WidgetIcon>{widget.metadata.icon || '📊'}</WidgetIcon>
                  <WidgetName>{widget.metadata.name}</WidgetName>
                  <WidgetDescription>{widget.metadata.description}</WidgetDescription>
                </WidgetCard>
              ))}
            </WidgetGrid>
          </ModalContent>
        </WidgetSelectorModal>
      )}
    </DashboardContainer>
  );
};

export default Dashboard;
