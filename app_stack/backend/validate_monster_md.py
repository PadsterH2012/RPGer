#!/usr/bin/env python3
"""
Run the monster Markdown validator.
"""

import sys
import logging
import argparse
from db.validate_monster_md import validate_monster_md_files

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
    """Main function to validate monster MD files."""
    parser = argparse.ArgumentParser(description='Validate monster Markdown files against the monster schema.')
    parser.add_argument('directory', type=str, help='Directory containing monster MD files')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    logger.info(f"Validating monster MD files in {args.directory}...")
    result = validate_monster_md_files(args.directory)
    
    if result[1] == 0:
        logger.info("All monster MD files are valid!")
    else:
        logger.error(f"Found {result[1]} invalid monster MD files.")
    
    return 0 if result[1] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
