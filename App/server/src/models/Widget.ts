/**
 * Widget Model
 */

import mongoose, { Document, Schema } from 'mongoose';

// Widget position and size
interface WidgetLayout {
  x: number;
  y: number;
  w: number;
  h: number;
  minW?: number;
  minH?: number;
  maxW?: number;
  maxH?: number;
}

// Widget document interface
export interface IWidget extends Document {
  userId: mongoose.Types.ObjectId;
  widgetId: string;
  name: string;
  type: string;
  config: Record<string, any>;
  layout: Record<string, WidgetLayout>;
  active: boolean;
  createdAt: Date;
  updatedAt: Date;
}

// Widget schema
const WidgetSchema = new Schema<IWidget>(
  {
    userId: {
      type: Schema.Types.ObjectId,
      ref: 'User',
      required: true,
    },
    widgetId: {
      type: String,
      required: true,
    },
    name: {
      type: String,
      required: true,
      trim: true,
    },
    type: {
      type: String,
      required: true,
    },
    config: {
      type: Schema.Types.Mixed,
      default: {},
    },
    layout: {
      type: Map,
      of: {
        x: Number,
        y: Number,
        w: Number,
        h: Number,
        minW: Number,
        minH: Number,
        maxW: Number,
        maxH: Number,
      },
      default: {},
    },
    active: {
      type: Boolean,
      default: true,
    },
  },
  {
    timestamps: true,
  }
);

// Create compound index for userId and widgetId
WidgetSchema.index({ userId: 1, widgetId: 1 }, { unique: true });

// Create and export Widget model
export const Widget = mongoose.model<IWidget>('Widget', WidgetSchema);
