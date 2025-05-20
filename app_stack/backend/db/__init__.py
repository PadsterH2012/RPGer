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

# MongoDB connection
def get_mongodb_client():
    """Get a MongoDB client instance."""
    # Try multiple connection strings to handle different environments
    connection_strings = [
        os.environ.get('MONGODB_URI', "mongodb://admin:password@mongodb:27017/rpger?authSource=admin"),
        "mongodb://admin:password@localhost:27017/rpger?authSource=admin",
        "mongodb://localhost:27017/rpger"
    ]

    last_error = None
    for uri in connection_strings:
        try:
            logger.info(f"Attempting to connect to MongoDB with URI: {uri.split('@')[-1]}")  # Log only the non-credential part
            client = MongoClient(uri, serverSelectionTimeoutMS=5000)
            # Verify connection
            client.server_info()
            logger.info(f"Successfully connected to MongoDB at {uri.split('@')[-1]}")
            return client
        except Exception as e:
            last_error = e
            logger.warning(f"Failed to connect to MongoDB at {uri.split('@')[-1]}: {e}")

    # If we get here, all connection attempts failed
    logger.error(f"All MongoDB connection attempts failed. Last error: {last_error}")
    raise last_error

def get_mongodb_database():
    """Get the MongoDB database instance."""
    client = get_mongodb_client()
    db_name = os.environ.get('MONGODB_DATABASE', 'rpger')
    return client[db_name]

# Chroma connection
def get_chroma_client():
    """Get a Chroma client instance."""
    chroma_host = os.environ.get('CHROMA_HOST', 'chroma')
    chroma_port = os.environ.get('CHROMA_PORT', '8000')
    try:
        client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
        # Verify connection
        client.heartbeat()
        logger.info("Connected to Chroma")
        return client
    except Exception as e:
        logger.error(f"Failed to connect to Chroma: {e}")
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
    tenant = os.environ.get('CHROMA_TENANT', 'default_tenant')

    try:
        # Check if tenant exists and create it if needed
        tenants = client.list_tenants()
        tenant_names = [t.name for t in tenants]
        
        if tenant not in tenant_names:
            logger.info(f"Creating Chroma tenant: {tenant}")
            client.create_tenant(tenant)
        
        # Set tenant context
        client.set_tenant(tenant)
        logger.info(f"Using Chroma tenant: {tenant}")
        
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
