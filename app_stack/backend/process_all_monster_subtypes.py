#!/usr/bin/env python3
"""
Process all monster files with subtypes.

This script:
1. Identifies monster files with potential subtypes
2. Allows you to select which files to process
3. Processes each selected file using the process_monster_subtypes.py script
"""

import os
import sys
import subprocess
import logging
import argparse
from identify_monster_subtypes import identify_monster_subtypes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def process_all_monster_subtypes(directory_path, output_dir, subtype_type=None):
    """Process all monster files with subtypes."""
    # Identify monster files with potential subtypes
    subtype_files = identify_monster_subtypes(directory_path)
    
    # Filter by subtype type if specified
    if subtype_type:
        subtype_files = [f for f in subtype_files if subtype_type in f['subtype_types']]
    
    if not subtype_files:
        logger.info("No monster files with subtypes found.")
        return
    
    # Display the list of files to process
    print("\nMonster files with subtypes:")
    for i, file_info in enumerate(subtype_files):
        print(f"{i+1}. {file_info['name']} ({os.path.basename(file_info['file'])}): {', '.join(file_info['subtype_types'])}")
    
    # Ask which files to process
    print("\nEnter the numbers of the files you want to process (comma-separated), or 'all' for all files:")
    selection = input().strip()
    
    if selection.lower() == 'all':
        selected_indices = range(len(subtype_files))
    else:
        try:
            selected_indices = [int(i.strip()) - 1 for i in selection.split(',')]
        except ValueError:
            logger.error("Invalid selection. Please enter comma-separated numbers.")
            return
    
    # Process each selected file
    for i in selected_indices:
        if i < 0 or i >= len(subtype_files):
            logger.warning(f"Invalid index: {i+1}")
            continue
        
        file_info = subtype_files[i]
        file_path = file_info['file']
        
        print(f"\nProcessing {file_info['name']} ({os.path.basename(file_path)})...")
        
        # Call the process_monster_subtypes.py script
        subprocess.run([
            sys.executable,
            os.path.join(os.path.dirname(__file__), 'process_monster_subtypes.py'),
            file_path,
            '--output-dir', output_dir
        ])

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Process all monster files with subtypes.')
    parser.add_argument('directory', type=str, help='Directory containing monster MD files')
    parser.add_argument('--output-dir', '-o', type=str, default='/mnt/network_repo/RPGer/processed_monsters',
                        help='Output directory for processed files')
    parser.add_argument('--subtype-type', '-t', type=str, choices=['multiple_headers', 'attribute_subtypes', 'parenthetical_subtypes', 'description_subtypes'],
                        help='Filter by subtype type')
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.directory):
        logger.error(f"Directory not found: {args.directory}")
        return 1
    
    if not os.path.isdir(args.output_dir):
        logger.error(f"Output directory not found: {args.output_dir}")
        return 1
    
    process_all_monster_subtypes(args.directory, args.output_dir, args.subtype_type)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
