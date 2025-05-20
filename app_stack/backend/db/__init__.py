"""
Database initialization and connection management.
"""

import os
import logging
import pymongo
import chromadb
from pymongo import MongoClient
from chromadb.config import Settings

# Configure logging
logger = logging.getLogger(__name__)

# Get MongoDB connection parameters from environment variables
def get_mongodb_connection_params():
    """Get MongoDB connection parameters from environment variables with defaults"""
    return {
        'uri': os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/rpger'),
        'connect_timeout_ms': int(os.environ.get('MONGODB_CONNECT_TIMEOUT_MS', 10000)),
        'socket_timeout_ms': int(os.environ.get('MONGODB_SOCKET_TIMEOUT_MS', 10000)),
        'server_selection_timeout_ms': int(os.environ.get('MONGODB_SERVER_SELECTION_TIMEOUT_MS', 10000)),
        'max_pool_size': int(os.environ.get('MONGODB_MAX_POOL_SIZE', 50)),
        'min_pool_size': int(os.environ.get('MONGODB_MIN_POOL_SIZE', 5)),
        'max_idle_time_ms': int(os.environ.get('MONGODB_MAX_IDLE_TIME_MS', 60000))
    }

# MongoDB connection
def get_mongodb_client():
    """Get a MongoDB client instance."""
    # Get connection parameters
    mongo_params = get_mongodb_connection_params()
    uri = mongo_params['uri']

    # Mask password in logs
    masked_uri = uri
    if '@' in uri:
        prefix = uri.split('@')[0]
        suffix = uri.split('@')[1]
        if ':' in prefix:
            masked_uri = f"{prefix.split(':')[0]}:***@{suffix}"

    try:
        logger.info(f"Attempting to connect to MongoDB with URI: {masked_uri}")

        # Create MongoDB client with connection parameters
        client = MongoClient(
            uri,
            serverSelectionTimeoutMS=mongo_params['server_selection_timeout_ms'],
            connectTimeoutMS=mongo_params['connect_timeout_ms'],
            socketTimeoutMS=mongo_params['socket_timeout_ms'],
            maxPoolSize=mongo_params['max_pool_size'],
            minPoolSize=mongo_params['min_pool_size'],
            maxIdleTimeMS=mongo_params['max_idle_time_ms'],
            retryWrites=True,
            retryReads=True
        )

        # Verify connection
        client.server_info()
        logger.info(f"Successfully connected to MongoDB at {masked_uri}")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")

        # Provide troubleshooting information
        troubleshooting = (
            "MongoDB connection failed. Please check:\n"
            "1. MongoDB service is running\n"
            "2. Network connectivity to MongoDB server\n"
            "3. Authentication credentials are correct\n"
            "4. Firewall settings allow connections\n"
            "5. MongoDB server is listening on the expected port\n"
            "6. MONGODB_URI environment variable is set correctly"
        )
        logger.error(troubleshooting)
        raise

def get_mongodb_database():
    """Get the MongoDB database instance."""
    client = get_mongodb_client()
    db_name = os.environ.get('MONGODB_DATABASE', 'rpger')
    return client[db_name]

# Get Chroma connection parameters from environment variables
def get_chroma_connection_params():
    """Get Chroma connection parameters from environment variables with defaults"""
    return {
        'host': os.environ.get('CHROMA_HOST', 'localhost'),
        'port': os.environ.get('CHROMA_PORT', '8000'),
        'ssl': os.environ.get('CHROMA_SSL', 'false').lower() == 'true',
        'headers': {}  # Can be extended for authentication if needed
    }

