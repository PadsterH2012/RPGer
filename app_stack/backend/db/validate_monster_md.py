#!/usr/bin/env python3
"""
Validator for monster Markdown files.

This script:
1. Parses monster Markdown files
2. Converts them to structured data
3. Validates the structured data against the monster schema
4. Reports any validation errors or missing required fields
"""

import os
import sys
import re
import logging
import argparse
import datetime
from .schemas import monster_schema
from .validate_schema import validate_schema

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Monster categories based on intelligence and alignment
def determine_monster_category(intelligence, alignment):
    """Determine the monster category based on intelligence and alignment."""
    if not intelligence or intelligence.lower() in ["non-", "animal", "semi-"]:
        return "Beast"

    if "evil" in alignment.lower():
        if "chaotic" in alignment.lower():
            return "Fiend"
        elif "lawful" in alignment.lower():
            return "Devil"
        else:
            return "Undead"

    if "good" in alignment.lower():
        if "lawful" in alignment.lower():
            return "Celestial"
        else:
            return "Fey"

    if "neutral" in alignment.lower():
        return "Monstrosity"

    # Default category
    return "Humanoid"

def extract_behavior_from_description(description):
    """Extract behavior information from the monster description."""
    behavior_patterns = [
        r'behavior[s]?[\s\:]+(.*?)(\.|\n)',
        r'typically[\s]+(.*?)(\.|\n)',
        r'usually[\s]+(.*?)(\.|\n)',
        r'tend[s]? to[\s]+(.*?)(\.|\n)'
    ]

    for pattern in behavior_patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    # If no specific behavior pattern is found, return a generic statement
    return "Behavior information not explicitly stated in the description."

def extract_socialization_from_description(description):
    """Extract socialization information from the monster description."""
    social_patterns = [
        r'social[\s\:]+(.*?)(\.|\n)',
        r'group[s]?[\s\:]+(.*?)(\.|\n)',
        r'communit[y|ies][\s\:]+(.*?)(\.|\n)',
        r'live[s]? in[\s]+(.*?)(\.|\n)'
    ]

    for pattern in social_patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            return match.group(1).strip()

    # If no specific socialization pattern is found, return a generic statement
    return "Socialization information not explicitly stated in the description."

def extract_related_monsters(description):
    """Extract related monsters from the description."""
    related_monsters = []

    # Common monster types to look for
    monster_types = [
        "dragon", "giant", "troll", "ogre", "goblin", "orc", "elf", "dwarf",
        "demon", "devil", "elemental", "undead", "zombie", "skeleton", "ghost",
        "vampire", "werewolf", "lycanthrope", "golem", "construct", "aberration"
    ]

    # Check for mentions of monster types
    for monster_type in monster_types:
        if re.search(r'\b' + monster_type + r'[s]?\b', description, re.IGNORECASE):
            related_monsters.append(monster_type.capitalize())

    # Look for explicit mentions of related creatures
    related_patterns = [
        r'related to[\s]+(.*?)(\.|\n)',
        r'similar to[\s]+(.*?)(\.|\n)',
        r'akin to[\s]+(.*?)(\.|\n)',
        r'like[\s]+(.*?)(\.|\n)'
    ]

    for pattern in related_patterns:
        match = re.search(pattern, description, re.IGNORECASE)
        if match:
            related_text = match.group(1).strip()
            # Extract monster names from the related text
            monster_names = re.findall(r'\b[A-Z][a-z]+\b', related_text)
            related_monsters.extend(monster_names)

    # Remove duplicates and return
    return list(set(related_monsters))

