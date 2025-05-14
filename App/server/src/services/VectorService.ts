/**
 * Vector Database Service
 * 
 * A simple in-memory vector database service with Redis persistence.
 * For production, consider using a dedicated vector database like Pinecone, Weaviate, or Qdrant.
 */

import { getRedisClient } from '../config/redis';
import { logger } from '../utils/logger';

interface VectorItem {
  id: string;
  vector: number[];
  metadata: Record<string, any>;
}

interface SearchResult {
  id: string;
  score: number;
  metadata: Record<string, any>;
}

class VectorService {
  private collections: Map<string, VectorItem[]> = new Map();
  
  /**
   * Create a new collection
   * 
   * @param collectionName Collection name
   * @returns Boolean indicating success
   */
  public createCollection(collectionName: string): boolean {
    if (this.collections.has(collectionName)) {
      logger.warn(`Collection ${collectionName} already exists`);
      return false;
    }
    
    this.collections.set(collectionName, []);
    logger.info(`Created collection ${collectionName}`);
    
    // Persist to Redis if available
    this.persistCollection(collectionName);
    
    return true;
  }
  
  /**
   * Delete a collection
   * 
   * @param collectionName Collection name
   * @returns Boolean indicating success
   */
  public deleteCollection(collectionName: string): boolean {
    if (!this.collections.has(collectionName)) {
      logger.warn(`Collection ${collectionName} does not exist`);
      return false;
    }
    
    this.collections.delete(collectionName);
    logger.info(`Deleted collection ${collectionName}`);
    
    // Remove from Redis if available
    const redisClient = getRedisClient();
    if (redisClient) {
      redisClient.del(`vector:collection:${collectionName}`).catch((err) => {
        logger.error(`Error deleting collection from Redis: ${err}`);
      });
    }
    
    return true;
  }
  
  /**
   * Insert a vector into a collection
   * 
   * @param collectionName Collection name
   * @param item Vector item
   * @returns Boolean indicating success
   */
  public insertVector(collectionName: string, item: VectorItem): boolean {
    if (!this.collections.has(collectionName)) {
      logger.warn(`Collection ${collectionName} does not exist`);
      return false;
    }
    
    const collection = this.collections.get(collectionName)!;
    
    // Check if item with same ID already exists
    const existingIndex = collection.findIndex((i) => i.id === item.id);
    if (existingIndex !== -1) {
      // Replace existing item
      collection[existingIndex] = item;
    } else {
      // Add new item
      collection.push(item);
    }
    
    // Persist to Redis if available
    this.persistCollection(collectionName);
    
    return true;
  }
  
  /**
   * Delete a vector from a collection
   * 
   * @param collectionName Collection name
   * @param id Vector ID
   * @returns Boolean indicating success
   */
  public deleteVector(collectionName: string, id: string): boolean {
    if (!this.collections.has(collectionName)) {
      logger.warn(`Collection ${collectionName} does not exist`);
      return false;
    }
    
    const collection = this.collections.get(collectionName)!;
    const initialLength = collection.length;
    
    // Filter out the item with the given ID
    const newCollection = collection.filter((item) => item.id !== id);
    this.collections.set(collectionName, newCollection);
    
    // Persist to Redis if available
    this.persistCollection(collectionName);
    
    return newCollection.length < initialLength;
  }
  
  /**
   * Search for similar vectors in a collection
   * 
   * @param collectionName Collection name
   * @param queryVector Query vector
   * @param limit Maximum number of results
   * @param threshold Similarity threshold (0-1)
   * @returns Array of search results
   */
  public searchVectors(
    collectionName: string,
    queryVector: number[],
    limit: number = 10,
    threshold: number = 0.7
  ): SearchResult[] {
    if (!this.collections.has(collectionName)) {
      logger.warn(`Collection ${collectionName} does not exist`);
      return [];
    }
    
    const collection = this.collections.get(collectionName)!;
    
    // Calculate cosine similarity for each vector
    const results = collection.map((item) => {
      const similarity = this.cosineSimilarity(queryVector, item.vector);
      return {
        id: item.id,
        score: similarity,
        metadata: item.metadata,
      };
    });
    
    // Filter by threshold and sort by similarity (descending)
    return results
      .filter((result) => result.score >= threshold)
      .sort((a, b) => b.score - a.score)
      .slice(0, limit);
  }
  
  /**
   * Load collections from Redis
   */
  public async loadFromRedis(): Promise<void> {
    const redisClient = getRedisClient();
    if (!redisClient) {
      logger.warn('Redis client not available, skipping collection loading');
      return;
    }
    
    try {
      // Get all collection keys
      const keys = await redisClient.keys('vector:collection:*');
      
      for (const key of keys) {
        const collectionName = key.replace('vector:collection:', '');
        const data = await redisClient.get(key);
        
        if (data) {
          try {
            const items = JSON.parse(data) as VectorItem[];
            this.collections.set(collectionName, items);
            logger.info(`Loaded collection ${collectionName} from Redis with ${items.length} items`);
          } catch (error) {
            logger.error(`Error parsing collection data for ${collectionName}: ${error}`);
          }
        }
      }
    } catch (error) {
      logger.error(`Error loading collections from Redis: ${error}`);
    }
  }
  
  /**
   * Persist a collection to Redis
   * 
   * @param collectionName Collection name
   */
  private persistCollection(collectionName: string): void {
    const redisClient = getRedisClient();
    if (!redisClient) {
      return;
    }
    
    const collection = this.collections.get(collectionName);
    if (!collection) {
      return;
    }
    
    redisClient
      .set(`vector:collection:${collectionName}`, JSON.stringify(collection))
      .catch((err) => {
        logger.error(`Error persisting collection to Redis: ${err}`);
      });
  }
  
  /**
   * Calculate cosine similarity between two vectors
   * 
   * @param a First vector
   * @param b Second vector
   * @returns Cosine similarity (0-1)
   */
  private cosineSimilarity(a: number[], b: number[]): number {
    if (a.length !== b.length) {
      throw new Error('Vectors must have the same length');
    }
    
    let dotProduct = 0;
    let normA = 0;
    let normB = 0;
    
    for (let i = 0; i < a.length; i++) {
      dotProduct += a[i] * b[i];
      normA += a[i] * a[i];
      normB += b[i] * b[i];
    }
    
    if (normA === 0 || normB === 0) {
      return 0;
    }
    
    return dotProduct / (Math.sqrt(normA) * Math.sqrt(normB));
  }
}

// Export singleton instance
export const vectorService = new VectorService();
