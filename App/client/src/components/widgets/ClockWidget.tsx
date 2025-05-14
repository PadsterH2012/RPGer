/**
 * ClockWidget Component
 * 
 * Widget for displaying current time and date.
 */

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useTheme } from '../../context/ThemeContext';
import { WidgetProps, WidgetCategory } from '../../types/widget';
import withWidget from './withWidget';

const ClockContainer = styled.div`
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
`;

const TimeDisplay = styled.div<{ size: string }>`
  font-size: ${props => props.size};
  font-weight: 700;
  margin-bottom: var(--spacing-sm);
  font-family: var(--font-family-mono, monospace);
`;

const DateDisplay = styled.div<{ size: string }>`
  font-size: ${props => props.size};
  color: var(--${props => props.theme}-text-secondary);
`;

const SecondsDot = styled.span<{ blinking: boolean }>`
  opacity: ${props => props.blinking ? (props.theme === 'dark' ? 0.7 : 0.5) : 1};
  transition: opacity 0.5s ease;
`;

interface ClockWidgetConfig {
  format: '12h' | '24h';
  showSeconds: boolean;
  showDate: boolean;
  blinkingSeparator: boolean;
  timeSize: string;
  dateSize: string;
  timezone?: string;
}

const defaultConfig: ClockWidgetConfig = {
  format: '24h',
  showSeconds: true,
  showDate: true,
  blinkingSeparator: true,
  timeSize: 'var(--font-size-xxl)',
  dateSize: 'var(--font-size-md)',
};

const ClockWidget: React.FC<WidgetProps> = ({ config }) => {
  const { theme } = useTheme();
  const widgetConfig = { ...defaultConfig, ...config } as ClockWidgetConfig;
  
  const [time, setTime] = useState<Date>(new Date());
  const [blinkState, setBlinkState] = useState<boolean>(true);
  
  // Update time every second
  useEffect(() => {
    const timer = setInterval(() => {
      setTime(new Date());
      
      if (widgetConfig.blinkingSeparator) {
        setBlinkState(prev => !prev);
      }
    }, 1000);
    
    return () => {
      clearInterval(timer);
    };
  }, [widgetConfig.blinkingSeparator]);
  
  // Format time based on configuration
  const formatTime = (date: Date): string => {
    let hours = date.getHours();
    const minutes = date.getMinutes().toString().padStart(2, '0');
    const seconds = date.getSeconds().toString().padStart(2, '0');
    let period = '';
    
    if (widgetConfig.format === '12h') {
      period = hours >= 12 ? ' PM' : ' AM';
      hours = hours % 12;
      hours = hours ? hours : 12; // Convert 0 to 12 for 12 AM
    }
    
    const separator = widgetConfig.blinkingSeparator 
      ? <SecondsDot blinking={!blinkState} theme={theme}>:</SecondsDot>
      : ':';
    
    return (
      <>
        {hours.toString().padStart(2, '0')}{separator}{minutes}
        {widgetConfig.showSeconds && <>{separator}{seconds}</>}
        {period}
      </>
    );
  };
  
  // Format date
  const formatDate = (date: Date): string => {
    const options: Intl.DateTimeFormatOptions = { 
      weekday: 'long', 
      year: 'numeric', 
      month: 'long', 
      day: 'numeric' 
    };
    
    return date.toLocaleDateString(undefined, options);
  };
  
  return (
    <ClockContainer>
      <TimeDisplay size={widgetConfig.timeSize}>
        {formatTime(time)}
      </TimeDisplay>
      
      {widgetConfig.showDate && (
        <DateDisplay size={widgetConfig.dateSize} theme={theme}>
          {formatDate(time)}
        </DateDisplay>
      )}
    </ClockContainer>
  );
};

export default withWidget(ClockWidget, {
  metadata: {
    name: 'Clock',
    description: 'Display current time and date',
    category: WidgetCategory.UTILITY,
    icon: '🕒',
    defaultSize: {
      w: 4,
      h: 2,
    },
    minW: 2,
    minH: 1,
  },
  defaultConfig,
});
