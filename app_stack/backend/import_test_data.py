#!/usr/bin/env python3
"""
Import test data into the RPGer database.

This script:
1. Validates the schema and test data
2. Initializes the MongoDB collections
3. Imports the test data into MongoDB
4. Creates Chroma collections
5. Generates embeddings for the test data (placeholder)
"""

import sys
import logging
import argparse
from db.validate_schema import main as validate_main
from db import init_mongodb_collections, init_chroma_collections
from db.test_data import init_test_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main():
    """Main function to import test data."""
    parser = argparse.ArgumentParser(description='Import test data into the RPGer database.')
    parser.add_argument('--skip-validation', action='store_true', help='Skip schema and data validation')
    parser.add_argument('--skip-mongodb', action='store_true', help='Skip MongoDB initialization and import')
    parser.add_argument('--skip-chroma', action='store_true', help='Skip Chroma initialization')
    parser.add_argument('--skip-embeddings', action='store_true', help='Skip embedding generation')
    
    args = parser.parse_args()
    
    # Step 1: Validate schema and test data
    if not args.skip_validation:
        logger.info("Validating schema and test data...")
        validation_result = validate_main()
        if validation_result != 0:
            logger.error("Validation failed. Please fix the issues before importing data.")
            return 1
    
    # Step 2: Initialize MongoDB collections
    if not args.skip_mongodb:
        logger.info("Initializing MongoDB collections...")
        try:
            init_mongodb_collections()
            logger.info("MongoDB collections initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB collections: {e}")
            return 1
    
    # Step 3: Import test data into MongoDB
    if not args.skip_mongodb:
        logger.info("Importing test data into MongoDB...")
        try:
            init_test_data()
            logger.info("Test data imported successfully.")
        except Exception as e:
            logger.error(f"Failed to import test data: {e}")
            return 1
    
    # Step 4: Initialize Chroma collections
    if not args.skip_chroma:
        logger.info("Initializing Chroma collections...")
        try:
            init_chroma_collections()
            logger.info("Chroma collections initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Chroma collections: {e}")
            return 1
    
    # Step 5: Generate embeddings for test data (placeholder)
    if not args.skip_embeddings:
        logger.info("Generating embeddings for test data...")
        logger.info("Note: This is a placeholder. Embedding generation is not implemented yet.")
    
    logger.info("Import completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
