/**
 * CountdownWidget Component
 * 
 * Widget for displaying a countdown timer.
 */

import React, { useState, useEffect, useCallback } from 'react';
import styled from 'styled-components';
import { useTheme } from '../../context/ThemeContext';
import { WidgetProps, WidgetCategory } from '../../types/widget';
import withWidget from './withWidget';

const CountdownContainer = styled.div`
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
`;

const Title = styled.div`
  font-size: var(--font-size-md);
  font-weight: 600;
  margin-bottom: var(--spacing-sm);
`;

const TimeDisplay = styled.div`
  font-size: var(--font-size-xxl);
  font-weight: 700;
  margin-bottom: var(--spacing-md);
  font-family: var(--font-family-mono, monospace);
`;

const TimeUnit = styled.span<{ highlight: boolean }>`
  color: ${props => props.highlight ? `var(--${props.theme}-primary)` : 'inherit'};
`;

const ControlsContainer = styled.div`
  display: flex;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-sm);
`;

const Button = styled.button`
  background-color: var(--${props => props.theme}-primary);
  color: ${props => props.theme === 'dark' ? 'black' : 'white'};
  border: none;
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  font-size: var(--font-size-sm);
  
  &:hover {
    background-color: var(--${props => props.theme}-primary-variant);
  }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background-color: ${props => props.theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'};
  border-radius: var(--border-radius-full);
  margin-top: var(--spacing-md);
  overflow: hidden;
`;

const ProgressFill = styled.div<{ width: number; color: string }>`
  height: 100%;
  width: ${props => props.width}%;
  background-color: ${props => props.color};
  border-radius: var(--border-radius-full);
  transition: width 1s linear;
`;

const InputContainer = styled.div`
  display: flex;
  flex-direction: column;
  width: 100%;
  margin-bottom: var(--spacing-md);
`;

const InputLabel = styled.label`
  font-size: var(--font-size-sm);
  margin-bottom: var(--spacing-xs);
  color: var(--${props => props.theme}-text-secondary);
`;

const Input = styled.input`
  padding: var(--spacing-sm);
  border: 1px solid var(--${props => props.theme}-border);
  border-radius: var(--border-radius-sm);
  background-color: var(--${props => props.theme}-surface);
  color: var(--${props => props.theme}-text-primary);
  
  &:focus {
    outline: none;
    border-color: var(--${props => props.theme}-primary);
  }
`;

interface CountdownWidgetConfig {
  title: string;
  duration: number; // in seconds
  autoStart: boolean;
  showControls: boolean;
  showProgress: boolean;
  endTime?: number; // timestamp
}

const defaultConfig: CountdownWidgetConfig = {
  title: 'Countdown',
  duration: 300, // 5 minutes
  autoStart: false,
  showControls: true,
  showProgress: true,
};

