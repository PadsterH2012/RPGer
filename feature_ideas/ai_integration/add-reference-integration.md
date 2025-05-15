# AD&D 1st Edition Reference Integration (May 2025)

## Feature Request

Integrate AD&D 1st Edition reference materials (Dungeon Masters Guide, Players Handbook, and Monster Manual) into the RPG agent system to make the content easily accessible to the various specialized agents. The system should leverage modern retrieval technologies to provide accurate and efficient access to rules, spells, monsters, and other game content.

## Decision

After evaluating multiple approaches, a **three-tier hybrid architecture** is recommended for a homelab environment with existing MongoDB and Redis containers.

## Recommended Approach

A **three-tier hybrid architecture** leveraging existing MongoDB and Redis containers with an additional Chroma container:

1. **Primary Storage: MongoDB with Vector Search**
   - Store structured rulebook content with hierarchical organization
   - Support exact lookups and metadata filtering
   - Enable semantic search for natural language queries

2. **Vector Search: Chroma in Docker Container**
   - Add a dedicated Chroma container to existing infrastructure
   - Optimize for specialized semantic search capabilities
   - Handle complex natural language queries about rules and content

3. **Caching Layer: Redis with Vector Sets**
   - Utilize existing Redis container for high-speed caching
   - Implement semantic caching for frequently accessed content
   - Optimize for real-time gameplay with low-latency requirements

4. **Agent-Specific Retrievers**
   - Create specialized retrievers for each agent type (Combat, Character, DM, etc.)
   - Implement hybrid search combining exact and semantic approaches
   - Optimize context management for token efficiency

## Implementation Plan

1. **Phase 1: Infrastructure Setup (2 weeks)**
   - Configure MongoDB with vector search capabilities
   - Set up Chroma container alongside existing infrastructure
   - Design schema for rulebook content with embedding fields
   - Create appropriate indices for efficient retrieval
   - Configure persistent storage volumes for all database containers

2. **Phase 2: Data Processing (3 weeks)**
   - Process markdown files into appropriate chunks
   - Generate embeddings for semantic search
   - Migrate content to MongoDB with metadata preservation
   - Create secondary indices in Chroma for specialized queries
   - Configure Redis for frequently accessed content
   - Implement initial database backup process

3. **Phase 3: Retrieval Implementation (2 weeks)**
   - Implement RAG patterns for each agent type
   - Create specialized retrievers for different content types
   - Set up orchestration for complex retrieval workflows
   - Configure semantic caching for common queries
   - Create database dump scripts for preseeding containers

4. **Phase 4: Agent Integration (2 weeks)**
   - Update agent prompts to utilize the new reference system
   - Implement agent-specific retrieval strategies
   - Create hybrid search functionality
   - Configure synchronization between storage tiers
   - Set up automated backup schedule

5. **Phase 5: Testing and Refinement (1 week)**
   - Test retrieval accuracy across different query types
   - Benchmark performance across all storage tiers
   - Optimize embedding strategies and chunk sizes
   - Refine search algorithms based on usage patterns
   - Validate backup and restore procedures

## Database Persistence Strategy

To ensure data persistence and enable container rebuilds with preseeded data:

1. **Permanent Database Stack**
   - Deploy MongoDB, Redis, and Chroma as a permanent database stack
   - Configure with persistent volume mounts to preserve data across restarts
   - Separate this stack from the application frontend and backend
   - Use Docker Compose or Kubernetes for orchestration

2. **Backup Automation**
   - Implement scheduled MongoDB dumps using `mongodump`
   - Create Redis RDB snapshots at regular intervals
   - Back up Chroma's persistent storage directory
   - Store backups in a designated backup volume

3. **Preseeding Mechanism**
   - Create initialization scripts that detect empty databases
   - Automatically restore from latest backups when containers are rebuilt
   - Include version control for database schemas and migrations
   - Document the restore process for manual intervention if needed

4. **Application Connection**
   - Configure frontend and backend to connect to the database stack via internal network
   - Use environment variables for connection strings to facilitate changes
   - Implement connection pooling and retry logic for resilience
   - Add health checks to verify database connectivity
