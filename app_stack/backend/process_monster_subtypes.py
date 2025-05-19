#!/usr/bin/env python3
"""
Helper script for manually processing monster files with subtypes.

This script:
1. Takes a monster file as input
2. Displays its content
3. Allows you to create separate files for each subtype
4. Moves the processed file to a "processed" directory
"""

import os
import sys
import re
import shutil
import argparse
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def display_file_content(file_path):
    """Display the content of a file."""
    print("\n" + "="*80)
    print(f"File: {file_path}")
    print("="*80)
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(content)
    print("="*80 + "\n")
    
    return content

def create_subtype_file(original_file, subtype_name, content, output_dir):
    """Create a new file for a subtype."""
    # Extract the directory structure from the original file
    rel_path = os.path.relpath(original_file, "/mnt/network_repo/RPGer/reference")
    dir_path = os.path.dirname(rel_path)
    
    # Create the output directory if it doesn't exist
    output_path = os.path.join(output_dir, dir_path)
    os.makedirs(output_path, exist_ok=True)
    
    # Create the output file name
    base_name = os.path.basename(original_file)
    name_parts = os.path.splitext(base_name)
    subtype_file = f"{name_parts[0]}_{subtype_name.replace(' ', '_')}{name_parts[1]}"
    output_file = os.path.join(output_path, subtype_file)
    
    # Write the content to the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"Created subtype file: {output_file}")
    return output_file

def mark_as_processed(file_path):
    """Mark a file as processed by moving it to a 'processed' directory."""
    # Create a 'processed' directory in the same directory as the original file
    dir_path = os.path.dirname(file_path)
    processed_dir = os.path.join(dir_path, "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    # Move the file to the 'processed' directory
    base_name = os.path.basename(file_path)
    processed_file = os.path.join(processed_dir, base_name)
    
    # If the file already exists in the processed directory, add a timestamp
    if os.path.exists(processed_file):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        name_parts = os.path.splitext(base_name)
        processed_file = os.path.join(processed_dir, f"{name_parts[0]}_{timestamp}{name_parts[1]}")
    
    shutil.move(file_path, processed_file)
    logger.info(f"Moved original file to: {processed_file}")
    return processed_file

def process_monster_file(file_path, output_dir):
    """Process a monster file with subtypes."""
    # Display the file content
    content = display_file_content(file_path)
    
    # Extract the monster name
    name_match = re.search(r'# (.*)', content)
    monster_name = name_match.group(1).strip() if name_match else os.path.basename(file_path)
    
    print(f"\nProcessing monster: {monster_name}")
    print("This file may contain subtypes. Please follow these steps:")
    print("1. Review the file content above")
    print("2. Identify each subtype in the file")
    print("3. For each subtype, create a separate file with the appropriate content")
    print("4. Mark the original file as processed when done")
    print("\nCommands:")
    print("  c <subtype_name> - Create a new file for a subtype")
    print("  m - Mark the original file as processed")
    print("  q - Quit without processing")
    
    while True:
        command = input("\nEnter command: ").strip()
        
        if command.lower() == 'q':
            print("Quitting without processing.")
            return False
        
        elif command.lower() == 'm':
            processed_file = mark_as_processed(file_path)
            print(f"Marked as processed: {processed_file}")
            return True
        
        elif command.lower().startswith('c '):
            subtype_name = command[2:].strip()
            if not subtype_name:
                print("Error: Subtype name cannot be empty.")
                continue
            
            print(f"Creating file for subtype: {subtype_name}")
            print("Enter the content for this subtype (end with a line containing only '---'):")
            
            subtype_content = []
            while True:
                line = input()
                if line == "---":
                    break
                subtype_content.append(line)
            
            subtype_file = create_subtype_file(
                file_path,
                subtype_name,
                "\n".join(subtype_content),
                output_dir
            )
            
            print(f"Created subtype file: {subtype_file}")
        
        else:
            print("Invalid command. Please try again.")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Process monster files with subtypes.')
    parser.add_argument('file', type=str, help='Monster file to process')
    parser.add_argument('--output-dir', '-o', type=str, default='/mnt/network_repo/RPGer/processed_monsters',
                        help='Output directory for processed files')
    
    args = parser.parse_args()
    
    if not os.path.isfile(args.file):
        logger.error(f"File not found: {args.file}")
        return 1
    
    if not os.path.isdir(args.output_dir):
        logger.error(f"Output directory not found: {args.output_dir}")
        return 1
    
    process_monster_file(args.file, args.output_dir)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
