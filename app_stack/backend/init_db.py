#!/usr/bin/env python3
"""
Initialize the RPGer database with schema and test data.
"""

import logging
import argparse
import sys
import time
from db import init_databases
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
    """Main function to initialize the database."""
    parser = argparse.ArgumentParser(description='Initialize the RPGer database.')
    parser.add_argument('--with-test-data', action='store_true', help='Include test data')
    parser.add_argument('--retry', type=int, default=5, help='Number of retry attempts')
    parser.add_argument('--retry-delay', type=int, default=5, help='Delay between retries in seconds')
    
    args = parser.parse_args()
    
    # Try to initialize the database with retries
    for attempt in range(args.retry):
        try:
            logger.info("Initializing database schema...")
            init_databases()
            
            if args.with_test_data:
                logger.info("Initializing test data...")
                init_test_data()
            
            logger.info("Database initialization complete!")
            break
        except Exception as e:
            logger.error(f"Attempt {attempt + 1}/{args.retry} failed: {e}")
            if attempt < args.retry - 1:
                logger.info(f"Retrying in {args.retry_delay} seconds...")
                time.sleep(args.retry_delay)
            else:
                logger.error("All retry attempts failed. Database initialization unsuccessful.")
                sys.exit(1)

if __name__ == "__main__":
    main()
