"""
SimpleADDTest - A simple implementation of an AD&D game engine that uses OpenRouter for AI agents.

This module provides a SimpleADDTest class that connects to OpenRouter to process commands
and interact with various agents like the Dungeon Master Agent (DMA) and Character Management
Agent (CMA).
"""

import os
import json
import logging
import time
from typing import Dict, Any, List, Optional

# Import the OpenRouterAgentManager
from openrouter_agent_manager import OpenRouterAgentManager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SimpleADDTest')

# Define prompt paths
PROMPT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'prompts')  # App/prompts

class SimpleADDTest:
    """
    A simple implementation of an AD&D game engine that uses OpenRouter for AI agents.
    """

    def __init__(self, mode="standard"):
        """
        Initialize the SimpleADDTest instance.

        Args:
            mode: The mode to run in (standard, create_character, create_campaign, etc.)
        """
        self.mode = mode
        logger.info(f"Initializing SimpleADDTest with mode: {mode}")
        print(f"DMA: Initializing SimpleADDTest with mode: {mode}")

        # Initialize game state
        self.game_state = {
            "player": {
                "name": "Test Character",
                "race": "Human",
                "class": "Fighter",
                "level": 1,
                "hp": 10,
                "max_hp": 10,
                "stats": {"STR": 16, "DEX": 14, "CON": 15, "INT": 12, "WIS": 10, "CHA": 8}
            },
            "environment": {
                "location": "Test Dungeon",
                "description": "A dark, damp dungeon with stone walls.",
                "creatures": []
            },
            "world": {
                "time": {"day": 1, "hour": 12},
                "weather": {"condition": "Clear"},
                "light": {"level": "Dim"}
            },
            "exploration": {}
        }

        # Load prompts
        self.prompts = {
            'DMA': self._load_prompt('dma'),  # Dungeon Master Agent
            'CMA': self._load_prompt('cma'),  # Character Management Agent
            'CRA': self._load_prompt('cra'),  # Combat Resolution Agent
            'NEA': self._load_prompt('nea'),  # NPC & Encounter Agent
            'EEA': self._load_prompt('eea'),  # Exploration Engine Agent
            'WEA': self._load_prompt('wea'),  # World & Environment Agent
            'MSA': self._load_prompt('msa'),  # Magic System Agent
            'CaMA': self._load_prompt('cama') # Campaign Manager Agent
        }

        # Initialize the OpenRouterAgentManager
        try:
            logger.info("DMA: Initializing OpenRouterAgentManager")
            print("DMA: Initializing OpenRouterAgentManager")
            self.agent_manager = OpenRouterAgentManager()

            # Test the connection to OpenRouter
            self._test_openrouter_connection()

        except Exception as e:
            error_msg = f"DMA: Error initializing OpenRouterAgentManager: {str(e)}"
            logger.error(error_msg)
            print(f"ERROR: {error_msg}")
            self.agent_manager = None

    def _load_prompt(self, agent_type):
        """Load prompt for a specific agent"""
        prompt_path = os.path.join(PROMPT_DIR, f"{agent_type.lower()}_tier1_prompt.txt")
        try:
            with open(prompt_path, "r") as f:
                prompt_content = f.read()
                if len(prompt_content) < 10:
                    logger.warning(f"Warning: Prompt file {prompt_path} is empty or very short ({len(prompt_content)} chars)")
                    print(f"WARNING: DMA: Prompt file {prompt_path} is empty or very short ({len(prompt_content)} chars)")
                    return f"You are the {agent_type} for AD&D 1st Edition."
                else:
                    logger.info(f"DMA: Successfully loaded prompt for {agent_type} from {prompt_path} ({len(prompt_content)} chars)")
                    print(f"DMA: Successfully loaded prompt for {agent_type} from {prompt_path} ({len(prompt_content)} chars)")
                    return prompt_content
        except FileNotFoundError:
            error_msg = f"Warning: Prompt file {prompt_path} not found."
            logger.warning(error_msg)
            print(f"WARNING: DMA: {error_msg}")
            return f"You are the {agent_type} for AD&D 1st Edition."
        except Exception as e:
            error_msg = f"Error loading prompt file {prompt_path}: {str(e)}"
            logger.error(error_msg)
            print(f"ERROR: DMA: {error_msg}")
            return f"You are the {agent_type} for AD&D 1st Edition."

    def _test_openrouter_connection(self):
        """Test the connection to OpenRouter by making a simple query."""
        if not self.agent_manager or not self.agent_manager.api_key:
            logger.error("DMA: Cannot test OpenRouter connection - No API key available")
            print("ERROR: DMA: Cannot test OpenRouter connection - No API key available")
            return

        try:
            logger.info("DMA: Testing connection to OpenRouter...")
            print("DMA: Testing connection to OpenRouter...")

            # Make a simple query to test the connection
            test_response = self.agent_manager.query_agent(
                agent_type="DMA",
                message="Test connection",
                context={"test": True},
                starting_tier="tier1",
                fallback_to_higher_tiers=False
            )

            if test_response and not test_response.get('error', False):
                logger.info("DMA: Successfully connected to OpenRouter")
                print("DMA: Successfully connected to OpenRouter")
            else:
                error_msg = f"DMA: Failed to connect to OpenRouter: {test_response.get('response', 'Unknown error')}"
                logger.error(error_msg)
                print(f"ERROR: {error_msg}")

        except Exception as e:
            error_msg = f"DMA: Error testing OpenRouter connection: {str(e)}"
            logger.error(error_msg)
            print(f"ERROR: {error_msg}")

    def get_simplified_context(self):
        """
        Get a simplified context of the current game state.

        Returns:
            Dict: The simplified game state.
        """
        return self.game_state

    def process_player_input(self, input_text):
        """
        Process player input and return a response.

        Args:
            input_text: The player's input text.

        Returns:
            str: The response to the player's input.
        """
        logger.info(f"DMA: Processing player input: {input_text}")
        print(f"DMA: Processing player input: {input_text}")

        # Check if OpenRouterAgentManager is available
        if not self.agent_manager or not self.agent_manager.api_key:
            error_msg = "DMA: Cannot process input - OpenRouter API key not available"
            logger.error(error_msg)
            print(f"ERROR: {error_msg}")
            return f"The DM acknowledges your command: {input_text}, but cannot process it due to configuration issues."

        try:
            # Create context for the agent
            context = {
                "game_state": self.game_state,
                "mode": self.mode
            }

            # Get the DMA prompt
            dma_prompt = self.prompts.get('DMA', "You are the Dungeon Master Agent for AD&D 1st Edition.")

            # Log the prompt being used (first 100 chars)
            logger.info(f"DMA: Using prompt: {dma_prompt[:100]}...")
            print(f"DMA: Using prompt: {dma_prompt[:100]}...")

            # Query the DMA agent
            logger.info("DMA: Querying DMA agent...")
            print("DMA: Querying DMA agent...")

            # Create the full prompt with context and player input
            # Format the prompt according to the expected format based on the mode
            if self.mode == "standard":
                # Standard mode uses our engineered DMA prompt with the "Player: " format
                # Add a stronger reminder about the format
                format_reminder = """
REMEMBER: Your response MUST follow this EXACT structure:
1. A single BRIEF sentence (MAXIMUM 60 characters) acknowledging the player is ATTEMPTING the action
2. A structured tag in this format: [ACTION:TYPE|PARAM1:value1|PARAM2:value2]

Example:
Player: "I search the room"
DMA: You begin scanning the area for anything unusual. [ACTION:EXPLORE|TASK:search|LOCATION:room]
"""
                full_prompt = f"{dma_prompt}\n\n{format_reminder}\n\nGAME STATE:\n{json.dumps(context, indent=2)}\n\nPlayer: \"{input_text}\"\nDMA:"
                logger.info("DMA: Using standard mode prompt format")
                print("DMA: Using standard mode prompt format")

                # Log the full prompt to a file for debugging
                try:
                    with open("full_prompt_debug.txt", "w") as f:
                        f.write(full_prompt)
                    logger.info("DMA: Saved full prompt to full_prompt_debug.txt")
                    print("DMA: Saved full prompt to full_prompt_debug.txt")
                except Exception as e:
                    logger.error(f"DMA: Failed to save full prompt: {str(e)}")
                    print(f"ERROR: DMA: Failed to save full prompt: {str(e)}")
            elif self.mode == "create_character":
                # Character creation mode uses a different format
                full_prompt = f"{dma_prompt}\n\nGAME STATE:\n{json.dumps(context, indent=2)}\n\nUSER INPUT (Character Creation): {input_text}"
                logger.info("DMA: Using character creation mode prompt format")
                print("DMA: Using character creation mode prompt format")
            elif self.mode == "create_campaign":
                # Campaign creation mode uses a different format
                full_prompt = f"{dma_prompt}\n\nGAME STATE:\n{json.dumps(context, indent=2)}\n\nUSER INPUT (Campaign Creation): {input_text}"
                logger.info("DMA: Using campaign creation mode prompt format")
                print("DMA: Using campaign creation mode prompt format")
            else:
                # Default to standard format for other modes
                full_prompt = f"{dma_prompt}\n\nGAME STATE:\n{json.dumps(context, indent=2)}\n\nPlayer: \"{input_text}\"\nDMA:"
                logger.info(f"DMA: Using default prompt format for mode: {self.mode}")
                print(f"DMA: Using default prompt format for mode: {self.mode}")

            # Call the OpenRouter API
            model_name = self.agent_manager.model_tiers.get('tier1', 'mistralai/mistral-7b-instruct')

            logger.info(f"DMA: Using model: {model_name}")
            print(f"DMA: Using model: {model_name}")

            response = self.agent_manager._call_openrouter(
                prompt=full_prompt,
                model=model_name,
                temperature=0.1  # Lower temperature for more deterministic responses
            )

            if response and 'choices' in response and len(response['choices']) > 0:
                dm_response = response['choices'][0]['message']['content']
                logger.info(f"DMA: Got response from OpenRouter: {dm_response[:50]}...")
                print(f"DMA: Got response from OpenRouter")

                # Save the response to a file for debugging
                try:
                    with open("model_response_debug.txt", "w") as f:
                        f.write(dm_response)
                    logger.info("DMA: Saved model response to model_response_debug.txt")
                    print("DMA: Saved model response to model_response_debug.txt")
                except Exception as e:
                    logger.error(f"DMA: Failed to save model response: {str(e)}")
                    print(f"ERROR: DMA: Failed to save model response: {str(e)}")

                # Check if the response is a JSON request for another agent
                if dm_response.strip().startswith('{') and dm_response.strip().endswith('}'):
                    try:
                        json_resp = json.loads(dm_response)
                        if 'target_agent' in json_resp and json_resp['target_agent'] == 'CMA':
                            # Call the Character Management Agent
                            logger.info("DMA: Detected request for CMA, forwarding...")
                            print("DMA: Detected request for CMA, forwarding...")
                            return self._call_character_management_agent(json_resp)
                    except json.JSONDecodeError:
                        # Not a valid JSON, treat as regular response
                        pass

                # Process the response based on the mode
                if self.mode == "standard":
                    # In standard mode, check for the action tag format
                    import re
                    action_tag_pattern = r'\[ACTION:([A-Z]+)\|.*\]'
                    action_tag_match = re.search(action_tag_pattern, dm_response)

                    if action_tag_match:
                        # Response follows our expected format, extract the player-visible part
                        logger.info(f"DMA: Response follows expected format with action type: {action_tag_match.group(1)}")
                        print(f"DMA: Response follows expected format with action type: {action_tag_match.group(1)}")

                        # Extract the player-visible part (text before the action tag)
                        tag_index = dm_response.find('[ACTION:')
                        if tag_index > 0:
                            player_visible = dm_response[:tag_index].strip()
                            logger.info(f"DMA: Player-visible response: {player_visible}")
                            print(f"DMA: Player-visible response: {player_visible}")
                            return player_visible
                    else:
                        # Response doesn't follow our expected format, log a warning
                        logger.warning("DMA: Response doesn't follow expected format (missing action tag)")
                        print("WARNING: DMA: Response doesn't follow expected format (missing action tag)")

                        # Generate a compliant response
                        compliant_response = self._generate_compliant_response(input_text)
                        logger.info(f"DMA: Generated compliant response: {compliant_response}")
                        print(f"DMA: Generated compliant response: {compliant_response}")
                        return compliant_response
                elif self.mode == "create_character" or self.mode == "create_campaign":
                    # In character/campaign creation modes, we don't expect action tags
                    logger.info(f"DMA: Using raw response for {self.mode} mode")
                    print(f"DMA: Using raw response for {self.mode} mode")
                else:
                    # For other modes, we still check for action tags but don't require them
                    import re
                    action_tag_pattern = r'\[ACTION:([A-Z]+)\|.*\]'
                    action_tag_match = re.search(action_tag_pattern, dm_response)

                    if action_tag_match:
                        # If there's an action tag, extract the player-visible part
                        logger.info(f"DMA: Found action tag in {self.mode} mode: {action_tag_match.group(1)}")
                        print(f"DMA: Found action tag in {self.mode} mode: {action_tag_match.group(1)}")

                        tag_index = dm_response.find('[ACTION:')
                        if tag_index > 0:
                            player_visible = dm_response[:tag_index].strip()
                            return player_visible

                return dm_response
            else:
                error_msg = f"DMA: Error from OpenRouter: {response.get('error', 'Unknown error')}"
                logger.error(error_msg)
                print(f"ERROR: {error_msg}")
                return f"The DM acknowledges your command: {input_text}, but encountered an error processing it."

        except Exception as e:
            error_msg = f"DMA: Error processing input: {str(e)}"
            logger.error(error_msg)
            print(f"ERROR: {error_msg}")
            return f"The DM acknowledges your command: {input_text}, but encountered an error processing it."

    def _generate_compliant_response(self, input_text):
        """
        Generate a compliant response with action tag when the model fails to do so.

        Args:
            input_text: The player's input text.

        Returns:
            str: A compliant response with action tag.
        """
        # Map common verbs to action types
        action_mapping = {
            'attack': 'COMBAT',
            'fight': 'COMBAT',
            'hit': 'COMBAT',
            'strike': 'COMBAT',
            'stab': 'COMBAT',
            'shoot': 'COMBAT',
            'cast': 'MAGIC',
            'spell': 'MAGIC',
            'search': 'EXPLORE',
            'look': 'EXPLORE',
            'examine': 'EXPLORE',
            'check': 'EXPLORE',
            'find': 'EXPLORE',
            'explore': 'EXPLORE',
            'move': 'EXPLORE',
            'go': 'EXPLORE',
            'walk': 'EXPLORE',
            'run': 'EXPLORE',
            'talk': 'NPC',
            'speak': 'NPC',
            'ask': 'NPC',
            'tell': 'NPC',
            'persuade': 'NPC',
            'intimidate': 'NPC',
            'bribe': 'NPC',
            'rest': 'CHARACTER',
            'sleep': 'CHARACTER',
            'heal': 'CHARACTER',
            'inventory': 'CHARACTER',
            'equip': 'CHARACTER',
            'use': 'CHARACTER',
            'drink': 'CHARACTER',
            'eat': 'CHARACTER',
            'open': 'WORLD',
            'close': 'WORLD',
            'push': 'WORLD',
            'pull': 'WORLD',
            'break': 'WORLD',
            'climb': 'WORLD',
            'jump': 'WORLD',
            'swim': 'WORLD',
            'hide': 'CHARACTER',
            'sneak': 'CHARACTER',
            'steal': 'CHARACTER',
            'pick': 'CHARACTER',
            'lockpick': 'CHARACTER',
            'disarm': 'CHARACTER',
            'trap': 'CHARACTER'
        }

        # Default action type
        action_type = 'EXPLORE'

        # Try to determine the action type from the input
        input_lower = input_text.lower()
        for verb, action in action_mapping.items():
            if verb in input_lower:
                action_type = action
                break

        # Generate a brief response based on the action type
        if action_type == 'COMBAT':
            response = "You prepare to engage in combat."
            tag = f"[ACTION:COMBAT|INTENT:{input_text}]"
        elif action_type == 'MAGIC':
            response = "You begin to focus your magical energies."
            tag = f"[ACTION:MAGIC|INTENT:{input_text}]"
        elif action_type == 'EXPLORE':
            response = "You carefully survey your surroundings."
            tag = f"[ACTION:EXPLORE|INTENT:{input_text}]"
        elif action_type == 'NPC':
            response = "You prepare to interact with someone."
            tag = f"[ACTION:NPC|INTENT:{input_text}]"
        elif action_type == 'CHARACTER':
            response = "You focus on your personal actions."
            tag = f"[ACTION:CHARACTER|TASK:{input_text}]"
        elif action_type == 'WORLD':
            response = "You prepare to interact with the environment."
            tag = f"[ACTION:WORLD|TASK:{input_text}]"
        else:
            response = "You prepare to take action."
            tag = f"[ACTION:EXPLORE|INTENT:{input_text}]"

        return f"{response} {tag}"

    def _call_character_management_agent(self, request):
        """
        Call the Character Management Agent (CMA) with the given request.

        Args:
            request: The JSON request for the CMA.

        Returns:
            str: The response from the CMA.
        """
        logger.info("CMA: Processing request...")
        print("CMA: Processing request...")

        try:
            # Get the CMA prompt
            cma_prompt = self.prompts.get('CMA', "You are the Character Management Agent for AD&D 1st Edition.")

            # Create context for the agent
            context = {
                "game_state": self.game_state
            }

            # Create the full prompt with context and request
            # Format the prompt according to the expected format
            full_prompt = f"{cma_prompt}\n\nGAME STATE:\n{json.dumps(context, indent=2)}\n\nREQUEST:\n{json.dumps(request, indent=2)}\n\nCMA:"

            # Call the OpenRouter API
            model_name = self.agent_manager.model_tiers.get('tier1', 'mistralai/mistral-7b-instruct')

            logger.info(f"CMA: Using model: {model_name}")
            print(f"CMA: Using model: {model_name}")

            response = self.agent_manager._call_openrouter(
                prompt=full_prompt,
                model=model_name
            )

            if response and 'choices' in response and len(response['choices']) > 0:
                cma_response = response['choices'][0]['message']['content']
                logger.info(f"CMA: Got response from OpenRouter: {cma_response[:50]}...")
                print(f"CMA: Got response from OpenRouter")
                return cma_response
            else:
                error_msg = f"CMA: Error from OpenRouter: {response.get('error', 'Unknown error')}"
                logger.error(error_msg)
                print(f"ERROR: {error_msg}")
                return "The Character Management Agent encountered an error processing your request."

        except Exception as e:
            error_msg = f"CMA: Error processing request: {str(e)}"
            logger.error(error_msg)
            print(f"ERROR: {error_msg}")
            return "The Character Management Agent encountered an error processing your request."