# Chroma connection
def get_chroma_client():
    """Get a Chroma client instance."""
    # Get connection parameters
    chroma_params = get_chroma_connection_params()

    try:
        logger.info(f"Attempting to connect to Chroma at {chroma_params['host']}:{chroma_params['port']}")

        # Create Chroma client
        client = chromadb.HttpClient(
            host=chroma_params['host'],
            port=chroma_params['port'],
            ssl=chroma_params['ssl'],
            headers=chroma_params['headers']
        )

        # Verify connection
        client.heartbeat()
        logger.info(f"Successfully connected to Chroma at {chroma_params['host']}:{chroma_params['port']}")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Chroma: {e}")

        # Provide troubleshooting information
        troubleshooting = (
            "Chroma connection failed. Please check:\n"
            "1. Chroma service is running\n"
            "2. Network connectivity to Chroma server\n"
            "3. Firewall settings allow connections\n"
            "4. Chroma server is listening on the expected port\n"
            "5. CHROMA_HOST and CHROMA_PORT environment variables are set correctly"
        )
        logger.error(troubleshooting)
        raise

# Initialize database collections
def init_mongodb_collections():
    """Initialize MongoDB collections with validation schemas."""
    from .schemas import monster_schema, spell_schema, item_schema, npc_schema, character_schema

    db = get_mongodb_database()

    # Create collections with validation
    try:
        # Helper function to convert schema to MongoDB validator format
        def prepare_schema_for_mongodb(schema):
            # Extract required fields
            required_fields = []
            properties = {}

            for field_name, field_def in schema.items():
                properties[field_name] = field_def.copy()
                if "required" in field_def and field_def["required"] is True:
                    required_fields.append(field_name)
                    # Remove the required flag from the property definition
                    del properties[field_name]["required"]

            return {
                "bsonType": "object",
                "required": required_fields,
                "properties": properties
            }

        # Monsters collection
        if "monsters" not in db.list_collection_names():
            validator = {"$jsonSchema": prepare_schema_for_mongodb(monster_schema)}
            db.create_collection("monsters", validator=validator)
            logger.info("Created monsters collection")

        # Spells collection
        if "spells" not in db.list_collection_names():
            validator = {"$jsonSchema": prepare_schema_for_mongodb(spell_schema)}
            db.create_collection("spells", validator=validator)
            logger.info("Created spells collection")

        # Items collection
        if "items" not in db.list_collection_names():
            validator = {"$jsonSchema": prepare_schema_for_mongodb(item_schema)}
            db.create_collection("items", validator=validator)
            logger.info("Created items collection")

        # NPCs collection
        if "npcs" not in db.list_collection_names():
            validator = {"$jsonSchema": prepare_schema_for_mongodb(npc_schema)}
            db.create_collection("npcs", validator=validator)
            logger.info("Created npcs collection")

        # Characters collection
        if "characters" not in db.list_collection_names():
            validator = {"$jsonSchema": prepare_schema_for_mongodb(character_schema)}
            db.create_collection("characters", validator=validator)
            logger.info("Created characters collection")

        # Create indexes
        db.monsters.create_index("name", unique=True)
        db.spells.create_index("name", unique=True)
        db.items.create_index("name", unique=True)
        db.npcs.create_index("name", unique=True)
        db.characters.create_index([("name", pymongo.ASCENDING), ("userId", pymongo.ASCENDING)], unique=True)

        logger.info("MongoDB collections initialized")
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB collections: {e}")
        raise

# Initialize Chroma collections
def init_chroma_collections():
    """Initialize Chroma collections."""
    from .schemas import chroma_collections

    client = get_chroma_client()

    try:
        # Get existing collections
        existing_collections = client.list_collections()
        existing_collection_names = [c.name for c in existing_collections]

        # Create collections that don't exist
        for collection_name, config in chroma_collections.items():
            if collection_name not in existing_collection_names:
                client.create_collection(
                    name=collection_name,
                    metadata={"description": config["description"]}
                )
                logger.info(f"Created Chroma collection: {collection_name}")

        logger.info("Chroma collections initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Chroma collections: {e}")
        raise

# Initialize all databases
def init_databases():
    """Initialize all database connections and collections."""
    try:
        init_mongodb_collections()
        init_chroma_collections()
        logger.info("All databases initialized")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise
