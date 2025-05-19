/**
 * MongoDB MCP Server Configuration
 */

module.exports = {
  // MongoDB connection settings
  mongodb: {
    uri: 'mongodb://localhost:27017',
    dbName: 'rpger',
    options: {
      useNewUrlParser: true,
      useUnifiedTopology: true
    }
  },
  
  // MCP server settings
  server: {
    name: 'mongodb-rpger',
    description: 'MCP server for MongoDB integration with RPGer',
    version: '1.0.0',
    port: process.env.MCP_SERVER_PORT || 3100
  },
  
  // Tool settings
  tools: {
    queryCollection: {
      defaultLimit: 10,
      maxLimit: 100
    }
  },
  
  // Logging settings
  logging: {
    level: process.env.LOG_LEVEL || 'info'
  }
};