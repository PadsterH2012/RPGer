#!/usr/bin/env python3
"""
DMA Prompt Unit Test

This script tests the DMA (Dungeon Master Agent) prompt by sending various player actions
and evaluating the responses against expected formats.
"""

import os
import json
import re
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("Missing OPENROUTER_API_KEY in .env file")

# Define model to use
MODEL = "mistralai/mistral-7b-instruct"

# Load the DMA prompt
def load_prompt(prompt_file):
    """Load a prompt from a file"""
    with open(prompt_file, 'r') as f:
        return f.read()

# Call OpenRouter API
def call_openrouter(prompt, model=MODEL):
    """Call OpenRouter API"""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1000,
        "temperature": 0.2
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data
        )
        return response.json()
    except Exception as e:
        print(f"Error calling OpenRouter API: {e}")
        return None

# Test the DMA prompt with a player action
def test_dma_prompt(dma_prompt, player_action):
    """Test the DMA prompt with a player action"""
    # Ensure each call is completely independent by using a fresh prompt
    # without any context from previous interactions
    full_prompt = f"{dma_prompt}\n\nPlayer: \"{player_action}\"\nDMA:"

    # Make a completely independent API call for each test
    response_data = call_openrouter(full_prompt)

    if response_data and 'choices' in response_data and len(response_data['choices']) > 0:
        return response_data['choices'][0]['message']['content']
    else:
        return "Error: No response from OpenRouter"

# Validate DMA response format
def validate_response(response):
    """Validate the DMA response format"""
    # Check if response is a single sentence followed by a tag
    tag_pattern = r'\[ACTION:([A-Z]+)\|.*\]'

    # Check if the response contains a tag
    tag_match = re.search(tag_pattern, response)
    if not tag_match:
        return {
            "valid": False,
            "reason": "Missing action tag",
            "response": response
        }

    # Check if the response is brief (maximum 60 characters before the tag)
    tag_index = response.find('[ACTION:')
    if tag_index == -1:
        tag_index = len(response)

    narrative = response[:tag_index].strip()
    if len(narrative) > 60:
        return {
            "valid": False,
            "reason": f"Narrative too long ({len(narrative)} chars, max 60)",
            "response": response
        }

    # Check if the response contains any prohibited content
    prohibited_patterns = [
        r'you find',  # Resolving actions
        r'you see',   # Describing scenes
        r'you can',   # Providing options
        r'you could', # Providing options
        r'you might', # Providing options
        r'options',   # Providing options
        r'damage',    # Combat resolution
        r'hit points', # Combat resolution
        r'hp',        # Combat resolution
        r'success',   # Resolving actions
        r'fail',      # Resolving actions
        r'{"'         # JSON format
    ]

    # Check if the narrative uses "about to happen" phrasing
    about_to_happen_patterns = [
        r'prepare',
        r'attempt',
        r'begin',
        r'try',
        r'ready',
        r'position',
        r'focus',
        r'start',
        r'seek'
    ]

    has_about_to_happen_phrasing = False
    for pattern in about_to_happen_patterns:
        if re.search(pattern, narrative.lower()):
            has_about_to_happen_phrasing = True
            break

    if not has_about_to_happen_phrasing:
        return {
            "valid": False,
            "reason": "Missing 'about to happen' phrasing",
            "response": response
        }

    # Check if the response is too similar to the input (for advanced test cases only)
    # This is a simple check - we just see if more than 50% of the words in the input
    # appear in the response narrative
    test_case = None
    for tc in test_cases[15:]:  # Only check advanced test cases
        if tc.lower() in response.lower():
            test_case = tc
            break

    if test_case:
        # Count how many words from the test case appear in the narrative
        test_words = set(re.findall(r'\b\w+\b', test_case.lower()))
        narrative_words = set(re.findall(r'\b\w+\b', narrative.lower()))
        common_words = test_words.intersection(narrative_words)

        # Exclude common words like "I", "the", "and", etc.
        common_words = [w for w in common_words if len(w) > 2 and w not in ['the', 'and', 'for', 'with', 'you', 'your']]

        # If more than 70% of the significant words from the test case appear in the narrative,
        # it's too repetitive
        if len(common_words) > 0.7 * len([w for w in test_words if len(w) > 2 and w not in ['the', 'and', 'for', 'with', 'you', 'your']]):
            return {
                "valid": False,
                "reason": "Response mirrors input too closely",
                "response": response,
                "common_words": common_words
            }

    for pattern in prohibited_patterns:
        if re.search(pattern, response.lower()):
            return {
                "valid": False,
                "reason": f"Contains prohibited content: '{pattern}'",
                "response": response
            }

    # Extract what the player would actually see (narrative without the tag)
    player_visible_response = narrative.strip()

    # If we got here, the response is valid
    return {
        "valid": True,
        "action_type": tag_match.group(1),
        "response": response,
        "player_visible": player_visible_response
    }

