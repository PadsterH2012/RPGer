/**
 * BaseWidget Component
 *
 * Base component for all widgets to extend.
 */

import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useTheme } from '../../context/ThemeContext';
import { useWidget } from '../../hooks/useWidget';
import { WidgetProps, WidgetConfig } from '../../types/widget';

const WidgetWrapper = styled.div`
  height: 100%;
  display: flex;
  flex-direction: column;
  position: relative;
`;

const WidgetContent = styled.div`
  flex: 1;
  overflow: auto;
  padding: var(--spacing-sm);
`;

const LoadingOverlay = styled.div`
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
`;

const ErrorMessage = styled.div`
  color: var(--error);
  padding: var(--spacing-md);
  text-align: center;
  border: 1px solid var(--error);
  border-radius: var(--border-radius-sm);
  margin: var(--spacing-md);
`;

export interface BaseWidgetProps extends WidgetProps {
  defaultConfig?: WidgetConfig;
  onInit?: () => void | Promise<void>;
  onUpdate?: () => void | Promise<void>;
  onDestroy?: () => void | Promise<void>;
  onConfigChange?: (config: WidgetConfig) => void | Promise<void>;
  onDataUpdate?: (data: any) => void | Promise<void>;
  children?: React.ReactNode;
}

const BaseWidget: React.FC<BaseWidgetProps> = ({
  id,
  config: propConfig,
  onConfigChange: propOnConfigChange,
  defaultConfig,
  onInit,
  onUpdate,
  onDestroy,
  onConfigChange,
  onDataUpdate,
  children,
  className,
  style,
}) => {
  const { theme } = useTheme();
  const {
    config,
    updateConfig,
    isLoading,
    error,
    resetError,
    sendEvent
  } = useWidget(id, {
    defaultConfig,
    onInit,
    onUpdate,
    onDestroy,
    onConfigChange: (newConfig) => {
      // Call both the internal and external config change handlers
      if (onConfigChange) {
        onConfigChange(newConfig);
      }

      if (propOnConfigChange) {
        propOnConfigChange(newConfig);
      }
    },
    onDataUpdate
  });

  // Sync with prop config if provided
  useEffect(() => {
    if (propConfig && JSON.stringify(propConfig) !== JSON.stringify(config)) {
      updateConfig(propConfig);
    }
  }, [propConfig]);

  return (
    <WidgetWrapper className={className} style={style}>
      <WidgetContent>
        {error ? (
          <ErrorMessage onClick={resetError}>
            Error: {error.message}
            <br />
            <small>(Click to dismiss)</small>
          </ErrorMessage>
        ) : (
          children
        )}
      </WidgetContent>

      {isLoading && (
        <LoadingOverlay>
          <div>Loading...</div>
        </LoadingOverlay>
      )}
    </WidgetWrapper>
  );
};

export default BaseWidget;
