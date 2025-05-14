/**
 * API Routes
 */

import express from 'express';
import { Character } from '../models/Character';
import { Campaign } from '../models/Campaign';
import { Note } from '../models/Note';
import { Dashboard } from '../models/Dashboard';
import { Widget } from '../models/Widget';
import { getRedisClient } from '../config/redis';
import { logger } from '../utils/logger';

const router = express.Router();

/**
 * Health check endpoint
 */
router.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok', timestamp: new Date().toISOString() });
});

/**
 * Database status endpoint
 */
router.get('/db-status', async (req, res) => {
  try {
    const status = {
      mongodb: {
        connected: false,
        collections: {
          characters: 0,
          campaigns: 0,
          notes: 0,
          dashboards: 0,
          widgets: 0,
        },
      },
      redis: {
        connected: false,
        keys: 0,
      },
    };

    // Check MongoDB connection
    try {
      // Count documents in collections
      const [
        characterCount,
        campaignCount,
        noteCount,
        dashboardCount,
        widgetCount,
      ] = await Promise.all([
        Character.countDocuments(),
        Campaign.countDocuments(),
        Note.countDocuments(),
        Dashboard.countDocuments(),
        Widget.countDocuments(),
      ]);

      status.mongodb.connected = true;
      status.mongodb.collections.characters = characterCount;
      status.mongodb.collections.campaigns = campaignCount;
      status.mongodb.collections.notes = noteCount;
      status.mongodb.collections.dashboards = dashboardCount;
      status.mongodb.collections.widgets = widgetCount;
    } catch (error) {
      logger.error(`Error checking MongoDB status: ${error}`);
    }

    // Check Redis connection
    const redisClient = getRedisClient();
    if (redisClient) {
      try {
        // Check if Redis is connected
        const ping = await redisClient.ping();
        status.redis.connected = ping === 'PONG';

        // Count keys
        if (status.redis.connected) {
          const keys = await redisClient.keys('*');
          status.redis.keys = keys.length;
        }
      } catch (error) {
        logger.error(`Error checking Redis status: ${error}`);
      }
    }

    res.status(200).json(status);
  } catch (error) {
    logger.error(`Error in db-status endpoint: ${error}`);
    res.status(500).json({ error: 'Internal Server Error' });
  }
});

// Sample data for in-memory mode
const sampleData = {
  characters: [
    {
      _id: '1',
      name: 'Aragorn',
      race: 'Human',
      class: 'Ranger',
      level: 8,
      abilities: {
        strength: 16,
        dexterity: 14,
        constitution: 15,
        intelligence: 12,
        wisdom: 16,
        charisma: 14,
      },
      hp: {
        current: 65,
        maximum: 65,
      },
      armor_class: 16,
    },
    {
      _id: '2',
      name: 'Gandalf',
      race: 'Human',
      class: 'Wizard',
      level: 15,
      abilities: {
        strength: 10,
        dexterity: 12,
        constitution: 14,
        intelligence: 20,
        wisdom: 18,
        charisma: 16,
      },
      hp: {
        current: 90,
        maximum: 90,
      },
      armor_class: 14,
    },
  ],
  campaigns: [
    {
      _id: '1',
      name: 'The Fellowship of the Ring',
      concept: 'A journey to destroy the One Ring',
      setting: 'Middle Earth',
    },
  ],
  notes: [
    {
      _id: '1',
      title: 'Character Ideas',
      content: 'New character concept: Dwarven artificer who creates magical gadgets',
      category: 'Characters',
      tags: ['dwarf', 'artificer', 'magic'],
      pinned: true,
    },
    {
      _id: '2',
      title: 'Campaign Notes',
      content: 'Remember to introduce the mysterious stranger at the tavern next session',
      category: 'Campaigns',
      tags: ['npc', 'plot', 'hook'],
      pinned: false,
    },
  ],
  dashboards: [
    {
      _id: '1',
      name: 'Default Dashboard',
      description: 'Main game dashboard',
      isDefault: true,
    },
  ],
  widgets: [
    {
      _id: '1',
      widgetId: 'stats',
      name: 'Game Stats',
      type: 'stats',
      active: true,
    },
    {
      _id: '2',
      widgetId: 'notes',
      name: 'Notes',
      type: 'notes',
      active: true,
    },
    {
      _id: '3',
      widgetId: 'diceRoller',
      name: 'Dice Roller',
      type: 'diceRoller',
      active: true,
    },
    {
      _id: '4',
      widgetId: 'characterSheet',
      name: 'Character Sheet',
      type: 'characterSheet',
      active: true,
    },
    {
      _id: '5',
      widgetId: 'clock',
      name: 'Clock',
      type: 'clock',
      active: true,
    },
  ],
};

/**
 * Check if MongoDB is connected
 */
const isMongoConnected = (): boolean => {
  return mongoose.connection.readyState === 1;
};

/**
 * Get all characters
 */
router.get('/characters', async (req, res) => {
  try {
    if (isMongoConnected()) {
      const characters = await Character.find().select('-__v').limit(10);
      res.status(200).json(characters);
    } else {
      // Return sample data in in-memory mode
      res.status(200).json(sampleData.characters);
    }
  } catch (error) {
    logger.error(`Error getting characters: ${error}`);
    // Return sample data on error
    res.status(200).json(sampleData.characters);
  }
});

/**
 * Get all campaigns
 */
router.get('/campaigns', async (req, res) => {
  try {
    if (isMongoConnected()) {
      const campaigns = await Campaign.find().select('-__v').limit(10);
      res.status(200).json(campaigns);
    } else {
      // Return sample data in in-memory mode
      res.status(200).json(sampleData.campaigns);
    }
  } catch (error) {
    logger.error(`Error getting campaigns: ${error}`);
    // Return sample data on error
    res.status(200).json(sampleData.campaigns);
  }
});

/**
 * Get all notes
 */
router.get('/notes', async (req, res) => {
  try {
    if (isMongoConnected()) {
      const notes = await Note.find().select('-__v').limit(10);
      res.status(200).json(notes);
    } else {
      // Return sample data in in-memory mode
      res.status(200).json(sampleData.notes);
    }
  } catch (error) {
    logger.error(`Error getting notes: ${error}`);
    // Return sample data on error
    res.status(200).json(sampleData.notes);
  }
});

/**
 * Get all dashboards
 */
router.get('/dashboards', async (req, res) => {
  try {
    if (isMongoConnected()) {
      const dashboards = await Dashboard.find().select('-__v').limit(10);
      res.status(200).json(dashboards);
    } else {
      // Return sample data in in-memory mode
      res.status(200).json(sampleData.dashboards);
    }
  } catch (error) {
    logger.error(`Error getting dashboards: ${error}`);
    // Return sample data on error
    res.status(200).json(sampleData.dashboards);
  }
});

/**
 * Get all widgets
 */
router.get('/widgets', async (req, res) => {
  try {
    if (isMongoConnected()) {
      const widgets = await Widget.find().select('-__v').limit(10);
      res.status(200).json(widgets);
    } else {
      // Return sample data in in-memory mode
      res.status(200).json(sampleData.widgets);
    }
  } catch (error) {
    logger.error(`Error getting widgets: ${error}`);
    // Return sample data on error
    res.status(200).json(sampleData.widgets);
  }
});

export default router;
