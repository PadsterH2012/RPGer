/**
 * Note Model
 */

import mongoose, { Document, Schema } from 'mongoose';

// Note document interface
export interface INote extends Document {
  userId: mongoose.Types.ObjectId;
  title: string;
  content: string;
  category?: string;
  tags?: string[];
  pinned: boolean;
  createdAt: Date;
  updatedAt: Date;
}

// Note schema
const NoteSchema = new Schema<INote>(
  {
    userId: {
      type: Schema.Types.ObjectId,
      ref: 'User',
      required: true,
    },
    title: {
      type: String,
      required: true,
      trim: true,
    },
    content: {
      type: String,
      required: true,
    },
    category: {
      type: String,
      trim: true,
    },
    tags: [String],
    pinned: {
      type: Boolean,
      default: false,
    },
  },
  {
    timestamps: true,
  }
);

// Create and export Note model
export const Note = mongoose.model<INote>('Note', NoteSchema);
