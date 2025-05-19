#!/usr/bin/env python3
"""
Import processed monster files into the database.

This script:
1. Validates processed monster files
2. Imports them into the database
"""

import os
import sys
import logging
import argparse
from db import get_mongodb_database
from db.validate_monster_md import validate_monster_md_files, parse_monster_md_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def import_processed_monsters(directory_path, skip_validation=False, dry_run=False):
    """Import processed monster files into the database."""
    logger.info(f"Importing processed monster files from {directory_path}...")
    
    # Step 1: Validate monster files
    if not skip_validation:
        logger.info("Validating monster files...")
        result = validate_monster_md_files(directory_path)
        if result[1] > 0:
            logger.error(f"Found {result[1]} invalid monster files. Please fix the issues before importing.")
            return False
    
    # Step 2: Get MongoDB database
    if not dry_run:
        logger.info("Connecting to MongoDB...")
        db = get_mongodb_database()
        if not db:
            logger.error("Failed to connect to MongoDB.")
            return False
    
    # Step 3: Import monster data into MongoDB
    logger.info("Importing monster data into MongoDB...")
    import_count = 0
    error_count = 0
    
    # Get all MD files in the directory and subdirectories
    md_files = []
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".md"):
                md_files.append(os.path.join(root, file))
    
    logger.info(f"Found {len(md_files)} monster files to import")
    
    for md_file in md_files:
        try:
            # Parse the MD file into a structured format
            monsters_data = parse_monster_md_file(md_file)
            
            for monster_data in monsters_data:
                if dry_run:
                    logger.info(f"[DRY RUN] Would import monster: {monster_data['name']}")
                else:
                    # Check if the monster already exists
                    existing_monster = db.monsters.find_one({"name": monster_data["name"]})
                    if existing_monster:
                        # Update the existing monster
                        db.monsters.update_one(
                            {"name": monster_data["name"]},
                            {"$set": monster_data}
                        )
                        logger.info(f"Updated monster: {monster_data['name']}")
                    else:
                        # Insert the new monster
                        db.monsters.insert_one(monster_data)
                        logger.info(f"Inserted monster: {monster_data['name']}")
                
                import_count += 1
        except Exception as e:
            logger.error(f"Failed to import monster from {md_file}: {e}")
            error_count += 1
    
    logger.info(f"Import completed: {import_count} monsters imported, {error_count} errors")
    
    return import_count > 0 and error_count == 0

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Import processed monster files into the database.')
    parser.add_argument('directory', type=str, help='Directory containing processed monster files')
    parser.add_argument('--skip-validation', action='store_true', help='Skip validation of monster files')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (no database changes)')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.directory):
        logger.error(f"Directory not found: {args.directory}")
        return 1
    
    import_processed_monsters(args.directory, args.skip_validation, args.dry_run)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
