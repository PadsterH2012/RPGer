#!/usr/bin/env python3
"""
Import monster data from Markdown files into the RPGer database.

This script:
1. Validates monster Markdown files
2. Converts them to structured data
3. Imports the structured data into MongoDB
4. Optionally creates embeddings in Chroma
"""

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

def import_monster_md_files(path, skip_validation=False, skip_chroma=True, dry_run=False):
    """Import monster data from Markdown files into the database."""
    logger.info(f"Importing monster MD files from {path}...")

    # Step 1: Validate monster MD files
    if not skip_validation:
        logger.info("Validating monster MD files...")
        result = validate_monster_md_files(path)
        if result[1] > 0:
            logger.error(f"Found {result[1]} invalid monster MD files. Please fix the issues before importing.")
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
    import os
    md_files = []
    if os.path.isdir(path):
        # Get all MD files in the directory and subdirectories
        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(".md"):
                    md_files.append(os.path.join(root, file))
    elif os.path.isfile(path) and path.endswith(".md"):
        # Single MD file
        md_files = [path]
    else:
        logger.warning(f"Invalid path: {path}")
        return False

    logger.info(f"Found {len(md_files)} monster MD files to import")

    for md_file in md_files:
        try:
            # Parse the MD file into a structured format (may return multiple monsters for subtypes)
            monsters_data = parse_monster_md_file(md_file)

            for monster_data in monsters_data:
                if dry_run:
                    logger.info(f"[DRY RUN] Would import monster: {monster_data['name']}")

                    # Display detailed information for a few selected monsters
                    # Regular monster example
                    if monster_data['name'] == "BARRACUDA" and not hasattr(import_monster_md_files, 'shown_regular'):
                        import_monster_md_files.shown_regular = True
                        logger.info("=== SAMPLE REGULAR MONSTER DATA ===")
                        logger.info(f"Name: {monster_data['name']}")
                        logger.info(f"Category: {monster_data['category']}")
                        logger.info(f"Stats: {monster_data['stats']}")
                        logger.info(f"Description: {monster_data['description'][:100]}...")
                        logger.info(f"Abilities: {monster_data['abilities']}")
                        logger.info(f"Metadata: {monster_data['metadata']}")
                        logger.info("=== END SAMPLE DATA ===\n")

                    # Subtype monster example
                    if "BEETLE, GIANT" in monster_data['name'] and not hasattr(import_monster_md_files, 'shown_subtype'):
                        import_monster_md_files.shown_subtype = True
                        logger.info("=== SAMPLE SUBTYPE MONSTER DATA ===")
                        logger.info(f"Name: {monster_data['name']}")
                        logger.info(f"Category: {monster_data['category']}")
                        logger.info(f"Stats: {monster_data['stats']}")
                        logger.info(f"Description: {monster_data['description'][:100]}...")
                        logger.info(f"Abilities: {monster_data['abilities']}")
                        logger.info(f"Metadata: {monster_data['metadata']}")
                        logger.info("=== END SAMPLE DATA ===\n")
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

    # Step 4: Create embeddings in Chroma (optional)
    if not skip_chroma and not dry_run:
        logger.info("Creating embeddings in Chroma...")
        logger.info("Note: This is a placeholder. Embedding generation is not implemented yet.")

    return import_count > 0 and error_count == 0

def main():
    """Main function to import monster MD files."""
    parser = argparse.ArgumentParser(description='Import monster Markdown files into the RPGer database.')
    parser.add_argument('directory', type=str, help='Directory containing monster MD files')
    parser.add_argument('--skip-validation', action='store_true', help='Skip validation of monster MD files')
    parser.add_argument('--skip-chroma', action='store_true', help='Skip creating embeddings in Chroma')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (no database changes)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    result = import_monster_md_files(
        args.directory,
        skip_validation=args.skip_validation,
        skip_chroma=args.skip_chroma,
        dry_run=args.dry_run
    )

    return 0 if result else 1

if __name__ == "__main__":
    sys.exit(main())
