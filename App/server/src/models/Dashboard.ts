/**
 * Dashboard Model
 */

import mongoose, { Document, Schema } from 'mongoose';

// Dashboard document interface
export interface IDashboard extends Document {
  userId: mongoose.Types.ObjectId;
  name: string;
  description?: string;
  layouts: Record<string, any>;
  isDefault: boolean;
  createdAt: Date;
  updatedAt: Date;
}

// Dashboard schema
const DashboardSchema = new Schema<IDashboard>(
  {
    userId: {
      type: Schema.Types.ObjectId,
      ref: 'User',
      required: true,
    },
    name: {
      type: String,
      required: true,
      trim: true,
    },
    description: {
      type: String,
      trim: true,
    },
    layouts: {
      type: Schema.Types.Mixed,
      required: true,
    },
    isDefault: {
      type: Boolean,
      default: false,
    },
  },
  {
    timestamps: true,
  }
);

// Create and export Dashboard model
export const Dashboard = mongoose.model<IDashboard>('Dashboard', DashboardSchema);
