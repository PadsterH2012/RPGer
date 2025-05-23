import React, { useState } from 'react';
import styled from 'styled-components';
import { Link, useLocation } from 'react-router-dom';
import { useTheme } from '../context/ThemeContext';

// Use $-prefixed props to avoid DOM warnings
const SidebarContainer = styled.aside<{ $isCollapsed: boolean; $theme: string }>`
  width: ${props => props.$isCollapsed ? '60px' : '240px'};
  height: 100%;
  background-color: ${props => props.$theme === 'dark' ? 'var(--dark-surface)' : 'var(--light-surface)'};
  border-right: 1px solid ${props => props.$theme === 'dark' ? 'var(--dark-border)' : 'var(--light-border)'};
  transition: width var(--transition-normal) ease;
  overflow: hidden;
`;

const SidebarHeader = styled.div<{ $theme: string }>`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md);
  border-bottom: 1px solid ${props => props.$theme === 'dark' ? 'var(--dark-border)' : 'var(--light-border)'};
`;

const CollapseButton = styled.button<{ $theme: string }>`
  background: none;
  border: none;
  color: var(--${props => props.$theme}-text-primary);
  cursor: pointer;
  padding: var(--spacing-sm);
  border-radius: var(--border-radius-full);
  transition: background-color var(--transition-fast) ease;

  &:hover {
    background-color: ${props => props.$theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)'};
  }
`;

const SidebarTitle = styled.h3<{ $isCollapsed: boolean }>`
  margin: 0;
  font-size: var(--font-size-md);
  font-weight: 500;
  display: ${props => props.$isCollapsed ? 'none' : 'block'};
`;

const SidebarContent = styled.div`
  padding: var(--spacing-md);
`;

const SidebarSection = styled.div`
  margin-bottom: var(--spacing-lg);
`;

const SectionTitle = styled.h4<{ $isCollapsed: boolean; $theme: string }>`
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: var(--${props => props.$theme}-text-secondary);
  margin-bottom: var(--spacing-sm);
  display: ${props => props.$isCollapsed ? 'none' : 'block'};
`;

const SidebarItem = styled.div<{ $isCollapsed: boolean; $isActive?: boolean; $theme: string }>`
  display: flex;
  align-items: center;
  padding: ${props => props.$isCollapsed ? 'var(--spacing-sm)' : 'var(--spacing-sm) var(--spacing-md)'};
  margin-bottom: var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  cursor: pointer;
  transition: background-color var(--transition-fast) ease;
  background-color: ${props => props.$isActive
    ? (props.$theme === 'dark' ? 'rgba(255, 255, 255, 0.15)' : 'rgba(0, 0, 0, 0.08)')
    : 'transparent'};

  &:hover {
    background-color: ${props => props.$theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)'};
  }
`;

const StyledLink = styled(Link)`
  text-decoration: none;
  color: inherit;
  display: flex;
  align-items: center;
  width: 100%;
`;

const ItemIcon = styled.span<{ $isCollapsed: boolean }>`
  margin-right: ${props => props.$isCollapsed ? '0' : 'var(--spacing-sm)'};
  font-size: var(--font-size-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  width: ${props => props.$isCollapsed ? '100%' : 'auto'};
`;

const ItemText = styled.span<{ $isCollapsed: boolean }>`
  display: ${props => props.$isCollapsed ? 'none' : 'block'};
`;