# Define test cases
test_cases = [
    # Basic combat actions
    "I attack the goblin with my sword",
    "I shoot an arrow at the orc",
    "I cast Magic Missile at the wizard",

    # Basic exploration actions
    "I search the room for traps",
    "I look around the tavern",
    "I check the bookshelf for hidden compartments",

    # Basic character actions
    "I check my inventory",
    "I rest for the night",
    "I use a healing potion",

    # Basic NPC interactions
    "I talk to the innkeeper",
    "I try to persuade the guard to let me pass",
    "I intimidate the merchant to lower his prices",

    # Basic world interactions
    "I climb the tower",
    "I swim across the river",
    "I hide in the shadows",

    # Advanced combat actions
    "I feint with my dagger then thrust at the troll's exposed flank",
    "I parry the incoming blow and riposte with my rapier",
    "I conjure an eldritch blast aimed at the necromancer's phylactery",

    # Advanced exploration actions
    "I scrutinize the arcane sigils etched into the obsidian altar",
    "I triangulate our position using the stars and my astrolabe",
    "I decipher the ancient hieroglyphics on the sarcophagus lid",

    # Advanced character actions
    "I meditate to attune myself to the ley lines of magical energy",
    "I concoct an alchemical solution using my herbalism kit",
    "I transcribe the spell from the grimoire into my spellbook",

    # Advanced NPC interactions
    "I regale the tavern patrons with tales of my exploits",
    "I interrogate the prisoner about the cult's nefarious plans",
    "I barter with the nomadic merchant for exotic wares",

    # Advanced world interactions
    "I traverse the treacherous mountain pass during the blizzard",
    "I disarm the complex mechanical trap guarding the treasury",
    "I commune with the ancient spirit bound to this hallowed grove"
]

def run_tests(advanced_only=True):
    """Run test cases

    Args:
        advanced_only: If True, only run the advanced test cases (16-30)
    """
    # Use the correct path to the prompt file in App/prompts directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(script_dir, "..", ".."))
    prompt_path = os.path.join(repo_root, "App", "prompts", "dma_tier1_prompt.txt")

    print(f"Loading prompt from: {prompt_path}")
    if not os.path.exists(prompt_path):
        print(f"ERROR: Prompt file not found at {prompt_path}")
        return {"total": 0, "passed": 0, "failed": 0, "details": []}
    # We'll load the prompt fresh for each test to ensure no shared context

    # If advanced_only is True, only test the advanced cases (indices 15-30)
    if advanced_only:
        test_subset = test_cases[15:]
        print(f"Running only advanced test cases ({len(test_subset)} tests)")
    else:
        test_subset = test_cases
        print(f"Running all test cases ({len(test_subset)} tests)")

    results = {
        "total": len(test_subset),
        "passed": 0,
        "failed": 0,
        "details": []
    }

    # Add timestamp to results
    import datetime
    results["timestamp"] = datetime.datetime.now().isoformat()
    results["prompt_file"] = prompt_path

    print(f"Running {len(test_subset)} independent tests...")
    print(f"Each test will make a separate API call with no shared context")

    for i, test_case in enumerate(test_subset):
        print(f"\nTest {i+1}/{len(test_subset)}: '{test_case}'")

        # Load the prompt fresh for each test to ensure no context is shared
        try:
            fresh_prompt = load_prompt(prompt_path)
        except Exception as e:
            print(f"ERROR: Failed to load prompt: {str(e)}")
            continue

        # Make the API call
        response = test_dma_prompt(fresh_prompt, test_case)
        validation = validate_response(response)

        if validation["valid"]:
            results["passed"] += 1
            print(f"✅ PASSED: {validation['action_type']}")
            print(f"   Player sees: \"{validation['player_visible']}\"")
        else:
            results["failed"] += 1
            print(f"❌ FAILED: {validation['reason']}")
            print(f"   Response: {validation['response']}")

        results["details"].append({
            "test_case": test_case,
            "response": response,
            "validation": validation
        })

        print("-" * 80)

        # Add a small delay between API calls to avoid rate limiting
        import time
        time.sleep(1)

    # Print summary
    print(f"\nTest Summary: {results['passed']}/{results['total']} passed ({results['passed']/results['total']*100:.1f}%)")

    # Save results to file
    with open("dma_test_results.json", "w") as f:
        json.dump(results, f, indent=2)

    return results

if __name__ == "__main__":
    import sys
    # Check if "all" is passed as a command-line argument
    if len(sys.argv) > 1 and sys.argv[1] == "all":
        run_tests(advanced_only=False)
    else:
        run_tests(advanced_only=True)
