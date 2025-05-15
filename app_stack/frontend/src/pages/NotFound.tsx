import React from 'react';
import { Link } from 'react-router-dom';
import styled from 'styled-components';
import { useTheme } from '../context/ThemeContext';

const NotFoundContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  text-align: center;
  padding: var(--spacing-xl);
`;

const NotFoundTitle = styled.h1`
  font-size: var(--font-size-4xl);
  margin-bottom: var(--spacing-md);
  color: var(--${props => props.theme}-primary);
`;

const NotFoundMessage = styled.p`
  font-size: var(--font-size-lg);
  margin-bottom: var(--spacing-xl);
  max-width: 600px;
`;

const HomeButton = styled(Link)`
  background-color: var(--${props => props.theme}-primary);
  color: ${props => props.theme === 'dark' ? 'black' : 'white'};
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--border-radius-md);
  text-decoration: none;
  font-weight: 500;
  transition: background-color var(--transition-fast) ease;

  &:hover {
    background-color: var(--${props => props.theme}-primary-variant);
    text-decoration: none;
  }
`;

const NotFound: React.FC = () => {
  const { theme } = useTheme();

  return (
    <NotFoundContainer>
      <NotFoundTitle theme={theme}>404</NotFoundTitle>
      <NotFoundMessage>
        Oops! The page you're looking for seems to have vanished into another dimension.
      </NotFoundMessage>
      <HomeButton to="/" theme={theme}>
        Return to Dashboard
      </HomeButton>
    </NotFoundContainer>
  );
};

export default NotFound;
