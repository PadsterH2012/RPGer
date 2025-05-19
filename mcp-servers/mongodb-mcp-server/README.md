# RPGer MongoDB MCP Server

## Overview

This is a Model Context Protocol (MCP) server designed to provide seamless MongoDB integration for the RPGer application. It offers a robust set of tools for interacting with the MongoDB database, supporting various operations like querying, inserting, updating, and deleting documents.

## Features

- 🔌 Seamless MongoDB Connection
- 🛠️ Comprehensive CRUD Operations
- 🔒 Configurable Connection Settings
- 📊 Flexible Query Tools
- 🧪 Comprehensive Test Suite

## Prerequisites

- Node.js (v14.0.0 or later)
- MongoDB (v4.4 or later)
- npm (v6.0.0 or later)

## Installation

1. Clone the repository
```bash
git clone <repository-url>
cd mcp-servers/mongodb-mcp-server
```

2. Install dependencies
```bash
npm install
```

## Configuration

The server uses a flexible configuration system. Modify `config.js` to customize:

```javascript
module.exports = {
  mongodb: {
    uri: 'mongodb://localhost:27017',
    dbName: 'rpger',
    options: { /* MongoDB connection options */ }
  },
  server: {
    name: 'mongodb-rpger',
    port: 3100
  }
};
```

## Available Tools

### 1. `query_collection`
Query documents from a MongoDB collection.

**Parameters:**
- `collection`: Collection name
- `query`: MongoDB query object
- `limit`: Maximum documents to return
- `skip`: Number of documents to skip
- `sort`: Sorting criteria

### 2. `get_document`
Retrieve a single document by ID.

**Parameters:**
- `collection`: Collection name
- `id`: Document ID

### 3. `insert_document`
Insert a new document into a collection.

**Parameters:**
- `collection`: Collection name
- `document`: Document to insert

### 4. `update_document`
Update an existing document.

**Parameters:**
- `collection`: Collection name
- `id`: Document ID
- `update`: Update operations

### 5. `delete_document`
Delete a document from a collection.

**Parameters:**
- `collection`: Collection name
- `id`: Document ID

### 6. `list_collections`
List all collections in the database.

## Running the Server

### Development
```bash
npm run start:dev
```

### Production
```bash
npm start
```

## Testing

Run the test suite with:
```bash
npm test
```

## Logging

Logging is configured in `config.js`. Adjust the logging level as needed.

## Error Handling

The server provides detailed error responses for all operations.

## Security

- Ensure MongoDB connection is secure
- Use environment variables for sensitive information
- Implement proper access controls

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License

## Contact

RPGer Development Team