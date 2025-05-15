/**
 * withWidget Higher-Order Component
 *
 * HOC for creating widget components with standard functionality.
 */

import React from 'react';
import BaseWidget, { BaseWidgetProps } from './BaseWidget';
import { WidgetMetadata, WidgetCategory, WidgetProps } from '../../types/widget';
import widgetRegistry from '../../services/WidgetRegistry';

interface WithWidgetOptions {
  metadata: Omit<WidgetMetadata, 'id' | 'category' | 'version'> & {
    id?: string;
    category?: WidgetCategory;
    version?: string;
  };
  defaultConfig?: Record<string, any>;
}

/**
 * Higher-order component for creating widgets
 *
 * @param WrappedComponent Component to wrap
 * @param options Widget options
 * @returns Widget component
 */
export const withWidget = <P extends WidgetProps>(
  WrappedComponent: React.ComponentType<P>,
  options: WithWidgetOptions
) => {
  // Generate widget ID if not provided
  const widgetId = options.metadata.id || `widget-${options.metadata.name.toLowerCase().replace(/\s+/g, '-')}`;

  // Create metadata
  const metadata: WidgetMetadata = {
    id: widgetId,
    name: options.metadata.name,
    description: options.metadata.description,
    category: options.metadata.category || WidgetCategory.CUSTOM,
    version: options.metadata.version || '1.0.0',
    defaultSize: options.metadata.defaultSize,
    icon: options.metadata.icon,
    author: options.metadata.author,
    minW: options.metadata.minW,
    minH: options.metadata.minH,
    maxW: options.metadata.maxW,
    maxH: options.metadata.maxH,
  };

  // Create widget component
  const WidgetComponent: React.FC<P> = (props) => {
    return (
      <BaseWidget
        defaultConfig={options.defaultConfig}
        {...props}
      >
        <WrappedComponent {...props} />
      </BaseWidget>
    );
  };

  // Set display name
  WidgetComponent.displayName = `Widget(${WrappedComponent.displayName || WrappedComponent.name || 'Component'})`;

  // Register widget
  widgetRegistry.registerWidget({
    metadata,
    component: WidgetComponent as any,
  });

  return WidgetComponent;
};

export default withWidget;
