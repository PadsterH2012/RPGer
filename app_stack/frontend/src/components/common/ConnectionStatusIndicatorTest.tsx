/**
 * ConnectionStatusIndicatorTest Component
 * 
 * A test component to demonstrate the ConnectionStatusIndicator in different configurations.
 * This component can be used for development and testing purposes.
 */

import React from 'react';
import styled from 'styled-components';
import { useTheme } from '../../context/ThemeContext';
import ConnectionStatusIndicator from './ConnectionStatusIndicator';

const TestContainer = styled.div<{ theme: string }>`
  display: flex;
  flex-direction: column;
  gap: 20px;
  padding: 20px;
  background-color: var(--${props => props.theme}-widget-bg);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-sm);
`;

const TestSection = styled.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

const SectionTitle = styled.h3<{ theme: string }>`
  margin: 0;
  color: var(--${props => props.theme}-text-primary);
  font-size: var(--font-size-md);
  font-weight: 600;
`;

const SectionDescription = styled.p<{ theme: string }>`
  margin: 0;
  color: var(--${props => props.theme}-text-secondary);
  font-size: var(--font-size-sm);
`;

const IndicatorContainer = styled.div<{ theme: string }>`
  padding: 10px;
  background-color: var(--${props => props.theme}-card-bg);
  border-radius: var(--border-radius-sm);
  border: 1px solid var(--${props => props.theme}-border);
`;

const ConnectionStatusIndicatorTest: React.FC = () => {
  const { theme } = useTheme();

  return (
    <TestContainer theme={theme}>
      <SectionTitle theme={theme}>Connection Status Indicator Test</SectionTitle>
      <SectionDescription theme={theme}>
        This component demonstrates the ConnectionStatusIndicator in different configurations.
      </SectionDescription>

      <TestSection>
        <SectionTitle theme={theme}>Single Service (Backend)</SectionTitle>
        <IndicatorContainer theme={theme}>
          <ConnectionStatusIndicator 
            services={['backend']} 
            size="medium" 
            refreshInterval={15000}
          />
        </IndicatorContainer>
      </TestSection>

      <TestSection>
        <SectionTitle theme={theme}>Multiple Services (Horizontal)</SectionTitle>
        <IndicatorContainer theme={theme}>
          <ConnectionStatusIndicator 
            services={['backend', 'mongodb', 'redis', 'chroma']} 
            size="small" 
            horizontal={true}
            refreshInterval={15000}
          />
        </IndicatorContainer>
      </TestSection>

      <TestSection>
        <SectionTitle theme={theme}>Multiple Services (Vertical)</SectionTitle>
        <IndicatorContainer theme={theme}>
          <ConnectionStatusIndicator 
            services={['backend', 'mongodb', 'redis', 'chroma']} 
            size="medium" 
            horizontal={false}
            refreshInterval={15000}
          />
        </IndicatorContainer>
      </TestSection>

      <TestSection>
        <SectionTitle theme={theme}>Without Labels</SectionTitle>
        <IndicatorContainer theme={theme}>
          <ConnectionStatusIndicator 
            services={['backend', 'mongodb', 'redis', 'chroma']} 
            size="large" 
            horizontal={true}
            showLabels={false}
            refreshInterval={15000}
          />
        </IndicatorContainer>
      </TestSection>

      <TestSection>
        <SectionTitle theme={theme}>Different Sizes</SectionTitle>
        <IndicatorContainer theme={theme}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div>
              <span style={{ marginRight: '10px', fontSize: '12px' }}>Small:</span>
              <ConnectionStatusIndicator 
                services={['backend']} 
                size="small" 
                horizontal={true}
                refreshInterval={15000}
              />
            </div>
            <div>
              <span style={{ marginRight: '10px', fontSize: '12px' }}>Medium:</span>
              <ConnectionStatusIndicator 
                services={['backend']} 
                size="medium" 
                horizontal={true}
                refreshInterval={15000}
              />
            </div>
            <div>
              <span style={{ marginRight: '10px', fontSize: '12px' }}>Large:</span>
              <ConnectionStatusIndicator 
                services={['backend']} 
                size="large" 
                horizontal={true}
                refreshInterval={15000}
              />
            </div>
          </div>
        </IndicatorContainer>
      </TestSection>
    </TestContainer>
  );
};

export default ConnectionStatusIndicatorTest;
