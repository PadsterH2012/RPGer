#!/usr/bin/env python3
"""
Import validated monster files into the database.

This script:
1. Validates each monster file by displaying how it would be imported
2. Imports only the validated monsters into the database
"""

import os
import sys
import logging
import argparse
import json
from db import get_mongodb_database
from db.validate_monster_md import parse_monster_md_file
from validate_monster_display import validate_monster_file, display_monster_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def import_validated_monsters(directory_path, dry_run=False, save_to_file=None):
    """Import validated monster files into the database."""
    logger.info(f"Importing validated monster files from {directory_path}...")

    # Step 1: Get MongoDB database
    db = None
    if not dry_run:
        logger.info("Connecting to MongoDB...")
        try:
            db = get_mongodb_database()
            if not db:
                logger.warning("Failed to connect to MongoDB. Continuing in dry-run mode.")
                dry_run = True
        except Exception as e:
            logger.warning(f"Failed to connect to MongoDB: {e}. Continuing in dry-run mode.")
            dry_run = True

    # If save_to_file is specified, prepare to save validated monsters to a file
    validated_monsters = []

    # Step 2: Find all monster files
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
        return False

    logger.info(f"Found {len(md_files)} monster files")

    # Step 3: Import validated monsters
    import_count = 0
    error_count = 0

    for i, md_file in enumerate(md_files):
        print(f"\nProcessing file {i+1} of {len(md_files)}: {md_file}")

        try:
            # Parse the monster file
            monsters_data = parse_monster_md_file(md_file)

            # Display and validate each monster
            for monster_data in monsters_data:
                print("\n" + "="*80)
                print(f"Monster: {monster_data['name']}")
                print("="*80 + "\n")

                display_monster_data(monster_data)

                # Ask for validation
                print("\n" + "="*80)
                valid = input("\nImport this monster? (y/n/q): ").strip().lower()

                if valid == 'q':
                    logger.info("Quitting import.")
                    return import_count > 0 and error_count == 0

                if valid == 'y':
                    if dry_run:
                        logger.info(f"[DRY RUN] Would import monster: {monster_data['name']}")
                        # Add to validated monsters list if saving to file
                        if save_to_file:
                            validated_monsters.append(monster_data)
                        import_count += 1
                    else:
                        try:
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
                            logger.error(f"Failed to import monster {monster_data['name']}: {e}")
                            error_count += 1

        except Exception as e:
            logger.error(f"Failed to process file {md_file}: {e}")
            error_count += 1

    logger.info(f"Import completed: {import_count} monsters imported, {error_count} errors")

    # Save validated monsters to file if specified
    if save_to_file and validated_monsters:
        try:
            # Convert ObjectId to string for JSON serialization
            for monster in validated_monsters:
                if '_id' in monster and not isinstance(monster['_id'], str):
                    monster['_id'] = str(monster['_id'])

            with open(save_to_file, 'w', encoding='utf-8') as f:
                json.dump(validated_monsters, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved {len(validated_monsters)} validated monsters to {save_to_file}")
        except Exception as e:
            logger.error(f"Failed to save validated monsters to file: {e}")

    return import_count > 0 and error_count == 0

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Import validated monster files into the database.')
    parser.add_argument('directory', type=str, help='Directory containing monster files')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (no database changes)')
    parser.add_argument('--save-to-file', type=str, help='Save validated monsters to a JSON file')

    args = parser.parse_args()

    if not os.path.exists(args.directory):
        logger.error(f"Path not found: {args.directory}")
        return 1

    import_validated_monsters(args.directory, args.dry_run, args.save_to_file)

    return 0

if __name__ == "__main__":
    sys.exit(main())
