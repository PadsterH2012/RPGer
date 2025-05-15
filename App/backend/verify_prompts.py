#!/usr/bin/env python3
"""
Prompt Verification Script

This script verifies that all required prompts are present in the App/prompts directory
and can be loaded correctly by the OpenRouterAgentManager.
"""

import os
import sys
import logging
from typing import Dict, Any, List

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("prompt-verifier")

# Define the expected prompt files
EXPECTED_PROMPTS = [
    "dma_tier1_prompt.txt",
    "dma_tier2_prompt.txt",
    "dma_tier3_prompt.txt",
    # Add other expected prompts here
]

def verify_prompts() -> bool:
    """Verify that all required prompts are present and can be loaded"""
    # Determine the repository root directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    prompt_dir = os.path.join(repo_root, "App", "prompts")

    print(f"Checking prompts in: {prompt_dir}")

    # Check if the prompt directory exists
    if not os.path.exists(prompt_dir):
        print(f"ERROR: Prompt directory not found: {prompt_dir}")
        return False

    # Get the list of prompt files
    try:
        prompt_files = os.listdir(prompt_dir)
    except Exception as e:
        print(f"ERROR: Failed to list prompt directory: {str(e)}")
        return False

    # Check if all expected prompts are present
    missing_prompts = []
    for expected_prompt in EXPECTED_PROMPTS:
        if expected_prompt not in prompt_files:
            missing_prompts.append(expected_prompt)

    if missing_prompts:
        print(f"ERROR: Missing {len(missing_prompts)} expected prompt files:")
        for missing_prompt in missing_prompts:
            print(f"  - {missing_prompt}")
        return False

    # Try to load each prompt file
    loading_errors = []
    for prompt_file in prompt_files:
        if not prompt_file.endswith("_prompt.txt"):
            continue

        prompt_path = os.path.join(prompt_dir, prompt_file)
        try:
            with open(prompt_path, 'r') as f:
                prompt_content = f.read()
                if len(prompt_content) < 10:
                    print(f"⚠️ Warning: {prompt_file} is empty or very short ({len(prompt_content)} chars)")
                else:
                    print(f"✅ Successfully loaded {prompt_file} ({len(prompt_content)} chars)")
        except Exception as e:
            loading_errors.append(f"{prompt_file}: {str(e)}")

    if loading_errors:
        print(f"ERROR: Failed to load {len(loading_errors)} prompt files:")
        for error in loading_errors:
            print(f"  - {error}")
        return False

    # All checks passed
    print(f"✅ All {len(prompt_files)} prompt files verified successfully!")
    return True

def main():
    """Main function"""
    print("Verifying prompt files...")
    success = verify_prompts()

    if success:
        print("\nAll prompt checks passed!")
        sys.exit(0)
    else:
        print("\nPrompt verification failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
