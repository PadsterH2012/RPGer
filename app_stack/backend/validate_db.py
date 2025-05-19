#!/usr/bin/env python3
"""
Run the database schema and test data validator.
"""

import sys
import logging
from db.validate_schema import main as validate_main

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("Running database schema and test data validation...")
    result = validate_main()
    sys.exit(result)
