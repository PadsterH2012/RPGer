import React from 'react';
import { WidgetCategory } from '../../types/widget';
import withWidget from './withWidget';
import MongoDBViewerWidget from './MongoDBViewerWidget';

// Register the MongoDB Viewer widget
export default withWidget(MongoDBViewerWidget, {
  metadata: {
    name: 'MongoDB Viewer',
    description: 'View and search MongoDB collections and documents',
    category: WidgetCategory.SYSTEM,
    defaultSize: { w: 6, h: 8 },
    icon: '🗃️',
    author: 'RPGer',
    minW: 4,
    minH: 4,
    maxW: 12,
    maxH: 12,
  },
  defaultConfig: {
    collection: 'monsters',
    limit: 10,
  },
});
