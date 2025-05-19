import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useTheme } from '../../context/ThemeContext';
import { WidgetProps } from '../../types/widget';

// Widget container
const PerformanceContainer = styled.div<{ theme: string }>`
  display: flex;
  flex-direction: column;
  height: 100%;
  background-color: var(--${props => props.theme}-widget-bg);
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
`;

// Widget header
const WidgetHeader = styled.div<{ theme: string }>`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--spacing-sm) var(--spacing-md);
  background-color: var(--${props => props.theme}-widget-header-bg);
  border-bottom: 1px solid var(--${props => props.theme}-border);
`;

// Widget title
const WidgetTitle = styled.h3<{ theme: string }>`
  margin: 0;
  font-size: var(--font-size-md);
  font-weight: 600;
  color: var(--${props => props.theme}-text-primary);
`;

// Widget content
const WidgetContent = styled.div<{ theme: string }>`
  flex: 1;
  padding: var(--spacing-md);
  overflow-y: auto;
`;

// Metric container
const MetricContainer = styled.div<{ theme: string }>`
  display: flex;
  flex-direction: column;
  margin-bottom: var(--spacing-md);
  padding: var(--spacing-sm);
  background-color: var(--${props => props.theme}-card-bg);
  border-radius: var(--border-radius-sm);
  border: 1px solid var(--${props => props.theme}-border);
`;

// Metric header
const MetricHeader = styled.div<{ theme: string }>`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xs);
`;

// Metric title
const MetricTitle = styled.h4<{ theme: string }>`
  margin: 0;
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--${props => props.theme}-text-primary);
`;

// Metric value
const MetricValue = styled.span<{ theme: string, warning?: boolean }>`
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: ${props => props.warning ? 'var(--color-warning)' : 'var(--color-success)'};
`;

// Progress bar container
const ProgressBarContainer = styled.div<{ theme: string }>`
  width: 100%;
  height: 8px;
  background-color: var(--${props => props.theme}-progress-bg);
  border-radius: 4px;
  overflow: hidden;
`;

// Progress bar
const ProgressBar = styled.div<{ width: number, warning?: boolean }>`
  width: ${props => props.width}%;
  height: 100%;
  background-color: ${props => props.warning ? 'var(--color-warning)' : 'var(--color-success)'};
  transition: width 0.3s ease;
`;

// Performance data interface
interface PerformanceData {
  system: {
    cpu: {
      percent: number;
      count: number;
      frequency: {
        current: number | null;
        min: number | null;
        max: number | null;
      };
    };
    memory: {
      total: number;
      available: number;
      used: number;
      percent: number;
    };
    disk: {
      total: number;
      used: number;
      free: number;
      percent: number;
    };
    network: {
      bytes_sent: number;
      bytes_recv: number;
      packets_sent: number;
      packets_recv: number;
    };
  };
  process: {
    pid: number;
    cpu_percent: number;
    memory: {
      rss: number;
      vms: number;
      shared: number;
    };
    threads: number;
    create_time: number;
  };
  timestamp: number;
}

// Format bytes to human-readable string
const formatBytes = (bytes: number): string => {
  if (bytes === 0) return '0 B';
  
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(1024));
  
  return `${(bytes / Math.pow(1024, i)).toFixed(2)} ${sizes[i]}`;
};

