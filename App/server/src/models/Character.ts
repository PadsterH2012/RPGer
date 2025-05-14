/**
 * Character Model
 */

import mongoose, { Document, Schema } from 'mongoose';

// Character ability scores
interface AbilityScores {
  strength: number;
  dexterity: number;
  constitution: number;
  intelligence: number;
  wisdom: number;
  charisma: number;
}

// Character hit points
interface HitPoints {
  current: number;
  maximum: number;
  temporary?: number;
}

// Character equipment item
interface EquipmentItem {
  name: string;
  type: string;
  details?: string;
  quantity?: number;
  equipped?: boolean;
}

// Character skill
interface Skill {
  name: string;
  value: number;
  proficient?: boolean;
}

// Character spell
interface Spell {
  name: string;
  level: number;
  prepared?: boolean;
  details?: string;
}

// Character document interface
export interface ICharacter extends Document {
  userId: mongoose.Types.ObjectId;
  name: string;
  race: string;
  class: string;
  level: number;
  experience: number;
  next_level_xp: number;
  alignment?: string;
  background?: string;
  abilities: AbilityScores;
  hp: HitPoints;
  armor_class: number;
  equipment: EquipmentItem[];
  spells: Spell[];
  skills: Record<string, number>;
  features?: string[];
  proficiencies?: string[];
  languages?: string[];
  money?: {
    copper?: number;
    silver?: number;
    electrum?: number;
    gold?: number;
    platinum?: number;
  };
  notes?: string;
  createdAt: Date;
  updatedAt: Date;
}

// Character schema
const CharacterSchema = new Schema<ICharacter>(
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
    race: {
      type: String,
      required: true,
    },
    class: {
      type: String,
      required: true,
    },
    level: {
      type: Number,
      required: true,
      min: 1,
      default: 1,
    },
    experience: {
      type: Number,
      required: true,
      min: 0,
      default: 0,
    },
    next_level_xp: {
      type: Number,
      required: true,
      min: 0,
      default: 300,
    },
    alignment: {
      type: String,
    },
    background: {
      type: String,
    },
    abilities: {
      strength: {
        type: Number,
        required: true,
        min: 1,
        max: 30,
      },
      dexterity: {
        type: Number,
        required: true,
        min: 1,
        max: 30,
      },
      constitution: {
        type: Number,
        required: true,
        min: 1,
        max: 30,
      },
      intelligence: {
        type: Number,
        required: true,
        min: 1,
        max: 30,
      },
      wisdom: {
        type: Number,
        required: true,
        min: 1,
        max: 30,
      },
      charisma: {
        type: Number,
        required: true,
        min: 1,
        max: 30,
      },
    },
    hp: {
      current: {
        type: Number,
        required: true,
      },
      maximum: {
        type: Number,
        required: true,
      },
      temporary: {
        type: Number,
      },
    },
    armor_class: {
      type: Number,
      required: true,
      min: 0,
    },
    equipment: [
      {
        name: {
          type: String,
          required: true,
        },
        type: {
          type: String,
          required: true,
        },
        details: {
          type: String,
        },
        quantity: {
          type: Number,
          default: 1,
        },
        equipped: {
          type: Boolean,
          default: false,
        },
      },
    ],
    spells: [
      {
        name: {
          type: String,
          required: true,
        },
        level: {
          type: Number,
          required: true,
          min: 0,
        },
        prepared: {
          type: Boolean,
          default: false,
        },
        details: {
          type: String,
        },
      },
    ],
    skills: {
      type: Map,
      of: Number,
      default: {},
    },
    features: [String],
    proficiencies: [String],
    languages: [String],
    money: {
      copper: {
        type: Number,
        default: 0,
      },
      silver: {
        type: Number,
        default: 0,
      },
      electrum: {
        type: Number,
        default: 0,
      },
      gold: {
        type: Number,
        default: 0,
      },
      platinum: {
        type: Number,
        default: 0,
      },
    },
    notes: {
      type: String,
    },
  },
  {
    timestamps: true,
  }
);

// Create and export Character model
export const Character = mongoose.model<ICharacter>('Character', CharacterSchema);
