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
PROMPT_DIR = os.path.join(os.path.dirname(__file__), 'prompts')

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
                logger.info(f"Loaded prompt for {agent_type} from {prompt_path}")
                return prompt_content
        except FileNotFoundError:
            logger.warning(f"Warning: Prompt file {prompt_path} not found.")
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

            # Query the DMA agent
            logger.info("DMA: Querying DMA agent...")
            print("DMA: Querying DMA agent...")

            # Create the full prompt with context and user input
            full_prompt = f"{dma_prompt}\n\nGAME STATE:\n{json.dumps(context, indent=2)}\n\nUSER INPUT: {input_text}"

            # Call the OpenRouter API
            model_name = self.agent_manager.model_tiers.get('tier1', 'mistralai/mistral-7b-instruct')

            logger.info(f"DMA: Using model: {model_name}")
            print(f"DMA: Using model: {model_name}")

            response = self.agent_manager._call_openrouter(
                prompt=full_prompt,
                model=model_name
            )

            if response and 'choices' in response and len(response['choices']) > 0:
                dm_response = response['choices'][0]['message']['content']
                logger.info(f"DMA: Got response from OpenRouter: {dm_response[:50]}...")
                print(f"DMA: Got response from OpenRouter")

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
            full_prompt = f"{cma_prompt}\n\nGAME STATE:\n{json.dumps(context, indent=2)}\n\nREQUEST:\n{json.dumps(request, indent=2)}"

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
