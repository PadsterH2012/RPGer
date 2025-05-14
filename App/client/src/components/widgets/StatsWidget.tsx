import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useSocket } from '../../context/SocketContext';
import { useTheme } from '../../context/ThemeContext';
import { WidgetProps, WidgetCategory } from '../../types/widget';
import withWidget from './withWidget';

const StatsContainer = styled.div`
  height: 100%;
`;

const StatGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-md);
`;

const StatItem = styled.div`
  background-color: ${props => props.theme === 'dark' ? 'rgba(255, 255, 255, 0.05)' : 'rgba(0, 0, 0, 0.05)'};
  border-radius: var(--border-radius-sm);
  padding: var(--spacing-md);
`;

const StatLabel = styled.div`
  font-size: var(--font-size-sm);
  color: var(--${props => props.theme}-text-secondary);
  margin-bottom: var(--spacing-xs);
`;

const StatValue = styled.div`
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--${props => props.theme}-primary);
`;

const StatBar = styled.div`
  height: 6px;
  background-color: ${props => props.theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)'};
  border-radius: var(--border-radius-full);
  margin-top: var(--spacing-sm);
  overflow: hidden;
`;

const StatBarFill = styled.div<{ width: number; color: string }>`
  height: 100%;
  width: ${props => props.width}%;
  background-color: ${props => props.color};
  border-radius: var(--border-radius-full);
`;

interface PlayerStats {
  hp: {
    current: number;
    maximum: number;
  };
  level: number;
  experience: number;
  next_level_xp: number;
  armor_class: number;
}

// Default stats for in-memory mode
const defaultStats: PlayerStats = {
  hp: {
    current: 25,
    maximum: 30,
  },
  level: 3,
  experience: 2500,
  next_level_xp: 4000,
  armor_class: 15,
};

interface StatsWidgetConfig {
  showHp: boolean;
  showLevel: boolean;
  showExperience: boolean;
  showArmorClass: boolean;
}

const defaultConfig: StatsWidgetConfig = {
  showHp: true,
  showLevel: true,
  showExperience: true,
  showArmorClass: true,
};

const StatsWidget: React.FC<WidgetProps> = ({ id, config }) => {
  const { theme } = useTheme();
  const { socket, isConnected } = useSocket();
  const widgetConfig = { ...defaultConfig, ...config } as StatsWidgetConfig;
  const [stats, setStats] = useState<PlayerStats>(defaultStats);

  useEffect(() => {
    if (socket && isConnected) {
      // Listen for stats updates from the server
      socket.on('player:statsUpdate', (updatedStats: PlayerStats) => {
        setStats(updatedStats);
      });

      // Request initial stats
      socket.emit('player:requestStats');

      // Cleanup listener on unmount
      return () => {
        socket.off('player:statsUpdate');
      };
    }
  }, [socket, isConnected]);

  // Calculate HP percentage
  const hpPercent = stats.hp.maximum > 0 ? (stats.hp.current / stats.hp.maximum) * 100 : 0;

  // Calculate XP percentage
  const xpPercent = stats.next_level_xp > 0 ? (stats.experience / stats.next_level_xp) * 100 : 0;

  // Determine HP bar color based on percentage
  const getHpColor = () => {
    if (hpPercent <= 25) return 'var(--dark-error)';
    if (hpPercent <= 50) return 'orange';
    return 'var(--dark-secondary)';
  };

  return (
    <StatsContainer>
      <StatGrid>
        {widgetConfig.showHp && (
          <StatItem theme={theme}>
            <StatLabel theme={theme}>Hit Points</StatLabel>
            <StatValue theme={theme}>{stats.hp.current}/{stats.hp.maximum}</StatValue>
            <StatBar theme={theme}>
              <StatBarFill width={hpPercent} color={getHpColor()} />
            </StatBar>
          </StatItem>
        )}

        {widgetConfig.showLevel && (
          <StatItem theme={theme}>
            <StatLabel theme={theme}>Level</StatLabel>
            <StatValue theme={theme}>{stats.level}</StatValue>
          </StatItem>
        )}

        {widgetConfig.showExperience && (
          <StatItem theme={theme}>
            <StatLabel theme={theme}>Experience</StatLabel>
            <StatValue theme={theme}>{stats.experience}/{stats.next_level_xp}</StatValue>
            <StatBar theme={theme}>
              <StatBarFill width={xpPercent} color="var(--dark-primary)" />
            </StatBar>
          </StatItem>
        )}

        {widgetConfig.showArmorClass && (
          <StatItem theme={theme}>
            <StatLabel theme={theme}>Armor Class</StatLabel>
            <StatValue theme={theme}>{stats.armor_class}</StatValue>
          </StatItem>
        )}
      </StatGrid>
    </StatsContainer>
  );
};

export default withWidget(StatsWidget, {
  metadata: {
    name: 'Character Stats',
    description: 'Display character statistics',
    category: WidgetCategory.CHARACTER,
    icon: '📊',
    defaultSize: {
      w: 6,
      h: 2,
    },
    minW: 3,
    minH: 2,
  },
  defaultConfig,
});