def parse_monster_md_file(file_path):
    """Parse a monster Markdown file into a structured format."""
    logger.debug(f"Parsing file: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Check if the file contains multiple monster entries (like Ape.md)
    monster_entries = re.findall(r'# ([^\n]+)', content)
    if len(monster_entries) > 1:
        logger.debug(f"Found multiple monster entries: {monster_entries}")

        # Split the content by monster entries
        monster_sections = re.split(r'# ', content)[1:]  # Skip the first empty section
        monster_list = []

        for i, section in enumerate(monster_sections):
            # Reconstruct the section with the header
            section_content = f"# {section}"

            # Parse each section as a separate monster
            parsed_monsters = parse_monster_content(section_content, file_path)
            monster_list.extend(parsed_monsters)

        return monster_list
    else:
        # Single monster entry
        return parse_monster_content(content, file_path)

def parse_monster_content(content, file_path):
    """Parse monster content into a structured format."""
    # Extract monster name (assuming it's the first heading)
    name_match = re.search(r'# (.*)', content)
    name = name_match.group(1).strip() if name_match else "Unknown"

    # Extract other attributes using regex patterns
    attributes = {
        "frequency": extract_attribute(content, r'\*\*FREQUENCY\*\*: (.*)'),
        "no_appearing": extract_attribute(content, r'\*\*NO\. APPEARING\*\*: (.*)'),
        "armor_class": extract_attribute(content, r'\*\*ARMOR CLASS\*\*: (.*)'),
        "move": extract_attribute(content, r'\*\*MOVE\*\*: (.*)'),
        "hit_dice": extract_attribute(content, r'\*\*HIT DICE\*\*: (.*)'),
        "percent_in_lair": extract_attribute(content, r'\*\*% IN LAIR\*\*: (.*)'),
        "treasure_type": extract_attribute(content, r'\*\*TREASURE TYPE\*\*: (.*)'),
        "no_of_attacks": extract_attribute(content, r'\*\*NO\. OF ATTACKS\*\*: (.*)'),
        "damage_attack": extract_attribute(content, r'\*\*DAMAGE/ATTACK\*\*: (.*)'),
        "special_attacks": extract_attribute(content, r'\*\*SPECIAL ATTACKS\*\*: (.*)'),
        "special_defenses": extract_attribute(content, r'\*\*SPECIAL DEFENSES\*\*: (.*)'),
        "magic_resistance": extract_attribute(content, r'\*\*MAGIC RESISTANCE\*\*: (.*)'),
        "intelligence": extract_attribute(content, r'\*\*INTELLIGENCE\*\*: (.*)'),
        "alignment": extract_attribute(content, r'\*\*ALIGNMENT\*\*: (.*)'),
        "size": extract_attribute(content, r'\*\*SIZE\*\*: (.*)'),
        "psionic_ability": extract_attribute(content, r'\*\*PSIONIC ABILITY\*\*: (.*)'),
        "attack_defense_modes": extract_attribute(content, r'\*\*Attack/Defense Modes\*\*: (.*)')
    }

    # Extract description (assuming it's the text after all the attributes)
    description_match = re.search(r'Attack/Defense Modes\*\*:.*?\n\n(.*)', content, re.DOTALL)
    description = description_match.group(1).strip() if description_match else ""

    # Check if this monster has subtypes
    subtypes = extract_subtypes(content, name)

    # If subtypes are found, return a list of monster objects (one for each subtype)
    if subtypes:
        logger.debug(f"Found {len(subtypes)} subtypes for {name}")
        monster_list = []

        for subtype in subtypes:
            subtype_name = f"{name}, {subtype['name']}"

            # Create a monster object for this subtype
            monster = create_monster_object(
                name=subtype_name,
                attributes=attributes,
                description=description,
                file_path=file_path,
                subtype_data=subtype
            )

            monster_list.append(monster)

        return monster_list
    else:
        # Check for parenthetical subtypes in attributes (like Bat.md)
        parenthetical_subtypes = extract_parenthetical_subtypes(attributes)
        if parenthetical_subtypes:
            logger.debug(f"Found {len(parenthetical_subtypes)} parenthetical subtypes for {name}")
            monster_list = []

            for subtype in parenthetical_subtypes:
                subtype_name = f"{name}, {subtype['name']}"

                # Create a monster object for this subtype
                monster = create_monster_object(
                    name=subtype_name,
                    attributes=attributes,
                    description=description,
                    file_path=file_path,
                    subtype_data=subtype
                )

                monster_list.append(monster)

            return monster_list
        else:
            # Create a single monster object
            return [create_monster_object(
                name=name,
                attributes=attributes,
                description=description,
                file_path=file_path
            )]

def extract_parenthetical_subtypes(attributes):
    """Extract subtypes from parenthetical expressions in attributes."""
    subtypes = []

    # Look for patterns like "1-2 hit points (normal), 4 (giant)" in attributes
    for attr_name, attr_value in attributes.items():
        if not attr_value:
            continue

        # Look for patterns like "X (normal), Y (giant)"
        subtype_pattern = r'([^,]+)\s*\((\w+)\)(?:,\s*|\Z)'
        matches = re.finditer(subtype_pattern, attr_value)

        for match in matches:
            value = match.group(1).strip()
            subtype_name = match.group(2).strip()

            # Find or create the subtype
            subtype = next((s for s in subtypes if s['name'] == subtype_name), None)
            if not subtype:
                subtype = {'name': subtype_name, 'description': ''}
                subtypes.append(subtype)

            # Add the attribute value to the subtype
            subtype[attr_name] = value

    # Look for subtype descriptions in the description field
    # This will be handled separately in the create_monster_object function

    return subtypes

def extract_subtypes(content, parent_name=None):
    """Extract subtypes from a monster description."""
    subtypes = []

    # First, check for the format where subtypes are listed under each attribute
    # (e.g., "**FREQUENCY**:\nBlack: Common\nBrown: Uncommon\nCave: Uncommon")
    subtype_names = []

    # Look for subtypes in the FREQUENCY section
    frequency_match = re.search(r'\*\*FREQUENCY\*\*:(.*?)(?=\n\n\*\*|\Z)', content, re.DOTALL)
    if frequency_match:
        frequency_text = frequency_match.group(1).strip()
        # Extract subtype names from lines like "Black: Common"
        subtype_lines = re.finditer(r'(\w+):\s*(.*)', frequency_text)
        for line in subtype_lines:
            subtype_name = line.group(1).strip()
            if subtype_name and subtype_name not in subtype_names:
                subtype_names.append(subtype_name)

    # Check for "Giant X" or similar variants in the description
    description_match = re.search(r'Attack/Defense Modes\*\*:.*?\n\n(.*)', content, re.DOTALL)
    if description_match:
        description = description_match.group(1).strip()

        # Look for patterns like "**Giant Badger**:" or "Giant Badger:" or "Giant Badger"
        giant_patterns = [
            r'\*\*(Giant \w+)\*\*:',  # "**Giant Badger**:"
            r'(?:^|\n)(Giant \w+):',  # "Giant Badger:"
            r'There is a .* variety of (badger)',  # "There is a very rare variety of badger"
            r'\*\*([\w\s]+)\*\*: There is'  # "**Giant Badger**: There is"
        ]

        for pattern in giant_patterns:
            giant_matches = re.finditer(pattern, description, re.MULTILINE | re.DOTALL)

            for match in giant_matches:
                if pattern == r'There is a .* variety of (badger)':
                    subtype_name = "Giant " + match.group(1)
                else:
                    subtype_name = match.group(1)

                if subtype_name and subtype_name not in subtype_names:
                    subtype_names.append(subtype_name)

                    # Extract stats for this giant variant
                    variant_text = description[match.end():].split('\n\n')[0].strip()
                    subtype_data = {
                        'name': subtype_name,
                        'description': variant_text
                    }

                    # Extract hit dice, damage, and size if mentioned
                    hd_match = re.search(r'Hit dice:\s*(\d+(?:\+\d+)?)', variant_text, re.IGNORECASE)
                    if hd_match:
                        subtype_data['hit_dice'] = hd_match.group(1)

                    damage_match = re.search(r'(\d+-\d+/\d+-\d+/\d+-\d+)', variant_text)
                    if damage_match:
                        subtype_data['damage_attack'] = damage_match.group(1)

                    size_match = re.search(r'Size:\s*([A-Z])', variant_text, re.IGNORECASE)
                    if size_match:
                        subtype_data['size'] = size_match.group(1)

                    subtypes.append(subtype_data)

                # Extract stats for this giant variant
                variant_text = description[match.end():].split('\n\n')[0].strip()
                subtype_data = {
                    'name': subtype_name,
                    'description': variant_text
                }

                # Extract hit dice, damage, and size if mentioned
                hd_match = re.search(r'Hit dice:\s*(\d+(?:\+\d+)?)', variant_text, re.IGNORECASE)
                if hd_match:
                    subtype_data['hit_dice'] = hd_match.group(1)

                damage_match = re.search(r'(\d+-\d+/\d+-\d+/\d+-\d+)', variant_text)
                if damage_match:
                    subtype_data['damage_attack'] = damage_match.group(1)

                size_match = re.search(r'Size:\s*([A-Z])', variant_text, re.IGNORECASE)
                if size_match:
                    subtype_data['size'] = size_match.group(1)

                subtypes.append(subtype_data)

    # If we found subtypes in the attribute format, extract all their attributes
    if len(subtype_names) > 0 and not subtypes:
        logger.debug(f"Found {len(subtype_names)} subtypes in attribute format: {subtype_names}")

        # Extract the main description (after the stats block)
        description_match = re.search(r'Attack/Defense Modes\*\*:.*?\n\n(.*)', content, re.DOTALL)
        main_description = description_match.group(1) if description_match else ""

        # Create a subtype object for each subtype
        for subtype_name in subtype_names:
            subtype_data = {
                'name': subtype_name,
                'description': ''
            }

            # Extract attributes for this subtype
            attributes = [
                ('frequency', r'\*\*FREQUENCY\*\*:(.*?)(?=\n\n\*\*|\Z)'),
                ('no_appearing', r'\*\*NO\. APPEARING\*\*:(.*?)(?=\n\n\*\*|\Z)'),
                ('armor_class', r'\*\*ARMOR CLASS\*\*:(.*?)(?=\n\n\*\*|\Z)'),
                ('move', r'\*\*MOVE\*\*:(.*?)(?=\n\n\*\*|\Z)'),
                ('hit_dice', r'\*\*HIT DICE\*\*:(.*?)(?=\n\n\*\*|\Z)'),
                ('percent_in_lair', r'\*\*% IN LAIR\*\*:(.*?)(?=\n\n\*\*|\Z)'),
                ('treasure_type', r'\*\*TREASURE TYPE\*\*:(.*?)(?=\n\n\*\*|\Z)'),
                ('no_of_attacks', r'\*\*NO\. OF ATTACKS\*\*:(.*?)(?=\n\n\*\*|\Z)'),
                ('damage_attack', r'\*\*DAMAGE/ATTACK\*\*:(.*?)(?=\n\n\*\*|\Z)'),
                ('special_attacks', r'\*\*SPECIAL ATTACKS\*\*:(.*?)(?=\n\n\*\*|\Z)'),
                ('special_defenses', r'\*\*SPECIAL DEFENSES\*\*:(.*?)(?=\n\n\*\*|\Z)'),
                ('magic_resistance', r'\*\*MAGIC RESISTANCE\*\*:(.*?)(?=\n\n\*\*|\Z)'),
                ('intelligence', r'\*\*INTELLIGENCE\*\*:(.*?)(?=\n\n\*\*|\Z)'),
                ('alignment', r'\*\*ALIGNMENT\*\*:(.*?)(?=\n\n\*\*|\Z)'),
                ('size', r'\*\*SIZE\*\*:(.*?)(?=\n\n\*\*|\Z)'),
                ('psionic_ability', r'\*\*PSIONIC ABILITY\*\*:(.*?)(?=\n\n\*\*|\Z)'),
                ('attack_defense_modes', r'\*\*Attack/Defense Modes\*\*:(.*?)(?=\n\n\*\*|\Z)')
            ]

            for attr_name, pattern in attributes:
                attr_match = re.search(pattern, content, re.DOTALL)
                if attr_match:
                    attr_text = attr_match.group(1).strip()
                    # Look for the subtype's value in this attribute
                    subtype_line = re.search(f'{subtype_name}:\\s*(.*)', attr_text)
                    if subtype_line:
                        subtype_data[attr_name] = subtype_line.group(1).strip()

            # Extract subtype-specific description from the main description
            # Look for paragraphs that start with the subtype name
            subtype_desc_pattern = f'The {subtype_name.lower()} bear is (.*?)(?=\n\n|$)'
            subtype_desc_match = re.search(subtype_desc_pattern, main_description, re.DOTALL | re.IGNORECASE)
            if subtype_desc_match:
                subtype_data['description'] = f"The {subtype_name.lower()} bear is {subtype_desc_match.group(1).strip()}"

            subtypes.append(subtype_data)

        return subtypes

    # If we didn't find subtypes in the attribute format, check for the format with subtype headers
    # Look for subtype headers (e.g., "**Bombardier Beetle**:")
    subtype_pattern = r'\*\*([\w\s]+)\*\*:\s*\n(.*?)(?=\n\n\*\*|\Z)'

    # Extract the main description (after the stats block)
    description_match = re.search(r'Attack/Defense Modes\*\*:.*?\n\n(.*)', content, re.DOTALL)
    if not description_match:
        return []

    description = description_match.group(1)

    # Check if the description contains phrases indicating subtypes
    subtype_indicators = [
        r'There are several types',
        r'There are \d+ types',
        r'There are \d+ varieties',
        r'There are several varieties',
        r'There are different types',
        r'There are different varieties'
    ]

    has_subtypes = False
    for indicator in subtype_indicators:
        if re.search(indicator, description):
            has_subtypes = True
            break

    if not has_subtypes:
        return []

    # Find all subtype blocks
    subtype_blocks = re.finditer(subtype_pattern, description, re.DOTALL | re.MULTILINE)

    for block in subtype_blocks:
        subtype_name = block.group(1).strip()
        subtype_text = block.group(2).strip()

        # Extract stats from the subtype text
        subtype_data = {
            'name': subtype_name,
            'description': ''
        }

        # Extract stats line (e.g., "AC: 4; Move: 9"; HD: 2+2; Damage: 2-12;...")
        stats_match = re.search(r'(AC:.*?)(Size:|$)', subtype_text)
        if stats_match:
            stats_line = stats_match.group(1).strip()

            # Extract individual stats
            ac_match = re.search(r'AC:\s*(\d+)', stats_line)
            if ac_match:
                subtype_data['armor_class'] = ac_match.group(1)

            move_match = re.search(r'Move:\s*([^;]+)', stats_line)
            if move_match:
                subtype_data['move'] = move_match.group(1).strip()

            hd_match = re.search(r'HD:\s*([^;]+)', stats_line)
            if hd_match:
                subtype_data['hit_dice'] = hd_match.group(1).strip()

            damage_match = re.search(r'Damage:\s*([^;]+)', stats_line)
            if damage_match:
                subtype_data['damage'] = damage_match.group(1).strip()

            treasure_match = re.search(r'Treasure Type:\s*([^;]+)', stats_line)
            if treasure_match:
                subtype_data['treasure_type'] = treasure_match.group(1).strip()

            size_match = re.search(r'Size:\s*([^;]+)', subtype_text)
            if size_match:
                subtype_data['size'] = size_match.group(1).strip()

        # Extract description (text after the stats line)
        description_start = subtype_text.find('\n\n')
        if description_start > 0:
            subtype_data['description'] = subtype_text[description_start:].strip()

        subtypes.append(subtype_data)

    return subtypes

def create_monster_object(name, attributes, description, file_path, subtype_data=None):
    """Create a structured monster object that matches our schema."""
    # Override attributes with subtype data if provided
    if subtype_data:
        for key, value in subtype_data.items():
            if key in attributes and value:
                attributes[key] = value

        # If subtype has its own description, append it to the main description
        if 'description' in subtype_data and subtype_data['description']:
            description = f"{description}\n\n{subtype_data['name']} Details:\n{subtype_data['description']}"
        else:
            # Try to extract subtype-specific description from the main description
            subtype_name = subtype_data['name']

            # Look for sections like "**Normal Bat**:" or "The black bear is..."
            subtype_patterns = [
                f"\\*\\*{subtype_name}\\*\\*:(.*?)(?=\\n\\n\\*\\*|\\Z)",  # "**Normal Bat**:"
                f"The {subtype_name.lower()} (?:bear|ape|bat|beetle) is (.*?)(?=\\n\\n|\\Z)"  # "The black bear is..."
            ]

            for pattern in subtype_patterns:
                subtype_desc_match = re.search(pattern, description, re.DOTALL | re.IGNORECASE)
                if subtype_desc_match:
                    subtype_desc = subtype_desc_match.group(1).strip()
                    if subtype_desc:
                        description = f"{description}\n\n{subtype_name} Details:\n{subtype_desc}"
                    break

    # Create the monster object
    monster = {
        "name": name,
        "category": determine_monster_category(attributes["intelligence"], attributes["alignment"]),
        "description": description,
        "stats": {
            "frequency": attributes["frequency"],
            "no_appearing": attributes["no_appearing"],
            "armor_class": convert_to_int(attributes["armor_class"]),
            "move": attributes["move"],
            "hit_dice": attributes["hit_dice"],
            "hit_points": convert_hit_dice_to_hp(attributes["hit_dice"]),
            "treasure_type": attributes["treasure_type"],
            "no_of_attacks": attributes["no_of_attacks"],
            "damage_attack": attributes["damage_attack"],
            "percent_in_lair": attributes["percent_in_lair"]
        },
        "path": file_path,
        "metadata": {
            "source": "Monster Manual 1",
            "type": "Monster",
            "alignment": attributes["alignment"],
            "size": attributes["size"],
            "intelligence": attributes["intelligence"],
            "psionic_ability": attributes["psionic_ability"],
            "attack_defense_modes": attributes["attack_defense_modes"],
            "tags": []
        },
        "habitat": {
            "primary_environments": [],
            "terrain_preferences": [],
            "climate_preferences": [],
            "regional_distribution": [],
            "specific_locations": [],
            "migration_patterns": "",
            "lair_description": ""
        },
        "ecology": {
            "diet": "",
            "predators": [],
            "prey": [],
            "behavior": extract_behavior_from_description(description),
            "lifecycle": "",
            "socialization": extract_socialization_from_description(description),
            "interaction_with_civilization": ""
        },
        "embedding_references": [],
        "related_monsters": extract_related_monsters(description),
        "encounter_suggestions": [],
        "campaign_usage": {
            "plot_hooks": [],
            "regional_variants": []
        },
        "extended_properties": {
            "legendary_actions": [],
            "lair_actions": [],
            "regional_effects": [],
            "custom_abilities": []
        },
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }

    # Add abilities field
    monster["abilities"] = []

    # Extract abilities from special attacks and defenses
    if attributes["special_attacks"] and attributes["special_attacks"].lower() != "nil":
        monster["abilities"].append({
            "name": "Special Attack",
            "description": attributes["special_attacks"],
            "type": "attack"
        })

    if attributes["special_defenses"] and attributes["special_defenses"].lower() != "nil":
        monster["abilities"].append({
            "name": "Special Defense",
            "description": attributes["special_defenses"],
            "type": "defense"
        })

    # Add tags based on attributes
    if attributes["alignment"]:
        monster["metadata"]["tags"].append(attributes["alignment"])

    if attributes["size"]:
        size_match = re.search(r'([A-Z])', attributes["size"])
        if size_match:
            monster["metadata"]["tags"].append(f"Size-{size_match.group(1)}")

    return monster

def extract_attribute(content, pattern):
    """Extract an attribute from the content using a regex pattern."""
    match = re.search(pattern, content)
    return match.group(1).strip() if match else ""

def convert_hit_dice_to_hp(hit_dice):
    """Convert hit dice to hit points (simple average calculation)."""
    if not hit_dice:
        return 0

    try:
        # Handle simple numbers like "16"
        return int(hit_dice) * 4  # Assuming average of 4 per hit die
    except ValueError:
        # Handle complex expressions like "2+1" or "3-1"
        match = re.search(r'(\d+)([+-]\d+)?', hit_dice)
        if match:
            base = int(match.group(1))
            modifier = match.group(2)
            modifier_value = int(modifier) if modifier else 0
            return base * 4 + modifier_value
        return 0

def convert_to_int(value):
    """Convert a string value to an integer, handling special cases."""
    if not value:
        return 0

    try:
        return int(value)
    except ValueError:
        # Handle special cases like "3/2" or "10 (4)"
        match = re.search(r'(\d+)', value)
        if match:
            return int(match.group(1))
        return 0

def convert_move_to_speed(move):
    """Convert movement value to speed in feet."""
    if not move:
        return 0

    # Handle values like "24""
    match = re.search(r'(\d+)', move)
    if match:
        # Convert to feet (assuming 1" = 10 feet)
        return int(match.group(1)) * 10
    return 0

def validate_monster_md_files(path):
    """Validate monster data from Markdown files against the monster schema."""
    logger.info(f"Validating monster MD files in {path}...")

    # Check if the path is a directory or a file
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
        return 0, 0, []

    logger.info(f"Found {len(md_files)} monster MD files")

    valid_count = 0
    invalid_count = 0
    issues = []
    total_monsters = 0

    for md_file in md_files:
        try:
            # Parse the MD file into a structured format (may return multiple monsters for subtypes)
            monsters_data = parse_monster_md_file(md_file)
            total_monsters += len(monsters_data)

            file_valid = True
            file_issues = []

            # Validate each monster in the file
            for monster_data in monsters_data:
                # Validate the monster data against the schema
                result = validate_schema("Monster", monster_schema, [monster_data], quiet=True)

                if result[1] > 0:  # Invalid items found
                    file_valid = False
                    file_issues.extend([{
                        "monster_name": monster_data["name"],
                        "error": error["error"],
                        "path": error["path"]
                    } for error in result[2]])

            if file_valid:
                valid_count += 1
                logger.debug(f"Valid file: {md_file} ({len(monsters_data)} monsters)")
            else:
                invalid_count += 1
                issues.append({
                    "file": md_file,
                    "errors": file_issues
                })
                logger.debug(f"Invalid file: {md_file} ({len(file_issues)} issues)")

        except Exception as e:
            invalid_count += 1
            issues.append({
                "file": md_file,
                "error": str(e)
            })
            logger.debug(f"Error parsing file: {md_file} - {str(e)}")

    # Report results
    logger.info(f"Monster MD files: {valid_count} valid, {invalid_count} invalid")
    logger.info(f"Total monsters (including subtypes): {total_monsters}")

    if invalid_count > 0:
        logger.warning(f"Issues found in monster MD files:")
        for issue in issues:
            logger.warning(f"  File: {issue['file']}")
            if "errors" in issue:
                for error in issue["errors"]:
                    logger.warning(f"    Monster: {error['monster_name']}")
                    logger.warning(f"    Error: {error['error']} (Path: {error['path']})")
            else:
                logger.warning(f"  Error: {issue['error']}")
            logger.warning("")

    return valid_count, invalid_count, issues

def main():
    """Main function to validate monster MD files."""
    parser = argparse.ArgumentParser(description='Validate monster Markdown files against the monster schema.')
    parser.add_argument('directory', type=str, help='Directory containing monster MD files')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')

    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    result = validate_monster_md_files(args.directory)

    return 0 if result[1] == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
