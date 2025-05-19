#!/usr/bin/env python3
"""
Validate all monster files in a directory.

This script:
1. Finds all monster files in a directory
2. Displays how each monster would be imported
3. Allows you to validate each monster before importing it
"""

import os
import sys
import logging
import argparse
from validate_monster_display import validate_monster_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def validate_all_monsters(directory_path):
    """Validate all monster files in a directory."""
    logger.info(f"Validating all monster files in {directory_path}...")
    
    # Find all monster files
    md_files = []
    if os.path.isdir(directory_path):
        # Get all MD files in the directory and subdirectories
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".md"):
                    md_files.append(os.path.join(root, file))
    elif os.path.isfile(directory_path) and directory_path.endswith(".md"):
        # Single MD file
        md_files = [directory_path]
    else:
        logger.warning(f"Invalid path: {directory_path}")
        return
    
    logger.info(f"Found {len(md_files)} monster files")
    
    # Validate each monster file
    valid_count = 0
    invalid_count = 0
    
    for i, md_file in enumerate(md_files):
        print(f"\nValidating file {i+1} of {len(md_files)}: {md_file}")
        
        # Ask if you want to validate this file
        validate = input("Validate this file? (y/n/q): ").strip().lower()
        
        if validate == 'q':
            logger.info("Quitting validation.")
            break
        
        if validate == 'y':
            # Validate the monster file
            if validate_monster_file(md_file):
                valid_count += 1
            else:
                invalid_count += 1
    
    logger.info(f"Validation completed: {valid_count} valid, {invalid_count} invalid")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Validate all monster files in a directory.')
    parser.add_argument('directory', type=str, help='Directory containing monster files')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.directory):
        logger.error(f"Path not found: {args.directory}")
        return 1
    
    validate_all_monsters(args.directory)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
