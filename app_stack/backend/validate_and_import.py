#!/usr/bin/env python3
"""
Validate and import monster files.

This script:
1. Goes through all monster files in a directory
2. Displays each monster for validation
3. Imports approved monsters
4. Records rejected monsters in a file
"""

import os
import sys
import logging
import argparse
from db import get_mongodb_database
from db.validate_monster_md import parse_monster_md_file
from validate_monster_display import display_monster_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def validate_and_import(directory_path, rejected_file, dry_run=False):
    """Validate and import monster files."""
    logger.info(f"Validating and importing monster files from {directory_path}...")

    # Step 1: Get MongoDB database
    db = None
    if not dry_run:
        logger.info("Connecting to MongoDB...")
        try:
            db = get_mongodb_database()
            # Test the connection by accessing a collection
            _ = db.list_collection_names()
        except Exception as e:
            logger.warning(f"Failed to connect to MongoDB: {e}. Continuing in dry-run mode.")
            dry_run = True

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
        return

    logger.info(f"Found {len(md_files)} monster files")

    # Step 3: Validate and import each monster file
    approved_count = 0
    rejected_count = 0
    rejected_monsters = []

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
                valid = input("\nIs this monster data correct? (y/n/q): ").strip().lower()

                if valid == 'q':
                    logger.info("Quitting validation.")

                    # Write rejected monsters to file
                    if rejected_monsters:
                        with open(rejected_file, 'a', encoding='utf-8') as f:
                            for monster in rejected_monsters:
                                f.write(f"{monster}\n")
                        logger.info(f"Wrote {len(rejected_monsters)} rejected monsters to {rejected_file}")

                    return

                if valid == 'y':
                    if dry_run:
                        logger.info(f"[DRY RUN] Would import monster: {monster_data['name']}")
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
                        except Exception as e:
                            logger.error(f"Failed to import monster {monster_data['name']}: {e}")
                            rejected_monsters.append(f"{md_file}: {monster_data['name']} - Error: {e}")
                            rejected_count += 1
                            continue

                    approved_count += 1
                else:
                    logger.info(f"Rejected monster: {monster_data['name']}")
                    rejected_monsters.append(f"{md_file}: {monster_data['name']} - Rejected by user")
                    rejected_count += 1

        except Exception as e:
            logger.error(f"Failed to process file {md_file}: {e}")
            rejected_monsters.append(f"{md_file}: Error: {e}")
            rejected_count += 1

    logger.info(f"Validation completed: {approved_count} approved, {rejected_count} rejected")

    # Write rejected monsters to file
    if rejected_monsters:
        with open(rejected_file, 'a', encoding='utf-8') as f:
            for monster in rejected_monsters:
                f.write(f"{monster}\n")
        logger.info(f"Wrote {len(rejected_monsters)} rejected monsters to {rejected_file}")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Validate and import monster files.')
    parser.add_argument('directory', type=str, help='Directory containing monster files')
    parser.add_argument('--rejected-file', type=str, default='Failed_Verification_Subtypes_mm.md',
                        help='File to record rejected monsters')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (no database changes)')

    args = parser.parse_args()

    if not os.path.exists(args.directory):
        logger.error(f"Path not found: {args.directory}")
        return 1

    validate_and_import(args.directory, args.rejected_file, args.dry_run)

    return 0

if __name__ == "__main__":
    sys.exit(main())