const Sidebar: React.FC = () => {
  const { theme } = useTheme();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const location = useLocation();

  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };

  return (
    <SidebarContainer $isCollapsed={isCollapsed} $theme={theme}>
      <SidebarHeader $theme={theme}>
        <SidebarTitle $isCollapsed={isCollapsed}>Navigation</SidebarTitle>
        <CollapseButton onClick={toggleCollapse} $theme={theme}>
          {isCollapsed ? '→' : '←'}
        </CollapseButton>
      </SidebarHeader>
      <SidebarContent>
        <SidebarSection>
          <SectionTitle $isCollapsed={isCollapsed} $theme={theme}>Dashboards</SectionTitle>
          <SidebarItem
            $isCollapsed={isCollapsed}
            $theme={theme}
            $isActive={location.pathname === '/'}
          >
            <StyledLink to="/">
              <ItemIcon $isCollapsed={isCollapsed}>🎮</ItemIcon>
              <ItemText $isCollapsed={isCollapsed}>RPG Dashboard</ItemText>
            </StyledLink>
          </SidebarItem>
          <SidebarItem
            $isCollapsed={isCollapsed}
            $theme={theme}
            $isActive={location.pathname === '/classic-dashboard'}
          >
            <StyledLink to="/classic-dashboard">
              <ItemIcon $isCollapsed={isCollapsed}>📋</ItemIcon>
              <ItemText $isCollapsed={isCollapsed}>Classic Dashboard</ItemText>
            </StyledLink>
          </SidebarItem>
          <SidebarItem
            $isCollapsed={isCollapsed}
            $theme={theme}
            $isActive={location.pathname === '/new-dashboard'}
          >
            <StyledLink to="/new-dashboard">
              <ItemIcon $isCollapsed={isCollapsed}>🆕</ItemIcon>
              <ItemText $isCollapsed={isCollapsed}>New Dashboard</ItemText>
            </StyledLink>
          </SidebarItem>
        </SidebarSection>

        <SidebarSection>
          <SectionTitle $isCollapsed={isCollapsed} $theme={theme}>Widgets</SectionTitle>
          <SidebarItem $isCollapsed={isCollapsed} $theme={theme}>
            <ItemIcon $isCollapsed={isCollapsed}>📊</ItemIcon>
            <ItemText $isCollapsed={isCollapsed}>Stats</ItemText>
          </SidebarItem>
          <SidebarItem $isCollapsed={isCollapsed} $theme={theme}>
            <ItemIcon $isCollapsed={isCollapsed}>🗺️</ItemIcon>
            <ItemText $isCollapsed={isCollapsed}>Map</ItemText>
          </SidebarItem>
          <SidebarItem $isCollapsed={isCollapsed} $theme={theme}>
            <ItemIcon $isCollapsed={isCollapsed}>📝</ItemIcon>
            <ItemText $isCollapsed={isCollapsed}>Notes</ItemText>
          </SidebarItem>
          <SidebarItem $isCollapsed={isCollapsed} $theme={theme}>
            <ItemIcon $isCollapsed={isCollapsed}>⚔️</ItemIcon>
            <ItemText $isCollapsed={isCollapsed}>Combat</ItemText>
          </SidebarItem>
        </SidebarSection>

        <SidebarSection>
          <SectionTitle $isCollapsed={isCollapsed} $theme={theme}>Tools</SectionTitle>
          <SidebarItem $isCollapsed={isCollapsed} $theme={theme}>
            <ItemIcon $isCollapsed={isCollapsed}>🎲</ItemIcon>
            <ItemText $isCollapsed={isCollapsed}>Dice Roller</ItemText>
          </SidebarItem>
          <SidebarItem $isCollapsed={isCollapsed} $theme={theme}>
            <ItemIcon $isCollapsed={isCollapsed}>👤</ItemIcon>
            <ItemText $isCollapsed={isCollapsed}>Character Sheet</ItemText>
          </SidebarItem>
          <SidebarItem $isCollapsed={isCollapsed} $theme={theme}>
            <ItemIcon $isCollapsed={isCollapsed}>📚</ItemIcon>
            <ItemText $isCollapsed={isCollapsed}>Rulebook</ItemText>
          </SidebarItem>
        </SidebarSection>

        <SidebarSection>
          <SectionTitle $isCollapsed={isCollapsed} $theme={theme}>System</SectionTitle>
          <SidebarItem
            $isCollapsed={isCollapsed}
            $theme={theme}
            $isActive={location.pathname === '/settings'}
          >
            <StyledLink to="/settings">
              <ItemIcon $isCollapsed={isCollapsed}>⚙️</ItemIcon>
              <ItemText $isCollapsed={isCollapsed}>Settings</ItemText>
            </StyledLink>
          </SidebarItem>
        </SidebarSection>
      </SidebarContent>
    </SidebarContainer>
  );
};

export default Sidebar;
