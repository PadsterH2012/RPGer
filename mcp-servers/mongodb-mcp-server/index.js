import { MongoClient, ObjectId } from 'mongodb';
import fs from 'fs';
import path from 'path';

// Manual .env parsing
function loadEnv() {
  const envPath = path.resolve('.env');
  const env = {};
  try {
    const envContents = fs.readFileSync(envPath, 'utf8');
    envContents.split('\n').forEach(line => {
      const trimmedLine = line.trim();
      if (trimmedLine && !trimmedLine.startsWith('#')) {
        const [key, value] = trimmedLine.split('=');
        env[key.trim()] = value.trim().replace(/^["']|["']$/g, '');
      }
    });
  } catch (error) {
    console.warn('Could not read .env file:', error.message);
  }
  return env;
}

const env = loadEnv();

class MongoDBMCPServer {
  constructor(connectionString, options = {}) {
    this.connectionString = connectionString;
    this.options = options;
    this.client = null;
    this.db = null;
  }

  async connect() {
    try {
      this.client = new MongoClient(this.connectionString, this.options);
      await this.client.connect();
      this.db = this.client.db('rpger');
      console.log('Connected to MongoDB');
      return this.client;
    } catch (error) {
      console.error('Failed to connect to MongoDB:', error);
      throw error;
    }
  }

  async listCollections() {
    if (!this.db) await this.connect();
    return await this.db.listCollections().toArray();
  }

  async listDocuments(collectionName, query = {}, options = { limit: 100 }) {
    if (!this.db) await this.connect();
    const collection = this.db.collection(collectionName);
    return await collection.find(query, options).toArray();
  }

  async createDocument(collectionName, document) {
    if (!this.db) await this.connect();
    const collection = this.db.collection(collectionName);
    return await collection.insertOne(document);
  }

  async updateDocument(collectionName, filter, update, options = {}) {
    if (!this.db) await this.connect();
    const collection = this.db.collection(collectionName);
    return await collection.updateOne(filter, { $set: update }, options);
  }

  async deleteDocument(collectionName, filter) {
    if (!this.db) await this.connect();
    const collection = this.db.collection(collectionName);
    return await collection.deleteOne(filter);
  }

  async findDocumentById(collectionName, id) {
    if (!this.db) await this.connect();
    const collection = this.db.collection(collectionName);
    return await collection.findOne({ _id: new ObjectId(id) });
  }

  async close() {
    if (this.client) {
      await this.client.close();
      console.log('Disconnected from MongoDB');
    }
  }
}

async function main() {
  // Use environment variables for connection
  const uri = env.MONGODB_URI || 'mongodb://localhost:27017/rpger';
  
  // Prepare connection options
  const options = {
    authSource: env.MONGODB_AUTH_SOURCE || 'admin',
  };

  const server = new MongoDBMCPServer(uri, options);

  try {
    await server.connect();
    
    // Example operations (can be customized based on specific needs)
    console.log('Available Collections:');
    const collections = await server.listCollections();
    collections.forEach(collection => console.log(collection.name));

    // Uncomment and modify as needed for specific operations
    // const monsters = await server.listDocuments('monsters');
    // console.log('Monsters:', monsters);

  } catch (error) {
    console.error('Error:', error);
  } finally {
    await server.close();
  }
}

// Export the server class for use in other modules
export default MongoDBMCPServer;

// Only run main if this file is being run directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(console.error);
}