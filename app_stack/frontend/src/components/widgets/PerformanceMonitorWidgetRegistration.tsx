import React from 'react';
import { WidgetCategory } from '../../types/widget';
import withWidget from './withWidget';
import PerformanceMonitorWidget from './PerformanceMonitorWidget';

// Register the Performance Monitor widget
export default withWidget(PerformanceMonitorWidget, {
  metadata: {
    name: 'Performance Monitor',
    description: 'Monitor system and container performance metrics',
    category: WidgetCategory.SYSTEM,
    defaultSize: { w: 4, h: 6 },
    icon: 'chart-line',
    minSize: { w: 2, h: 4 },
    maxSize: { w: 12, h: 12 },
  },
  defaultConfig: {
    refreshInterval: 5000,
  },
});
