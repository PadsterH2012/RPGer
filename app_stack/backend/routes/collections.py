"""
Collections API routes for MongoDB data access.
"""

import os
import logging
from flask import Blueprint, jsonify, request
from pymongo import MongoClient
from bson import ObjectId
import json

# Configure logging
logger = logging.getLogger(__name__)

# Create blueprint
collections_bp = Blueprint('collections', __name__)

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

# JSON encoder for MongoDB ObjectId
class MongoJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super(MongoJSONEncoder, self).default(obj)

# Helper function to convert MongoDB document to JSON-serializable dict
def document_to_dict(doc):
    """Convert MongoDB document to JSON-serializable dict."""
    if doc is None:
        return None

    # Convert ObjectId to string
    if '_id' in doc and isinstance(doc['_id'], ObjectId):
        doc['_id'] = str(doc['_id'])

    return doc

@collections_bp.route('/', methods=['GET'])
def get_collections():
    """Get all collections in the database."""
    try:
        db = get_mongodb_database()
        collections = db.list_collection_names()
        return jsonify({
            'collections': collections,
            'count': len(collections)
        })
    except Exception as e:
        logger.error(f"Error getting collections: {e}")
        return jsonify({
            'error': 'Failed to get collections',
            'message': str(e)
        }), 500

@collections_bp.route('/<collection_name>', methods=['GET'])
def get_collection_items(collection_name):
    """Get items from a collection with pagination and search."""
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        query_str = request.args.get('query', '')

        # Validate parameters
        if page < 1:
            page = 1
        if limit < 1 or limit > 100:
            limit = 10

        # Calculate skip value for pagination
        skip = (page - 1) * limit

        # Connect to database
        db = get_mongodb_database()

        # Check if collection exists
        if collection_name not in db.list_collection_names():
            return jsonify({
                'error': f"Collection '{collection_name}' not found",
                'items': [],
                'total': 0,
                'page': page,
                'limit': limit
            }), 404

        # Build query
        query = {}
        if query_str:
            # Search by name or other relevant fields
            query = {
                '$or': [
                    {'name': {'$regex': query_str, '$options': 'i'}},
                    {'title': {'$regex': query_str, '$options': 'i'}},
                    {'description': {'$regex': query_str, '$options': 'i'}}
                ]
            }

        # Get collection
        collection = db[collection_name]

        # Count total items matching query
        total = collection.count_documents(query)

        # Get items with pagination
        items = list(collection.find(query).skip(skip).limit(limit))

        # Convert items to JSON-serializable dicts
        items = [document_to_dict(item) for item in items]

        return jsonify({
            'items': items,
            'total': total,
            'page': page,
            'limit': limit,
            'pages': (total + limit - 1) // limit  # Ceiling division
        })
    except Exception as e:
        logger.error(f"Error getting items from collection '{collection_name}': {e}")
        return jsonify({
            'error': f"Failed to get items from collection '{collection_name}'",
            'message': str(e),
            'items': [],
            'total': 0
        }), 500

@collections_bp.route('/<collection_name>/<item_id>', methods=['GET'])
def get_collection_item(collection_name, item_id):
    """Get a single item from a collection by ID."""
    try:
        # Connect to database
        db = get_mongodb_database()

        # Check if collection exists
        if collection_name not in db.list_collection_names():
            return jsonify({
                'error': f"Collection '{collection_name}' not found"
            }), 404

        # Get collection
        collection = db[collection_name]

        # Try to convert item_id to ObjectId
        try:
            object_id = ObjectId(item_id)
            # Get item by ObjectId
            item = collection.find_one({'_id': object_id})
        except:
            # If item_id is not a valid ObjectId, try to find by name
            item = collection.find_one({'name': item_id})

        # Check if item exists
        if not item:
            return jsonify({
                'error': f"Item '{item_id}' not found in collection '{collection_name}'"
            }), 404

        # Convert item to JSON-serializable dict
        item = document_to_dict(item)

        return jsonify(item)
    except Exception as e:
        logger.error(f"Error getting item '{item_id}' from collection '{collection_name}': {e}")
        return jsonify({
            'error': f"Failed to get item '{item_id}' from collection '{collection_name}'",
            'message': str(e)
        }), 500
