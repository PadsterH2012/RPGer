// Jest setup file for MongoDB MCP Server

// Mock environment variables
process.env.NODE_ENV = 'test';

// Global test configuration
global.testConfig = {
  mongodb: {
    uri: 'mongodb://localhost:27017',
    dbName: 'rpger_test'
  }
};

// Optional: Add global mocks or test utilities
beforeAll(() => {
  // Global setup before all tests
  console.log('Starting test suite for MongoDB MCP Server');
});

afterAll(() => {
  // Global cleanup after all tests
  console.log('Completed test suite for MongoDB MCP Server');
});

// Optional: Add error handling for unhandled promises
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  // Optionally throw an error to fail the test
  throw reason;
});