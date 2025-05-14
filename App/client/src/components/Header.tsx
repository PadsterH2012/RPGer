import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { useTheme } from '../context/ThemeContext';
import { useSocket } from '../context/SocketContext';

const HeaderContainer = styled.header`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg);
  background-color: ${props => props.theme === 'dark' ? 'var(--dark-surface)' : 'var(--light-surface)'};
  border-bottom: 1px solid ${props => props.theme === 'dark' ? 'var(--dark-border)' : 'var(--light-border)'};
`;

const Logo = styled.div`
  font-family: var(--font-secondary);
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--${props => props.theme}-primary);
`;

const Nav = styled.nav`
  display: flex;
  gap: var(--spacing-md);
`;

const NavLink = styled(Link)`
  color: var(--${props => props.theme}-text-primary);
  text-decoration: none;
  padding: var(--spacing-sm);
  border-radius: var(--border-radius-sm);
  transition: background-color var(--transition-fast) ease;

  &:hover {
    background-color: ${props => props.theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)'};
    text-decoration: none;
  }
`;

const Controls = styled.div`
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
`;

const ThemeToggle = styled.button`
  background: none;
  border: none;
  color: var(--${props => props.theme}-text-primary);
  font-size: var(--font-size-md);
  cursor: pointer;
  padding: var(--spacing-sm);
  border-radius: var(--border-radius-full);
  transition: background-color var(--transition-fast) ease;

  &:hover {
    background-color: ${props => props.theme === 'dark' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.05)'};
  }
`;

const ConnectionStatus = styled.div<{ connected: boolean }>`
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-sm);
  color: ${props => props.connected ? 'var(--dark-secondary)' : 'var(--dark-error)'};
`;

const StatusDot = styled.div<{ connected: boolean }>`
  width: 8px;
  height: 8px;
  border-radius: var(--border-radius-full);
  background-color: ${props => props.connected ? 'var(--dark-secondary)' : 'var(--dark-error)'};
`;

const Header: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const { isConnected } = useSocket();

  return (
    <HeaderContainer theme={theme}>
      <Logo theme={theme}>RPGer</Logo>
      <Nav>
        <NavLink to="/" theme={theme}>Dashboard</NavLink>
        <NavLink to="/settings" theme={theme}>Settings</NavLink>
      </Nav>
      <Controls>
        <ConnectionStatus connected={isConnected}>
          <StatusDot connected={isConnected} />
          {isConnected ? 'Connected' : 'Disconnected'}
        </ConnectionStatus>
        <ThemeToggle onClick={toggleTheme} theme={theme}>
          {theme === 'dark' ? '☀️' : '🌙'}
        </ThemeToggle>
      </Controls>
    </HeaderContainer>
  );
};

export default Header;
