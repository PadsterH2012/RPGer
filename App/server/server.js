/**
 * Simple Express server for RPGer Dashboard
 */

const express = require('express');
const http = require('http');
const cors = require('cors');
const { Server } = require('socket.io');

// Create Express app
const app = express();
const server = http.createServer(app);

// Set up Socket.IO
const io = new Server(server, {
  cors: {
    origin: 'http://localhost:3000',
    methods: ['GET', 'POST'],
    credentials: true,
  },
});

// Middleware
app.use(cors());
app.use(express.json());

// Sample player stats
const samplePlayerStats = {
  hp: {
    current: 25,
    maximum: 30,
  },
  level: 3,
  experience: 2500,
  next_level_xp: 4000,
  armor_class: 15,
};

// Sample character data
const sampleCharacter = {
  name: 'Thalion',
  race: 'Human',
  class: 'Fighter',
  level: 3,
  abilities: {
    strength: 16,
    dexterity: 14,
    constitution: 15,
    intelligence: 12,
    wisdom: 10,
    charisma: 13
  },
  equipment: [
    { name: 'Longsword', type: 'Weapon', details: '1d8 slashing' },
    { name: 'Chain Mail', type: 'Armor', details: 'AC 16' },
    { name: 'Shield', type: 'Armor', details: '+2 AC' },
    { name: 'Backpack', type: 'Gear', details: 'Contains adventuring gear' }
  ],
  spells: [],
  skills: {
    'Athletics': 5,
    'Intimidation': 3,
    'Perception': 2,
    'Survival': 2
  }
};

// In-memory widget state
const widgetState = {
  activeWidgets: [],
  configs: {},
};

// Socket.IO connection handler
io.on('connection', (socket) => {
  console.log(`Client connected: ${socket.id}`);
  
  // Handle player stats request
  socket.on('player:requestStats', () => {
    console.log(`User ${socket.id} requested player stats`);
    socket.emit('player:statsUpdate', samplePlayerStats);
  });
  
  // Handle character request
  socket.on('character:request', () => {
    console.log(`User ${socket.id} requested character data`);
    socket.emit('character:update', sampleCharacter);
  });
  
  // Handle widget sync
  socket.on('widgets:sync', (data) => {
    console.log(`User ${socket.id} synced widget state`);
    
    // Update widget state
    widgetState.activeWidgets = data.activeWidgets || [];
    widgetState.configs = data.configs || {};
    
    // Join rooms for each active widget
    widgetState.activeWidgets.forEach(widgetId => {
      socket.join(`widget:${widgetId}`);
    });
  });
  
  // Handle widget add
  socket.on('widgets:add', (data) => {
    console.log(`User ${socket.id} added widget: ${data.widgetId}`);
    
    // Add widget to active widgets
    if (!widgetState.activeWidgets.includes(data.widgetId)) {
      widgetState.activeWidgets.push(data.widgetId);
    }
    
    // Add widget config if provided
    if (data.config) {
      widgetState.configs[data.widgetId] = data.config;
    }
    
    // Join room for the widget
    socket.join(`widget:${data.widgetId}`);
  });
  
  // Handle widget remove
  socket.on('widgets:remove', (data) => {
    console.log(`User ${socket.id} removed widget: ${data.widgetId}`);
    
    // Remove widget from active widgets
    widgetState.activeWidgets = widgetState.activeWidgets.filter(id => id !== data.widgetId);
    
    // Remove widget config
    delete widgetState.configs[data.widgetId];
    
    // Leave room for the widget
    socket.leave(`widget:${data.widgetId}`);
  });
  
  // Handle widget config update
  socket.on('widgets:updateConfig', (data) => {
    console.log(`User ${socket.id} updated widget config: ${data.widgetId}`);
    
    // Update widget config
    widgetState.configs[data.widgetId] = {
      ...widgetState.configs[data.widgetId],
      ...data.config,
    };
    
    // Broadcast config update to other users in the widget room
    socket.to(`widget:${data.widgetId}`).emit('widgets:configUpdate', {
      widgetId: data.widgetId,
      config: widgetState.configs[data.widgetId],
    });
  });
  
  // Handle widget data request
  socket.on('widget:requestData', (data) => {
    console.log(`User ${socket.id} requested data for widget: ${data.widgetId}`);
    
    // Generate sample data based on data source
    let sampleData = [];
    
    switch (data.dataSource) {
      case 'characters':
        sampleData = [
          { id: 1, name: 'Aragorn', class: 'Ranger', level: 8 },
          { id: 2, name: 'Gandalf', class: 'Wizard', level: 15 },
          { id: 3, name: 'Legolas', class: 'Ranger', level: 7 },
          { id: 4, name: 'Gimli', class: 'Fighter', level: 6 },
          { id: 5, name: 'Frodo', class: 'Rogue', level: 4 },
        ];
        break;
      case 'inventory':
        sampleData = [
          { id: 1, name: 'Healing Potion', quantity: 5, value: 50 },
          { id: 2, name: 'Longsword', quantity: 1, value: 15 },
          { id: 3, name: 'Chain Mail', quantity: 1, value: 75 },
          { id: 4, name: 'Rations', quantity: 10, value: 5 },
          { id: 5, name: 'Rope', quantity: 1, value: 1 },
        ];
        break;
      default:
        sampleData = [
          { id: 1, name: 'Item 1', value: 100 },
          { id: 2, name: 'Item 2', value: 200 },
          { id: 3, name: 'Item 3', value: 300 },
          { id: 4, name: 'Item 4', value: 400 },
          { id: 5, name: 'Item 5', value: 500 },
        ];
    }
    
    // Send data to the client
    socket.emit('widget:tableData', {
      widgetId: data.widgetId,
      data: sampleData,
    });
  });
  
  // Handle dice roll
  socket.on('dice:roll', (roll) => {
    console.log(`User ${socket.id} rolled dice: ${JSON.stringify(roll)}`);
    
    // Broadcast dice roll to other users
    socket.broadcast.emit('dice:roll', roll);
  });
  
  // Handle disconnection
  socket.on('disconnect', () => {
    console.log(`Client disconnected: ${socket.id}`);
  });
});

// API routes
app.get('/api/health', (req, res) => {
  res.status(200).json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Start server
const PORT = process.env.PORT || 5000;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