// Performance Monitor Widget
const PerformanceMonitorWidget: React.FC<WidgetProps> = ({ id, config = {} }) => {
  const { theme } = useTheme();
  const [performanceData, setPerformanceData] = useState<PerformanceData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string>('');

  // Fetch performance data
  const fetchPerformanceData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('http://localhost:5002/api/performance');
      
      if (response.status === 200) {
        const data = await response.json();
        setPerformanceData(data);
        setLastUpdated(new Date().toLocaleTimeString());
      } else {
        setError(`Failed to fetch performance data: ${response.status}`);
      }
    } catch (err: any) {
      console.error('Error fetching performance data:', err);
      setError(`Failed to fetch performance data: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // Fetch performance data on mount and every 5 seconds
  useEffect(() => {
    fetchPerformanceData();
    
    const intervalId = setInterval(fetchPerformanceData, 5000);
    
    return () => {
      clearInterval(intervalId);
    };
  }, []);

  return (
    <PerformanceContainer theme={theme}>
      <WidgetHeader theme={theme}>
        <WidgetTitle theme={theme}>Performance Monitor</WidgetTitle>
        <button
          onClick={fetchPerformanceData}
          style={{
            padding: '6px 12px',
            backgroundColor: '#8a2be2',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '14px',
            fontWeight: 'bold'
          }}
          disabled={loading}
        >
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </WidgetHeader>
      
      <WidgetContent theme={theme}>
        {error ? (
          <div style={{ color: 'var(--color-error)' }}>{error}</div>
        ) : !performanceData ? (
          <div>Loading performance data...</div>
        ) : (
          <>
            {/* CPU Usage */}
            <MetricContainer theme={theme}>
              <MetricHeader theme={theme}>
                <MetricTitle theme={theme}>CPU Usage</MetricTitle>
                <MetricValue 
                  theme={theme} 
                  warning={performanceData.system.cpu.percent > 80}
                >
                  {performanceData.system.cpu.percent.toFixed(1)}%
                </MetricValue>
              </MetricHeader>
              <ProgressBarContainer theme={theme}>
                <ProgressBar 
                  width={performanceData.system.cpu.percent} 
                  warning={performanceData.system.cpu.percent > 80} 
                />
              </ProgressBarContainer>
              <div style={{ fontSize: '12px', marginTop: '4px', color: 'var(--color-text-secondary)' }}>
                {performanceData.system.cpu.count} CPU cores
                {performanceData.system.cpu.frequency.current && 
                  ` @ ${(performanceData.system.cpu.frequency.current / 1000).toFixed(2)} GHz`}
              </div>
            </MetricContainer>
            
            {/* Memory Usage */}
            <MetricContainer theme={theme}>
              <MetricHeader theme={theme}>
                <MetricTitle theme={theme}>Memory Usage</MetricTitle>
                <MetricValue 
                  theme={theme} 
                  warning={performanceData.system.memory.percent > 80}
                >
                  {performanceData.system.memory.percent.toFixed(1)}%
                </MetricValue>
              </MetricHeader>
              <ProgressBarContainer theme={theme}>
                <ProgressBar 
                  width={performanceData.system.memory.percent} 
                  warning={performanceData.system.memory.percent > 80} 
                />
              </ProgressBarContainer>
              <div style={{ fontSize: '12px', marginTop: '4px', color: 'var(--color-text-secondary)' }}>
                {formatBytes(performanceData.system.memory.used)} / {formatBytes(performanceData.system.memory.total)}
              </div>
            </MetricContainer>
            
            {/* Disk Usage */}
            <MetricContainer theme={theme}>
              <MetricHeader theme={theme}>
                <MetricTitle theme={theme}>Disk Usage</MetricTitle>
                <MetricValue 
                  theme={theme} 
                  warning={performanceData.system.disk.percent > 80}
                >
                  {performanceData.system.disk.percent.toFixed(1)}%
                </MetricValue>
              </MetricHeader>
              <ProgressBarContainer theme={theme}>
                <ProgressBar 
                  width={performanceData.system.disk.percent} 
                  warning={performanceData.system.disk.percent > 80} 
                />
              </ProgressBarContainer>
              <div style={{ fontSize: '12px', marginTop: '4px', color: 'var(--color-text-secondary)' }}>
                {formatBytes(performanceData.system.disk.used)} / {formatBytes(performanceData.system.disk.total)}
              </div>
            </MetricContainer>
            
            {/* Network Usage */}
            <MetricContainer theme={theme}>
              <MetricHeader theme={theme}>
                <MetricTitle theme={theme}>Network Usage</MetricTitle>
              </MetricHeader>
              <div style={{ fontSize: '12px', color: 'var(--color-text-secondary)' }}>
                <div>Received: {formatBytes(performanceData.system.network.bytes_recv)}</div>
                <div>Sent: {formatBytes(performanceData.system.network.bytes_sent)}</div>
                <div>Packets: {performanceData.system.network.packets_recv} in / {performanceData.system.network.packets_sent} out</div>
              </div>
            </MetricContainer>
            
            {/* Last Updated */}
            <div style={{ fontSize: '12px', textAlign: 'right', color: 'var(--color-text-secondary)' }}>
              Last updated: {lastUpdated}
            </div>
          </>
        )}
      </WidgetContent>
    </PerformanceContainer>
  );
};

export default PerformanceMonitorWidget;
