#!/usr/bin/env python3
"""
Display how a monster file would be imported into the database.

This script:
1. Parses a monster MD file
2. Displays the structured data in a format similar to the original MD file
3. Allows you to validate the monster before importing it
"""

import os
import sys
import re
import logging
import argparse
from db.validate_monster_md import parse_monster_md_file

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def display_monster_data(monster_data):
    """Display monster data in a format similar to the original MD file."""
    print(f"# {monster_data['name']}\n")
    
    # Display stats
    stats = monster_data.get('stats', {})
    if 'frequency' in stats:
        print(f"**FREQUENCY**: {stats['frequency']}")
    if 'no_appearing' in stats:
        print(f"**NO. APPEARING**: {stats['no_appearing']}")
    if 'armor_class' in stats:
        print(f"**ARMOR CLASS**: {stats['armor_class']}")
    if 'move' in stats:
        print(f"**MOVE**: {stats['move']}")
    if 'hit_dice' in stats:
        print(f"**HIT DICE**: {stats['hit_dice']}")
    if 'hit_points' in stats:
        print(f"**HIT POINTS**: {stats['hit_points']}")
    if 'percent_in_lair' in stats:
        print(f"**% IN LAIR**: {stats['percent_in_lair']}")
    if 'treasure_type' in stats:
        print(f"**TREASURE TYPE**: {stats['treasure_type']}")
    if 'no_of_attacks' in stats:
        print(f"**NO. OF ATTACKS**: {stats['no_of_attacks']}")
    if 'damage_attack' in stats:
        print(f"**DAMAGE/ATTACK**: {stats['damage_attack']}")
    
    # Display special abilities
    abilities = monster_data.get('abilities', [])
    for ability in abilities:
        if ability.get('type') == 'attack':
            print(f"**SPECIAL ATTACKS**: {ability.get('description', '')}")
        elif ability.get('type') == 'defense':
            print(f"**SPECIAL DEFENSES**: {ability.get('description', '')}")
    
    # Display metadata
    metadata = monster_data.get('metadata', {})
    if 'magic_resistance' in metadata:
        print(f"**MAGIC RESISTANCE**: {metadata['magic_resistance']}")
    if 'intelligence' in metadata:
        print(f"**INTELLIGENCE**: {metadata['intelligence']}")
    if 'alignment' in metadata:
        print(f"**ALIGNMENT**: {metadata['alignment']}")
    if 'size' in metadata:
        print(f"**SIZE**: {metadata['size']}")
    if 'psionic_ability' in metadata:
        print(f"**PSIONIC ABILITY**: {metadata['psionic_ability']}")
    if 'attack_defense_modes' in metadata:
        print(f"**Attack/Defense Modes**: {metadata['attack_defense_modes']}")
    
    # Display description
    print(f"\n{monster_data.get('description', '')}")

def validate_monster_file(file_path):
    """Validate a monster file by displaying how it would be imported."""
    logger.info(f"Validating monster file: {file_path}")
    
    try:
        # Parse the monster file
        monsters_data = parse_monster_md_file(file_path)
        
        # Display each monster
        for i, monster_data in enumerate(monsters_data):
            if i > 0:
                print("\n" + "="*80 + "\n")
            
            print("="*80)
            print(f"Monster {i+1} of {len(monsters_data)}")
            print("="*80 + "\n")
            
            display_monster_data(monster_data)
            
            # Ask for validation
            print("\n" + "="*80)
            valid = input("\nIs this monster data correct? (y/n): ").strip().lower()
            
            if valid == 'y':
                logger.info(f"Monster validated: {monster_data['name']}")
            else:
                logger.warning(f"Monster not validated: {monster_data['name']}")
                
                # Ask for specific issues
                issues = input("What issues did you find? (optional): ").strip()
                if issues:
                    logger.warning(f"Issues: {issues}")
    
    except Exception as e:
        logger.error(f"Error validating monster file: {e}")
        return False
    
    return True

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Validate a monster file by displaying how it would be imported.')
    parser.add_argument('file', type=str, help='Monster file to validate')
    
    args = parser.parse_args()
    
    if not os.path.isfile(args.file):
        logger.error(f"File not found: {args.file}")
        return 1
    
    validate_monster_file(args.file)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
