/**
 * RPGer MongoDB MCP Server Integration
 * 
 * This file demonstrates how to integrate the MongoDB MCP server
 * with the RPGer application backend.
 */

// Import required modules
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

/**
 * Class to manage the MongoDB MCP server integration with RPGer
 */
class MongoDBMCPIntegration {
  constructor() {
    this.serverProcess = null;
    this.serverPath = path.join(__dirname);
    this.isRunning = false;
  }

  /**
   * Start the MongoDB MCP server
   * @returns {Promise<boolean>} True if server started successfully
   */
  async startServer() {
    return new Promise((resolve, reject) => {
      if (this.isRunning) {
        console.log('MongoDB MCP server is already running');
        return resolve(true);
      }

      console.log('Starting MongoDB MCP server...');
      
      // Check if the server files exist
      if (!fs.existsSync(path.join(this.serverPath, 'index.js'))) {
        return reject(new Error('MongoDB MCP server files not found'));
      }

      // Start the server process
      this.serverProcess = spawn('node', ['index.js'], {
        cwd: this.serverPath,
        stdio: ['ignore', 'pipe', 'pipe']
      });

      // Handle server output
      this.serverProcess.stdout.on('data', (data) => {
        const output = data.toString().trim();
        console.log(`[MongoDB MCP] ${output}`);
        
        // Check for server started message
        if (output.includes('MongoDB MCP server started')) {
          this.isRunning = true;
          resolve(true);
        }
      });

      // Handle server errors
      this.serverProcess.stderr.on('data', (data) => {
        console.error(`[MongoDB MCP Error] ${data.toString().trim()}`);
      });

      // Handle server exit
      this.serverProcess.on('close', (code) => {
        this.isRunning = false;
        console.log(`MongoDB MCP server exited with code ${code}`);
        
        if (code !== 0) {
          reject(new Error(`MongoDB MCP server exited with code ${code}`));
        }
      });

      // Set a timeout for server startup
      setTimeout(() => {
        if (!this.isRunning) {
          reject(new Error('MongoDB MCP server failed to start within timeout'));
        }
      }, 10000); // 10 seconds timeout
    });
  }

  /**
   * Stop the MongoDB MCP server
   */
  stopServer() {
    if (this.serverProcess && this.isRunning) {
      console.log('Stopping MongoDB MCP server...');
      this.serverProcess.kill();
      this.isRunning = false;
    }
  }

  /**
   * Check if the MongoDB MCP server is running
   * @returns {boolean} True if server is running
   */
  isServerRunning() {
    return this.isRunning;
  }
}

/**
 * Example usage in RPGer backend
 */
async function integrateWithRPGer() {
  // Create the integration instance
  const mcpIntegration = new MongoDBMCPIntegration();
  
  try {
    // Start the MongoDB MCP server
    await mcpIntegration.startServer();
    console.log('MongoDB MCP server started successfully');
    
    // Register shutdown handler
    process.on('SIGINT', () => {
      console.log('Shutting down...');
      mcpIntegration.stopServer();
      process.exit(0);
    });
    
    // Your RPGer backend code here...
    console.log('RPGer backend is now connected to MongoDB MCP server');
    
  } catch (error) {
    console.error('Failed to start MongoDB MCP server:', error);
  }
}

// Export the integration class
module.exports = {
  MongoDBMCPIntegration,
  integrateWithRPGer
};

// Example usage:
// const { integrateWithRPGer } = require('./rpger-integration');
// integrateWithRPGer();