const CountdownWidget: React.FC<WidgetProps> = ({ id, config, onConfigChange }) => {
  const { theme } = useTheme();
  const widgetConfig = { ...defaultConfig, ...config } as CountdownWidgetConfig;
  
  const [timeLeft, setTimeLeft] = useState<number>(widgetConfig.duration);
  const [isRunning, setIsRunning] = useState<boolean>(widgetConfig.autoStart);
  const [isEditing, setIsEditing] = useState<boolean>(false);
  const [inputDuration, setInputDuration] = useState<string>(widgetConfig.duration.toString());
  const [inputTitle, setInputTitle] = useState<string>(widgetConfig.title);
  
  // Calculate progress percentage
  const progressPercentage = (widgetConfig.duration - timeLeft) / widgetConfig.duration * 100;
  
  // Get progress color based on time left
  const getProgressColor = useCallback(() => {
    const percentage = timeLeft / widgetConfig.duration;
    
    if (percentage > 0.66) {
      return 'var(--success)';
    } else if (percentage > 0.33) {
      return 'var(--warning)';
    } else {
      return 'var(--error)';
    }
  }, [timeLeft, widgetConfig.duration]);
  
  // Format time as HH:MM:SS
  const formatTime = useCallback((seconds: number): string => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }, []);
  
  // Update countdown timer
  useEffect(() => {
    let timer: NodeJS.Timeout;
    
    if (isRunning && timeLeft > 0) {
      timer = setInterval(() => {
        setTimeLeft(prev => prev - 1);
      }, 1000);
    } else if (timeLeft === 0) {
      setIsRunning(false);
      
      // Play sound or show notification when timer ends
      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('Countdown Timer', {
          body: `${widgetConfig.title} has ended!`,
          icon: '/favicon.ico',
        });
      }
    }
    
    return () => {
      clearInterval(timer);
    };
  }, [isRunning, timeLeft, widgetConfig.title]);
  
  // Load end time from config if available
  useEffect(() => {
    if (widgetConfig.endTime) {
      const now = Date.now();
      const end = widgetConfig.endTime;
      
      if (end > now) {
        const secondsLeft = Math.floor((end - now) / 1000);
        setTimeLeft(secondsLeft);
        setIsRunning(true);
      } else {
        setTimeLeft(0);
        setIsRunning(false);
      }
    } else {
      setTimeLeft(widgetConfig.duration);
    }
  }, [widgetConfig.endTime, widgetConfig.duration]);
  
  // Handle start/pause button click
  const handleStartPause = () => {
    if (!isRunning && timeLeft === 0) {
      // Reset and start if timer has ended
      setTimeLeft(widgetConfig.duration);
      setIsRunning(true);
      
      // Save end time to config
      if (onConfigChange) {
        onConfigChange({
          ...widgetConfig,
          endTime: Date.now() + widgetConfig.duration * 1000,
        });
      }
    } else {
      setIsRunning(!isRunning);
      
      // Save or clear end time based on running state
      if (onConfigChange) {
        if (!isRunning) {
          onConfigChange({
            ...widgetConfig,
            endTime: Date.now() + timeLeft * 1000,
          });
        } else {
          onConfigChange({
            ...widgetConfig,
            endTime: undefined,
          });
        }
      }
    }
  };
  
  // Handle reset button click
  const handleReset = () => {
    setTimeLeft(widgetConfig.duration);
    setIsRunning(false);
    
    // Clear end time in config
    if (onConfigChange) {
      onConfigChange({
        ...widgetConfig,
        endTime: undefined,
      });
    }
  };
  
  // Handle edit button click
  const handleEdit = () => {
    setIsEditing(true);
    setIsRunning(false);
  };
  
  // Handle save button click
  const handleSave = () => {
    const newDuration = parseInt(inputDuration, 10) || widgetConfig.duration;
    
    if (onConfigChange) {
      onConfigChange({
        ...widgetConfig,
        title: inputTitle,
        duration: newDuration,
        endTime: undefined,
      });
    }
    
    setTimeLeft(newDuration);
    setIsEditing(false);
  };
  
  return (
    <CountdownContainer>
      {isEditing ? (
        <>
          <InputContainer>
            <InputLabel theme={theme}>Title</InputLabel>
            <Input
              type="text"
              value={inputTitle}
              onChange={(e) => setInputTitle(e.target.value)}
              theme={theme}
            />
          </InputContainer>
          
          <InputContainer>
            <InputLabel theme={theme}>Duration (seconds)</InputLabel>
            <Input
              type="number"
              value={inputDuration}
              onChange={(e) => setInputDuration(e.target.value)}
              min="1"
              theme={theme}
            />
          </InputContainer>
          
          <Button onClick={handleSave} theme={theme}>
            Save
          </Button>
        </>
      ) : (
        <>
          <Title>{widgetConfig.title}</Title>
          
          <TimeDisplay>
            {formatTime(timeLeft).split(':').map((unit, index) => (
              <React.Fragment key={index}>
                {index > 0 && ':'}
                <TimeUnit highlight={index === 2} theme={theme}>
                  {unit}
                </TimeUnit>
              </React.Fragment>
            ))}
          </TimeDisplay>
          
          {widgetConfig.showControls && (
            <ControlsContainer>
              <Button onClick={handleStartPause} theme={theme}>
                {isRunning ? 'Pause' : timeLeft === 0 ? 'Restart' : 'Start'}
              </Button>
              <Button onClick={handleReset} disabled={timeLeft === widgetConfig.duration && !isRunning} theme={theme}>
                Reset
              </Button>
              <Button onClick={handleEdit} theme={theme}>
                Edit
              </Button>
            </ControlsContainer>
          )}
          
          {widgetConfig.showProgress && (
            <ProgressBar theme={theme}>
              <ProgressFill width={progressPercentage} color={getProgressColor()} />
            </ProgressBar>
          )}
        </>
      )}
    </CountdownContainer>
  );
};

export default withWidget(CountdownWidget, {
  metadata: {
    name: 'Countdown',
    description: 'Display a countdown timer',
    category: WidgetCategory.UTILITY,
    icon: '⏱️',
    defaultSize: {
      w: 4,
      h: 3,
    },
    minW: 2,
    minH: 2,
  },
  defaultConfig,
});
