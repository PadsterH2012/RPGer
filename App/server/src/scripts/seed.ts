/**
 * Database Seed Script
 * 
 * Run with: npx ts-node src/scripts/seed.ts
 */

import mongoose from 'mongoose';
import dotenv from 'dotenv';
import { User } from '../models/User';
import { Character } from '../models/Character';
import { Campaign } from '../models/Campaign';
import { Note } from '../models/Note';
import { Dashboard } from '../models/Dashboard';
import { Widget } from '../models/Widget';
import { connectToMongoDB, disconnectFromMongoDB } from '../config/database';

// Load environment variables
dotenv.config();

/**
 * Seed the database with initial data
 */
async function seedDatabase() {
  try {
    // Connect to MongoDB
    await connectToMongoDB();
    
    console.log('Connected to MongoDB');
    
    // Clear existing data
    await Promise.all([
      User.deleteMany({}),
      Character.deleteMany({}),
      Campaign.deleteMany({}),
      Note.deleteMany({}),
      Dashboard.deleteMany({}),
      Widget.deleteMany({}),
    ]);
    
    console.log('Cleared existing data');
    
    // Create test user
    const user = await User.create({
      username: 'testuser',
      email: 'test@example.com',
      password: 'password123',
      role: 'user',
      preferences: {
        theme: 'dark',
        fontSize: 'medium',
        notifications: true,
      },
    });
    
    console.log(`Created test user: ${user.username}`);
    
    // Create test characters
    const characters = await Character.create([
      {
        userId: user._id,
        name: 'Aragorn',
        race: 'Human',
        class: 'Ranger',
        level: 8,
        experience: 34000,
        next_level_xp: 40000,
        alignment: 'Lawful Good',
        background: 'Outlander',
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
        equipment: [
          { name: 'Longsword', type: 'Weapon', details: '1d8 slashing' },
          { name: 'Bow', type: 'Weapon', details: '1d8 piercing' },
          { name: 'Leather Armor', type: 'Armor', details: 'AC 11 + DEX' },
          { name: 'Ranger\'s Kit', type: 'Gear', details: 'Various tools and supplies' },
        ],
        spells: [],
        skills: {
          'Survival': 7,
          'Perception': 6,
          'Stealth': 5,
          'Animal Handling': 6,
        },
      },
      {
        userId: user._id,
        name: 'Gandalf',
        race: 'Human',
        class: 'Wizard',
        level: 15,
        experience: 170000,
        next_level_xp: 195000,
        alignment: 'Neutral Good',
        background: 'Sage',
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
        equipment: [
          { name: 'Staff', type: 'Weapon', details: '1d6 bludgeoning' },
          { name: 'Spellbook', type: 'Gear', details: 'Contains spells' },
          { name: 'Robes', type: 'Armor', details: 'No armor bonus' },
          { name: 'Component Pouch', type: 'Gear', details: 'Spell components' },
        ],
        spells: [
          { name: 'Fireball', level: 3, prepared: true, details: '8d6 fire damage' },
          { name: 'Lightning Bolt', level: 3, prepared: true, details: '8d6 lightning damage' },
          { name: 'Magic Missile', level: 1, prepared: true, details: '3 darts, 1d4+1 force damage each' },
          { name: 'Shield', level: 1, prepared: true, details: '+5 AC until next turn' },
        ],
        skills: {
          'Arcana': 10,
          'History': 10,
          'Investigation': 10,
          'Persuasion': 8,
        },
      },
    ]);
    
    console.log(`Created ${characters.length} test characters`);
    
    // Create test campaign
    const campaign = await Campaign.create({
      userId: user._id,
      name: 'The Fellowship of the Ring',
      concept: 'A journey to destroy the One Ring',
      setting: 'Middle Earth',
      characters: characters.map(char => char._id),
      locations: [
        {
          name: 'Rivendell',
          description: 'Elven outpost and home of Elrond',
          type: 'City',
          notes: 'Council of Elrond was held here',
        },
        {
          name: 'Moria',
          description: 'Ancient dwarven mine, now overrun by orcs',
          type: 'Dungeon',
          notes: 'Balrog dwells in the depths',
        },
      ],
      npcs: [
        {
          name: 'Elrond',
          race: 'Elf',
          description: 'Lord of Rivendell, ancient and wise',
          alignment: 'Neutral Good',
        },
        {
          name: 'Galadriel',
          race: 'Elf',
          description: 'Lady of Lothlorien, powerful and mysterious',
          alignment: 'Neutral Good',
        },
      ],
      factions: [
        {
          name: 'The Fellowship',
          description: 'Group formed to destroy the One Ring',
          alignment: 'Good',
        },
        {
          name: 'Mordor',
          description: 'Forces of Sauron seeking the Ring',
          alignment: 'Evil',
        },
      ],
      quests: [
        {
          name: 'Destroy the One Ring',
          description: 'Take the Ring to Mount Doom and cast it into the fire',
          status: 'active',
          rewards: 'Save Middle Earth',
        },
        {
          name: 'Cross the Misty Mountains',
          description: 'Find a way through or around the mountains',
          status: 'completed',
          rewards: 'Continue the journey',
        },
      ],
      events: [
        {
          name: 'Council of Elrond',
          description: 'Meeting to decide the fate of the Ring',
          date: 'October 25, 3018',
        },
        {
          name: 'Battle of Moria',
          description: 'Confrontation with orcs and the Balrog',
          date: 'January 15, 3019',
        },
      ],
      timeline: [
        'The Ring is found',
        'Frodo leaves the Shire',
        'Council of Elrond',
        'Fellowship departs',
        'Gandalf falls in Moria',
      ],
      notes: 'The journey is perilous, but the fate of Middle Earth hangs in the balance.',
    });
    
    console.log(`Created test campaign: ${campaign.name}`);
    
    // Create test notes
    const notes = await Note.create([
      {
        userId: user._id,
        title: 'Character Ideas',
        content: 'New character concept: Dwarven artificer who creates magical gadgets',
        category: 'Characters',
        tags: ['dwarf', 'artificer', 'magic'],
        pinned: true,
      },
      {
        userId: user._id,
        title: 'Campaign Notes',
        content: 'Remember to introduce the mysterious stranger at the tavern next session',
        category: 'Campaigns',
        tags: ['npc', 'plot', 'hook'],
        pinned: false,
      },
    ]);
    
    console.log(`Created ${notes.length} test notes`);
    
    // Create test dashboard
    const dashboard = await Dashboard.create({
      userId: user._id,
      name: 'Default Dashboard',
      description: 'Main game dashboard',
      layouts: {
        lg: [
          { i: 'stats', x: 0, y: 0, w: 3, h: 2, minW: 2, minH: 1 },
          { i: 'notes', x: 3, y: 0, w: 6, h: 4, minW: 3, minH: 2 },
          { i: 'diceRoller', x: 9, y: 0, w: 3, h: 2, minW: 2, minH: 1 },
          { i: 'characterSheet', x: 0, y: 2, w: 6, h: 4, minW: 4, minH: 3 },
          { i: 'clock', x: 9, y: 2, w: 3, h: 2, minW: 2, minH: 1 },
        ],
        md: [
          { i: 'stats', x: 0, y: 0, w: 3, h: 2, minW: 2, minH: 1 },
          { i: 'notes', x: 3, y: 0, w: 5, h: 4, minW: 3, minH: 2 },
          { i: 'diceRoller', x: 8, y: 0, w: 2, h: 2, minW: 2, minH: 1 },
          { i: 'characterSheet', x: 0, y: 2, w: 5, h: 4, minW: 4, minH: 3 },
          { i: 'clock', x: 8, y: 2, w: 2, h: 2, minW: 2, minH: 1 },
        ],
        sm: [
          { i: 'stats', x: 0, y: 0, w: 3, h: 2, minW: 2, minH: 1 },
          { i: 'notes', x: 3, y: 0, w: 3, h: 4, minW: 3, minH: 2 },
          { i: 'diceRoller', x: 0, y: 2, w: 3, h: 2, minW: 2, minH: 1 },
          { i: 'characterSheet', x: 0, y: 4, w: 6, h: 4, minW: 4, minH: 3 },
          { i: 'clock', x: 3, y: 2, w: 3, h: 2, minW: 2, minH: 1 },
        ],
      },
      isDefault: true,
    });
    
    console.log(`Created test dashboard: ${dashboard.name}`);
    
    // Create test widgets
    const widgets = await Widget.create([
      {
        userId: user._id,
        widgetId: 'stats',
        name: 'Game Stats',
        type: 'stats',
        config: {},
        active: true,
      },
      {
        userId: user._id,
        widgetId: 'notes',
        name: 'Notes',
        type: 'notes',
        config: {},
        active: true,
      },
      {
        userId: user._id,
        widgetId: 'diceRoller',
        name: 'Dice Roller',
        type: 'diceRoller',
        config: {},
        active: true,
      },
      {
        userId: user._id,
        widgetId: 'characterSheet',
        name: 'Character Sheet',
        type: 'characterSheet',
        config: {},
        active: true,
      },
      {
        userId: user._id,
        widgetId: 'clock',
        name: 'Clock',
        type: 'clock',
        config: {
          format: '24h',
          showSeconds: true,
          showDate: true,
          blinkingSeparator: true,
        },
        active: true,
      },
    ]);
    
    console.log(`Created ${widgets.length} test widgets`);
    
    console.log('Database seeded successfully');
  } catch (error) {
    console.error('Error seeding database:', error);
  } finally {
    // Disconnect from MongoDB
    await disconnectFromMongoDB();
    console.log('Disconnected from MongoDB');
  }
}

// Run the seed function
seedDatabase();
