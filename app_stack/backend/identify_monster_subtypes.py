#!/usr/bin/env python3
"""
Identify monster files that potentially have subtypes.
"""

import os
import re
import sys
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def has_multiple_headers(content):
    """Check if the file has multiple monster headers."""
    headers = re.findall(r'# ([^\n]+)', content)
    return len(headers) > 1

def has_attribute_subtypes(content):
    """Check if the file has subtypes listed under attributes."""
    # Look for patterns like "Black: Common" under attributes
    for attr in ["FREQUENCY", "NO. APPEARING", "ARMOR CLASS", "MOVE", "HIT DICE"]:
        attr_match = re.search(r'\*\*' + attr + r'\*\*:(.*?)(?=\n\n\*\*|\Z)', content, re.DOTALL)
        if attr_match:
            attr_text = attr_match.group(1).strip()
            subtype_lines = re.findall(r'(\w+):\s*(.*)', attr_text)
            if len(subtype_lines) > 1:
                return True
    return False

def has_parenthetical_subtypes(content):
    """Check if the file has subtypes in parentheses in attributes."""
    # Look for patterns like "1-2 hit points (normal), 4 (giant)"
    for attr in ["NO. APPEARING", "ARMOR CLASS", "MOVE", "HIT DICE", "DAMAGE/ATTACK"]:
        attr_match = re.search(r'\*\*' + attr + r'\*\*:\s*(.*?)(?=\n\n\*\*|\Z)', content, re.DOTALL)
        if attr_match:
            attr_text = attr_match.group(1).strip()
            if re.search(r'\([a-zA-Z]+\)', attr_text):
                return True
    return False

def has_description_subtypes(content):
    """Check if the file has subtypes described in the description."""
    # Extract description
    description_match = re.search(r'Attack/Defense Modes\*\*:.*?\n\n(.*)', content, re.DOTALL)
    if not description_match:
        return False
    
    description = description_match.group(1).strip()
    
    # Check for subtype indicators
    subtype_indicators = [
        r'There are several types',
        r'There are \d+ types',
        r'There are \d+ varieties',
        r'There are several varieties',
        r'There are different types',
        r'There are different varieties',
        r'variety of',
        r'\*\*[\w\s]+\*\*:',  # "**Normal Bat**:"
        r'The \w+ (?:bear|ape|bat|beetle) is'  # "The black bear is..."
    ]
    
    for indicator in subtype_indicators:
        if re.search(indicator, description, re.IGNORECASE):
            return True
    
    return False

def identify_monster_subtypes(directory_path):
    """Identify monster files that potentially have subtypes."""
    logger.info(f"Scanning monster files in {directory_path}...")
    
    # Check if the path is a directory or a file
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
        return []
    
    logger.info(f"Found {len(md_files)} monster MD files")
    
    # Identify files with potential subtypes
    subtype_files = []
    
    for md_file in md_files:
        try:
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract monster name
            name_match = re.search(r'# (.*)', content)
            name = name_match.group(1).strip() if name_match else os.path.basename(md_file)
            
            # Check for subtypes
            has_subtypes = False
            subtype_types = []
            
            if has_multiple_headers(content):
                has_subtypes = True
                subtype_types.append("multiple_headers")
            
            if has_attribute_subtypes(content):
                has_subtypes = True
                subtype_types.append("attribute_subtypes")
            
            if has_parenthetical_subtypes(content):
                has_subtypes = True
                subtype_types.append("parenthetical_subtypes")
            
            if has_description_subtypes(content):
                has_subtypes = True
                subtype_types.append("description_subtypes")
            
            if has_subtypes:
                subtype_files.append({
                    "file": md_file,
                    "name": name,
                    "subtype_types": subtype_types
                })
                logger.info(f"Found potential subtypes in {md_file}: {subtype_types}")
        
        except Exception as e:
            logger.error(f"Error processing {md_file}: {e}")
    
    logger.info(f"Found {len(subtype_files)} files with potential subtypes")
    return subtype_files

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Identify monster files with potential subtypes.')
    parser.add_argument('directory', type=str, help='Directory containing monster MD files')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    subtype_files = identify_monster_subtypes(args.directory)
    
    # Print summary
    print("\nSummary of files with potential subtypes:")
    for file_info in subtype_files:
        print(f"{file_info['name']} ({os.path.basename(file_info['file'])}): {', '.join(file_info['subtype_types'])}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
