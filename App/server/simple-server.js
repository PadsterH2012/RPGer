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

// Define CORS options
const corsOptions = {
  origin: ['http://localhost:3000', 'http://localhost:3001', 'http://localhost:3002', 'http://localhost:3003'],
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true
};

// Set up Socket.IO
const io = new Server(server, {
  cors: corsOptions,
});

// Middleware
app.use(cors(corsOptions));
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
  // Log the request
  console.log(`Health check request received from ${req.ip}`);

  // Set CORS headers explicitly
  res.header('Access-Control-Allow-Origin', '*');
  res.header('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  // Send response
  res.status(200).json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    message: 'Server is running correctly'
  });
});

// Test endpoint
app.get('/api/test', (req, res) => {
  res.status(200).json({
    message: 'Test endpoint working',
    timestamp: new Date().toISOString()
  });
});

// Root route
app.get('/', (req, res) => {
  res.send(`
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <title>RPGer Dashboard Server</title>
      <style>
        body {
          font-family: Arial, sans-serif;
          max-width: 800px;
          margin: 0 auto;
          padding: 20px;
          line-height: 1.6;
          color: #333;
        }
        h1 {
          color: #6200ee;
          border-bottom: 2px solid #6200ee;
          padding-bottom: 10px;
        }
        h2 {
          color: #3700b3;
          margin-top: 30px;
        }
        code {
          background-color: #f5f5f5;
          padding: 2px 5px;
          border-radius: 3px;
          font-family: monospace;
        }
        pre {
          background-color: #f5f5f5;
          padding: 15px;
          border-radius: 5px;
          overflow-x: auto;
        }
        .endpoint {
          margin-bottom: 20px;
          border-left: 3px solid #6200ee;
          padding-left: 15px;
        }
      </style>
    </head>
    <body>
      <h1>RPGer Dashboard Server</h1>
      <p>This is the API server for the RPGer Dashboard. It provides endpoints for the dashboard to interact with.</p>

      <h2>Available Endpoints</h2>

      <div class="endpoint">
        <h3>Health Check</h3>
        <code>GET /api/health</code>
        <p>Returns the server status and current timestamp.</p>
        <pre>{
  "status": "ok",
  "timestamp": "${new Date().toISOString()}"
}</pre>
      </div>

      <h2>Socket.IO Events</h2>
      <p>This server also supports real-time communication via Socket.IO. The following events are available:</p>

      <ul>
        <li><code>player:requestStats</code> - Request player statistics</li>
        <li><code>character:request</code> - Request character data</li>
        <li><code>widgets:sync</code> - Synchronize widget state</li>
        <li><code>widgets:add</code> - Add a widget</li>
        <li><code>widgets:remove</code> - Remove a widget</li>
        <li><code>widgets:updateConfig</code> - Update widget configuration</li>
        <li><code>widget:requestData</code> - Request data for a widget</li>
        <li><code>dice:roll</code> - Roll dice</li>
      </ul>

      <h2>Running the Client</h2>
      <p>To run the client, navigate to the client directory and run:</p>
      <pre>npm start</pre>
      <p>The client will connect to this server automatically.</p>
    </body>
    </html>
  `);
});

// Start server
const PORT = process.env.PORT || 5001;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Open http://localhost:${PORT} in your browser to view the server status page`);
});
