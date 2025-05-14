/**
 * Campaign Model
 */

import mongoose, { Document, Schema } from 'mongoose';

// Campaign location
interface Location {
  name: string;
  description: string;
  type: string;
  notes?: string;
}

// Campaign NPC
interface NPC {
  name: string;
  race?: string;
  class?: string;
  description: string;
  alignment?: string;
  notes?: string;
}

// Campaign faction
interface Faction {
  name: string;
  description: string;
  alignment?: string;
  notes?: string;
}

// Campaign quest
interface Quest {
  name: string;
  description: string;
  status: 'active' | 'completed' | 'failed' | 'inactive';
  rewards?: string;
  notes?: string;
}

// Campaign event
interface Event {
  name: string;
  description: string;
  date?: string;
  notes?: string;
}

// Campaign document interface
export interface ICampaign extends Document {
  userId: mongoose.Types.ObjectId;
  name: string;
  concept: string;
  setting: string;
  characters: mongoose.Types.ObjectId[];
  locations: Location[];
  npcs: NPC[];
  factions: Faction[];
  quests: Quest[];
  events: Event[];
  timeline: string[];
  notes: string;
  createdAt: Date;
  updatedAt: Date;
}

// Campaign schema
const CampaignSchema = new Schema<ICampaign>(
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
    concept: {
      type: String,
      required: true,
    },
    setting: {
      type: String,
      required: true,
    },
    characters: [
      {
        type: Schema.Types.ObjectId,
        ref: 'Character',
      },
    ],
    locations: [
      {
        name: {
          type: String,
          required: true,
        },
        description: {
          type: String,
          required: true,
        },
        type: {
          type: String,
          required: true,
        },
        notes: {
          type: String,
        },
      },
    ],
    npcs: [
      {
        name: {
          type: String,
          required: true,
        },
        race: {
          type: String,
        },
        class: {
          type: String,
        },
        description: {
          type: String,
          required: true,
        },
        alignment: {
          type: String,
        },
        notes: {
          type: String,
        },
      },
    ],
    factions: [
      {
        name: {
          type: String,
          required: true,
        },
        description: {
          type: String,
          required: true,
        },
        alignment: {
          type: String,
        },
        notes: {
          type: String,
        },
      },
    ],
    quests: [
      {
        name: {
          type: String,
          required: true,
        },
        description: {
          type: String,
          required: true,
        },
        status: {
          type: String,
          enum: ['active', 'completed', 'failed', 'inactive'],
          default: 'active',
        },
        rewards: {
          type: String,
        },
        notes: {
          type: String,
        },
      },
    ],
    events: [
      {
        name: {
          type: String,
          required: true,
        },
        description: {
          type: String,
          required: true,
        },
        date: {
          type: String,
        },
        notes: {
          type: String,
        },
      },
    ],
    timeline: [String],
    notes: {
      type: String,
      default: '',
    },
  },
  {
    timestamps: true,
  }
);

// Create and export Campaign model
export const Campaign = mongoose.model<ICampaign>('Campaign', CampaignSchema);
