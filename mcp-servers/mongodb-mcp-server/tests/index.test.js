const { MongoClient } = require('mongodb');
const config = require('../config');

describe('MongoDB MCP Server', () => {
  let connection;
  let db;

  beforeAll(async () => {
    // Establish connection before tests
    connection = await MongoClient.connect(config.mongodb.uri, config.mongodb.options);
    db = connection.db(config.mongodb.dbName);
  });

  afterAll(async () => {
    // Close connection after tests
    await connection.close();
  });

  describe('Database Connection', () => {
    test('should connect to MongoDB', () => {
      expect(connection).toBeTruthy();
      expect(db).toBeTruthy();
    });

    test('should have the correct database name', () => {
      expect(db.databaseName).toBe(config.mongodb.dbName);
    });
  });

  describe('Collection Operations', () => {
    const testCollectionName = 'test_collection';
    
    beforeEach(async () => {
      // Clear the test collection before each test
      await db.collection(testCollectionName).deleteMany({});
    });

    test('should insert a document', async () => {
      const collection = db.collection(testCollectionName);
      const testDoc = { name: 'Test Character', level: 1 };
      
      const result = await collection.insertOne(testDoc);
      
      expect(result.acknowledged).toBe(true);
      expect(result.insertedId).toBeTruthy();
    });

    test('should find a document', async () => {
      const collection = db.collection(testCollectionName);
      const testDoc = { name: 'Search Character', level: 5 };
      
      await collection.insertOne(testDoc);
      
      const foundDoc = await collection.findOne({ name: 'Search Character' });
      
      expect(foundDoc).toBeTruthy();
      expect(foundDoc.name).toBe('Search Character');
      expect(foundDoc.level).toBe(5);
    });

    test('should update a document', async () => {
      const collection = db.collection(testCollectionName);
      const testDoc = { name: 'Update Character', level: 3 };
      
      const insertResult = await collection.insertOne(testDoc);
      
      const updateResult = await collection.updateOne(
        { _id: insertResult.insertedId },
        { $set: { level: 4 } }
      );
      
      expect(updateResult.modifiedCount).toBe(1);
      
      const updatedDoc = await collection.findOne({ _id: insertResult.insertedId });
      expect(updatedDoc.level).toBe(4);
    });

    test('should delete a document', async () => {
      const collection = db.collection(testCollectionName);
      const testDoc = { name: 'Delete Character', level: 2 };
      
      const insertResult = await collection.insertOne(testDoc);
      
      const deleteResult = await collection.deleteOne({ _id: insertResult.insertedId });
      
      expect(deleteResult.deletedCount).toBe(1);
      
      const foundDoc = await collection.findOne({ _id: insertResult.insertedId });
      expect(foundDoc).toBeNull();
    });
  });

  describe('Configuration', () => {
    test('should have valid MongoDB configuration', () => {
      expect(config.mongodb).toBeTruthy();
      expect(config.mongodb.uri).toBeTruthy();
      expect(config.mongodb.dbName).toBe('rpger');
    });

    test('should have valid server configuration', () => {
      expect(config.server).toBeTruthy();
      expect(config.server.name).toBe('mongodb-rpger');
      expect(config.server.port).toBeTruthy();
    });
  });
});