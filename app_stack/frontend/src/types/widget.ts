/**
 * Widget type definitions for the RPGer dashboard
 */

import { ReactNode } from 'react';

/**
 * Widget size constraints
 */
export interface WidgetSizeConstraints {
  minW?: number;
  minH?: number;
  maxW?: number;
  maxH?: number;
}

/**
 * Widget metadata
 */
export interface WidgetMetadata extends WidgetSizeConstraints {
  id: string;
  name: string;
  description: string;
  category: WidgetCategory;
  icon?: string;
  version: string;
  author?: string;
  defaultSize: {
    w: number;
    h: number;
  };
}

/**
 * Widget category
 */
export enum WidgetCategory {
  GAME = 'game',
  CHARACTER = 'character',
  UTILITY = 'utility',
  SYSTEM = 'system',
  CUSTOM = 'custom',
}

/**
 * Widget configuration options
 */
export interface WidgetConfig {
  [key: string]: any;
}

/**
 * Widget props
 */
export interface WidgetProps {
  id: string;
  config?: WidgetConfig;
  onConfigChange?: (config: WidgetConfig) => void;
  isConfiguring?: boolean;
  isEditing?: boolean;
  className?: string;
  style?: React.CSSProperties;
}

/**
 * Widget component type
 */
export type WidgetComponent = React.FC<WidgetProps>;

/**
 * Widget registration info
 */
export interface WidgetRegistration {
  metadata: WidgetMetadata;
  component: WidgetComponent;
  configComponent?: React.FC<WidgetConfigProps>;
}

/**
 * Widget config component props
 */
export interface WidgetConfigProps {
  config: WidgetConfig;
  onChange: (config: WidgetConfig) => void;
}

/**
 * Widget event types
 */
export enum WidgetEventType {
  INIT = 'init',
  UPDATE = 'update',
  DESTROY = 'destroy',
  CONFIG_CHANGE = 'config_change',
  DATA_UPDATE = 'data_update',
}

/**
 * Widget event
 */
export interface WidgetEvent {
  type: WidgetEventType;
  widgetId: string;
  payload?: any;
}

/**
 * Widget event handler
 */
export type WidgetEventHandler = (event: WidgetEvent) => void;

/**
 * Widget lifecycle hooks
 */
export interface WidgetLifecycleHooks {
  onInit?: () => void | Promise<void>;
  onUpdate?: () => void | Promise<void>;
  onDestroy?: () => void | Promise<void>;
  onConfigChange?: (config: WidgetConfig) => void | Promise<void>;
  onDataUpdate?: (data: any) => void | Promise<void>;
}
