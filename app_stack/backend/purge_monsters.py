#!/usr/bin/env python3
"""
Purge monsters from MongoDB.

This script:
1. Connects to MongoDB
2. Removes specified monsters or all monsters imported by the validation script
"""

import sys
import logging
import argparse
from db import get_mongodb_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def purge_monsters(monster_names=None, all_imported=False):
    """Purge monsters from MongoDB."""
    logger.info("Connecting to MongoDB...")
    try:
        db = get_mongodb_database()
        # Test the connection by accessing a collection
        _ = db.list_collection_names()
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        return False
    
    if all_imported:
        # Find all monsters with a path field (these were imported by our script)
        result = db.monsters.delete_many({"path": {"$exists": True}})
        logger.info(f"Deleted {result.deleted_count} imported monsters")
    elif monster_names:
        # Delete specific monsters by name
        result = db.monsters.delete_many({"name": {"$in": monster_names}})
        logger.info(f"Deleted {result.deleted_count} monsters: {', '.join(monster_names)}")
    else:
        logger.warning("No monsters specified for deletion")
        return False
    
    return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Purge monsters from MongoDB.')
    parser.add_argument('--names', type=str, nargs='+', help='Names of monsters to purge')
    parser.add_argument('--all-imported', action='store_true', help='Purge all monsters imported by the validation script')
    
    args = parser.parse_args()
    
    if not args.names and not args.all_imported:
        logger.error("Please specify either --names or --all-imported")
        return 1
    
    purge_monsters(args.names, args.all_imported)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
