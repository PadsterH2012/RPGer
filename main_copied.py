import os
import json
import requests
import uuid
import datetime
from dotenv import load_dotenv
from agent_rulebook_integration import AgentRulebookIntegration
from agent_state_handlers import AgentStateHandlers

# Load environment variables
load_dotenv()

# Get API key
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
if not OPENROUTER_API_KEY:
    raise ValueError("Missing OPENROUTER_API_KEY in .env file")

# Define model to use
MODEL = "mistralai/mistral-7b-instruct"

class SimpleADDTest:
    def __init__(self, mode=None):
        """Initialize the test app"""
        # Store the mode
        self.mode = mode
        print(f"Initializing SimpleADDTest with mode: {mode}")

        # Load all prompts
        self.prompts = {
            'DMA': self.load_prompt('dma'),  # Dungeon Master Agent
            'CRA': self.load_prompt('cra'),  # Combat Resolution Agent
            'CMA': self.load_prompt('cma'),  # Character Management Agent
            'NEA': self.load_prompt('nea'),  # NPC & Encounter Agent
            'EEA': self.load_prompt('eea'),  # Exploration Engine Agent
            'WEA': self.load_prompt('wea'),  # World & Environment Agent
            'MSA': self.load_prompt('msa'),  # Magic System Agent
            'CaMA': self.load_prompt('cama') # Campaign Manager Agent
        }

        # Initialize game state based on mode
        self.load_game_state(mode)

        # Track conversation history for context
        self.conversation_history = []

        # Track costs
        self.token_usage = {
            'prompt_tokens': 0,
            'completion_tokens': 0,
            'total_tokens': 0,
            'estimated_cost': 0
        }

        # Initialize rulebook integration
        try:
            print("Initializing rulebook system...")
            self.rulebook_integration = AgentRulebookIntegration()
            self.rulebooks_available = True
            print("Rulebook system initialized successfully")

            # Pre-load common rulebook information
            print("Pre-loading common rulebook information...")
            self.get_race_class_restrictions()
            self.get_class_alignment_restrictions()
            print("Rulebook information pre-loaded successfully")
        except Exception as e:
            print(f"Warning: Could not initialize rulebook system: {e}")
            self.rulebooks_available = False

    def load_prompt(self, agent_type):
        """Load prompt for a specific agent"""
        prompt_path = f"prompts/{agent_type.lower()}_tier1_prompt.txt"
        try:
            with open(prompt_path, "r") as f:
                return f.read()
        except FileNotFoundError:
            print(f"Warning: Prompt file {prompt_path} not found.")
            return f"You are the {agent_type} for AD&D 1st Edition."

    def load_game_state(self, mode=None):
        """Load the initial game state based on the mode"""
        # Check if we're in a special mode
        if mode == 'create_character':
            print("Initializing empty game state for character creation...")
            self.game_state = {
                "characters": {},
                "environment": {
                    "location": "Character Creation",
                    "description": "You are creating a new character.",
                    "creatures": []
                },
                "world": {
                    "time": {"day": 1, "hour": 12, "minute": 0},
                    "weather": {"condition": "Clear"},
                    "light": {"condition": "Bright"},
                    "resources": {}
                },
                "exploration": {},
                "mode": "create_character",
                "character_creation": {
                    "current_step": 0,
                    "steps": [
                        "introduction",
                        "ability_scores",
                        "race",
                        "class",
                        "alignment",
                        "hit_points",
                        "equipment_money",
                        "spell_selection",
                        "character_details",
                        "name",
                        "complete"
                    ],
                    "completed_steps": []
                }
            }
            return

        # For other modes or default, load from file
        try:
            with open("data/initial_game_state.json", "r") as f:
                self.game_state = json.load(f)

            # If we're in a specific mode, update the game state
            if mode:
                self.game_state["mode"] = mode

        except FileNotFoundError:
            print("Warning: Initial game state file not found. Using empty state.")
            self.game_state = {
                "characters": {},
                "environment": {
                    "location": "Unknown",
                    "description": "You are in a featureless void.",
                    "creatures": []
                },
                "world": {
                    "time": {"day": 1, "hour": 12, "minute": 0},
                    "weather": {"condition": "Clear"},
                    "light": {"condition": "Bright"},
                    "resources": {}
                },
                "exploration": {}
            }

            # If we're in a specific mode, update the game state
            if mode:
                self.game_state["mode"] = mode

    def call_openrouter(self, prompt, model=MODEL):
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

    def update_game_state(self, agent_request, agent_response):
        """Update the game state based on agent interactions"""
        if not agent_response or not isinstance(agent_response, dict):
            print("No valid agent response to update game state")
            return

        print(f"Updating game state with: {agent_response}")

        # Check which agent is responding and handle accordingly
        responding_agent = agent_response.get('responding_agent', '')
        target_agent = agent_request.get('target_agent', '')

        if responding_agent == 'CRA' or target_agent == 'CRA':
            # Handle Combat Resolution Agent response
            return self._update_combat_state(agent_request, agent_response)
        elif responding_agent == 'CMA' or target_agent == 'CMA':
            # Handle Character Management Agent response
            self.update_character_state(agent_request, agent_response)
        elif responding_agent == 'EEA' or target_agent == 'EEA':
            # Handle Exploration Engine Agent response
            self.update_exploration_state(agent_request, agent_response)
        elif responding_agent == 'WEA' or target_agent == 'WEA':
            # Handle World & Environment Agent response
            self.update_world_state(agent_request, agent_response)
        elif responding_agent == 'NEA' or target_agent == 'NEA':
            # Handle NPC & Encounter Agent response
            self.update_npc_state(agent_request, agent_response)
        elif responding_agent == 'MSA' or target_agent == 'MSA':
            # Handle Magic System Agent response
            self.update_magic_state(agent_request, agent_response)
        elif responding_agent == 'CaMA' or target_agent == 'CaMA':
            # Handle Campaign Manager Agent response
            self.update_campaign_state(agent_request, agent_response)
        else:
            print(f"No state handler for agent: {responding_agent or target_agent}")

    def _update_combat_state(self, agent_request, agent_response):
        """Update the game state based on combat interactions"""
        # Create a result object to track what happened
        result = {
            "target_defeated": False,
            "damage_dealt": 0,
            "target_name": "",
            "target_hp_before": 0,
            "target_hp_after": 0,
            "target_hp_max": 0
        }

        # Check if this is a combat outcome with damage
        if 'damage' in agent_response:
            # First try to get the target ID from the agent response
            target_id = agent_response.get('target_id')

            # If not found, try to get it from the request parameters
            if not target_id:
                target_id = agent_request.get('parameters', {}).get('target_id')

            # If still not found, try to find by name
            if not target_id:
                target_name = agent_request.get('parameters', {}).get('target')
                if target_name:
                    # Find the first creature matching the name
                    for creature in self.game_state.get('environment', {}).get('creatures', []):
                        if creature.get('name', '').lower() == target_name.lower():
                            target_id = creature.get('id')
                            break

            # If we still don't have a target ID but we have creatures, use the first one
            # This is a fallback for when the model doesn't provide consistent IDs
            if not target_id and self.game_state.get('environment', {}).get('creatures', []):
                target_id = self.game_state['environment']['creatures'][0]['id']
                print(f"Using fallback target ID: {target_id}")

            # If we found a target, apply damage
            if target_id:
                damage = agent_response.get('damage', 0)
                result["damage_dealt"] = damage

                if damage > 0:
                    # Find the creature and update HP
                    for i, creature in enumerate(self.game_state.get('environment', {}).get('creatures', [])):
                        if creature.get('id') == target_id:
                            # Store target information
                            result["target_name"] = creature.get('name', "Unknown")
                            result["target_hp_max"] = creature.get('hp', {}).get('maximum', 0)
                            result["target_hp_before"] = creature.get('hp', {}).get('current', 0)

                            # Apply damage
                            current_hp = creature.get('hp', {}).get('current', 0)
                            new_hp = max(0, current_hp - damage)
                            self.game_state['environment']['creatures'][i]['hp']['current'] = new_hp

                            # Update result
                            result["target_hp_after"] = new_hp

                            # If creature is defeated, mark for removal
                            if new_hp <= 0:
                                # Remove the creature
                                creature_name = creature.get('name')
                                self.game_state['environment']['creatures'].pop(i)
                                result["target_defeated"] = True
                                print(f"{creature_name} has been defeated and removed from the game!")
                            else:
                                print(f"{creature.get('name')} took {damage} damage. HP now {new_hp}/{creature.get('hp', {}).get('maximum', 0)}")
                            break

        # Add the result to the agent_response so it can be used for narrative generation
        agent_response["combat_result"] = result
        return result

    def update_token_usage(self, response_data):
        """Update token usage statistics"""
        if 'usage' in response_data:
            usage = response_data['usage']
            self.token_usage['prompt_tokens'] += usage.get('prompt_tokens', 0)
            self.token_usage['completion_tokens'] += usage.get('completion_tokens', 0)
            self.token_usage['total_tokens'] += usage.get('total_tokens', 0)

            # Estimate cost (very rough approximation)
            cost_per_1k = 0.0002  # $0.0002 per 1K tokens for Mistral-7B
            self.token_usage['estimated_cost'] += (usage.get('total_tokens', 0) / 1000) * cost_per_1k

    def extract_json_from_text(self, text):
        """Extract JSON object from text if present"""
        if '{' in text and '}' in text:
            try:
                start = text.find('{')

                # Find the matching closing brace
                open_braces = 1
                for i in range(start + 1, len(text)):
                    if text[i] == '{':
                        open_braces += 1
                    elif text[i] == '}':
                        open_braces -= 1
                        if open_braces == 0:
                            end = i + 1
                            break

                if 'end' not in locals():
                    end = text.rfind('}') + 1

                json_str = text[start:end]
                print(f"Extracted JSON: {json_str}")

                # Try to clean up any comments in the JSON
                try:
                    # Remove any lines that start with // or #
                    json_lines = []
                    for line in json_str.split('\n'):
                        line_stripped = line.strip()
                        if not line_stripped.startswith('//') and not line_stripped.startswith('#'):
                            json_lines.append(line)

                    clean_json = '\n'.join(json_lines)
                    return json.loads(clean_json)
                except json.JSONDecodeError:
                    # If cleaning didn't work, try the original JSON
                    return json.loads(json_str)

            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")

                # If the DMA response contains narrative text about combat but no valid JSON,
                # create a synthetic CRA request to ensure the game state is updated
                if "attack" in text.lower() and "goblin" in text.lower() and "longsword" in text.lower():
                    print("Creating synthetic CRA request for combat")
                    return {
                        "request_id": "synthetic_id",
                        "requesting_agent": "DMA",
                        "target_agent": "CRA",
                        "action_type": "attack",
                        "parameters": {
                            "character_id": "player1",
                            "target": "Goblin",
                            "target_id": "goblin1",
                            "weapon": "Longsword",
                            "bonuses": 2
                        }
                    }
                return None
        return None

    def extract_agent_request(self, text):
        """Extract agent request from DMA response"""
        # First try to extract JSON
        json_response = self.extract_json_from_text(text)

        # If we got a valid JSON response with a target_agent field, return it
        if json_response and isinstance(json_response, dict) and 'target_agent' in json_response:
            return json_response

        # If no JSON found, check for specific patterns in the text
        if "I need help from the Combat Resolution Agent" in text or "CRA" in text and "attack" in text.lower():
            # Create a synthetic CRA request
            return {
                "request_id": f"synthetic_{uuid.uuid4()}",
                "requesting_agent": "DMA",
                "target_agent": "CRA",
                "action_type": "attack",
                "timestamp": datetime.datetime.now().isoformat(),
                "parameters": {
                    "attacker": "player",
                    "target": "enemy",
                    "weapon": "default"
                }
            }

        if "I need help from the Character Management Agent" in text or "CMA" in text and "character" in text.lower():
            # Create a synthetic CMA request
            return {
                "request_id": f"synthetic_{uuid.uuid4()}",
                "requesting_agent": "DMA",
                "target_agent": "CMA",
                "action_type": "character_info",
                "timestamp": datetime.datetime.now().isoformat(),
                "parameters": {
                    "character_id": "player1"
                }
            }

        # No agent request found
        return None

    def process_agent_request(self, agent_request):
        """Process an agent request and return the response"""
        print(f"Processing agent request: {json.dumps(agent_request, indent=2)}")

        try:
            # Get the target agent
            target_agent = agent_request.get('target_agent')

            if target_agent not in self.prompts:
                print(f"Unknown target agent: {target_agent}")
                return None

            # Build the agent prompt
            context = self.get_simplified_context()
            agent_prompt = f"{self.prompts[target_agent]}\n\nGAME STATE:\n{json.dumps(context, indent=2)}\n\nREQUEST:\n{json.dumps(agent_request, indent=2)}"

            # Call OpenRouter with the agent prompt
            print(f"Requesting response from {target_agent}...")
            agent_response_data = self.call_openrouter(agent_prompt)

            if agent_response_data and 'choices' in agent_response_data and len(agent_response_data['choices']) > 0:
                agent_response = agent_response_data['choices'][0]['message']['content']
                self.update_token_usage(agent_response_data)

                # Extract JSON response
                json_response = self.extract_json_from_text(agent_response)

                if json_response:
                    print(f"Got JSON response from {target_agent}")
                    return json_response
                else:
                    print(f"No JSON response from {target_agent}")
                    return None
            else:
                print(f"Failed to get response from {target_agent}")
                return None

        except Exception as e:
            print(f"Error processing agent request: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def update_player_hp(self, json_response):
        """Update player HP based on enemy attack"""
        if not json_response or not isinstance(json_response, dict):
            return

        # Check if this is an attack against the player
        if json_response.get('action_type') == 'attack' and json_response.get('target_id') == 'player1':
            # Get the damage
            damage = json_response.get('damage', 0)

            # Get the player character
            character_id = next(iter(self.game_state.get('characters', {})), None)
            if not character_id:
                return

            # Get the character
            character = self.game_state['characters'].get(character_id)
            if not character:
                return

            # Get the current HP
            current_hp = character.get('hp', {}).get('current', 0)
            maximum_hp = character.get('hp', {}).get('maximum', 0)

            # Apply damage
            new_hp = max(0, current_hp - damage)

            # Update the character
            character['hp']['current'] = new_hp

            # Add a message to the action results
            if 'action_results' not in self.game_state:
                self.game_state['action_results'] = []

            self.game_state['action_results'].append(f"You took {damage} damage and now have {new_hp}/{maximum_hp} HP.")

    def load_character_creation_config(self):
        """Load the character creation workflow configuration"""
        try:
            config_path = os.path.join(os.path.dirname(__file__), 'config', 'character_creation_workflow.json')
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    config = json.load(f)
                return config.get('character_creation_workflow', {}).get('steps', [])
            else:
                print(f"Warning: Character creation config file not found at {config_path}")
                return self.get_default_creation_steps()
        except Exception as e:
            print(f"Error loading character creation config: {str(e)}")
            return self.get_default_creation_steps()

    def get_default_creation_steps(self):
        """Get the default character creation steps if config file is not available"""
        return [
            {"id": "introduction", "enabled": True, "required": True, "description": "Introduction to character creation"},
            {"id": "ability_scores", "enabled": True, "required": True, "description": "Generate ability scores", "default_method": "standard_array"},
            {"id": "race", "enabled": True, "required": True, "description": "Select character race", "default_value": "Human"},
            {"id": "class", "enabled": True, "required": True, "description": "Select character class", "default_value": "Fighter"},
            {"id": "alignment", "enabled": True, "required": True, "description": "Select character alignment", "default_value": "Neutral Good"},
            {"id": "name", "enabled": True, "required": True, "description": "Name your character", "default_value": "Adventurer"},
            {"id": "complete", "enabled": True, "required": True, "description": "Complete character creation"}
        ]

    def get_current_creation_step(self):
        """Get the current step in character creation"""
        if 'character_creation' not in self.game_state:
            # Load steps from configuration
            config_steps = self.load_character_creation_config()

            # Filter to only enabled steps
            enabled_steps = [step for step in config_steps if step.get('enabled', True)]

            # Extract just the step IDs for the workflow
            step_ids = [step['id'] for step in enabled_steps]

            self.game_state['character_creation'] = {
                "current_step": 0,
                "steps": step_ids,
                "completed_steps": [],
                "config": {step['id']: step for step in config_steps}  # Store full config for reference
            }

        return self.game_state['character_creation']['current_step']

    def advance_creation_step(self, skip_optional=False):
        """Advance to the next step in character creation

        Args:
            skip_optional: If True, skip optional (non-required) steps
        """
        if 'character_creation' not in self.game_state:
            self.get_current_creation_step()

        current_step = self.game_state['character_creation']['current_step']
        steps = self.game_state['character_creation']['steps']
        step_configs = self.game_state['character_creation'].get('config', {})

        # Add the current step to completed steps if not already there
        if current_step < len(steps) and steps[current_step] not in self.game_state['character_creation']['completed_steps']:
            self.game_state['character_creation']['completed_steps'].append(steps[current_step])

        # Advance to the next step
        if current_step < len(steps) - 1:
            next_step_index = current_step + 1

            # If skip_optional is True, skip any non-required steps
            if skip_optional:
                while (next_step_index < len(steps) - 1 and  # Don't skip the final "complete" step
                       steps[next_step_index] in step_configs and
                       not step_configs[steps[next_step_index]].get('required', True)):

                    # Apply default values for skipped step
                    self.apply_default_for_step(steps[next_step_index])

                    # Mark step as completed
                    if steps[next_step_index] not in self.game_state['character_creation']['completed_steps']:
                        self.game_state['character_creation']['completed_steps'].append(steps[next_step_index])

                    # Move to next step
                    next_step_index += 1

            self.game_state['character_creation']['current_step'] = next_step_index
            print(f"Advanced to character creation step {next_step_index}: {steps[next_step_index]}")
        else:
            print("Character creation complete")

        return self.game_state['character_creation']['current_step']

    def apply_default_for_step(self, step_id):
        """Apply default values for a skipped step"""
        print(f"Applying defaults for skipped step: {step_id}")

        # Get step configuration
        step_config = self.game_state['character_creation'].get('config', {}).get(step_id, {})
        character_id = next(iter(self.game_state.get('characters', {})), "player1")

        # Make sure we have a character
        if 'characters' not in self.game_state or character_id not in self.game_state['characters']:
            if 'characters' not in self.game_state:
                self.game_state['characters'] = {}

            # Create a basic character if none exists
            self.game_state['characters'][character_id] = {
                "name": "Unnamed",
                "race": "",
                "class": "",
                "level": 1,
                "alignment": "",
                "abilities": {},
                "hp": {"current": 0, "maximum": 0},
                "armor_class": 10,
                "weapons": [],
                "equipment": [],
                "gold": 0,
                "experience_points": 0,
                "next_level_xp": 0
            }

        # Apply defaults based on step
        if step_id == "hit_points":
            # Apply average hit points based on class
            character = self.game_state['characters'][character_id]
            class_name = character.get('class', '').lower()
            con_bonus = 0

            if 'abilities' in character and 'constitution' in character['abilities']:
                con_score = character['abilities']['constitution']
                if con_score >= 15:
                    con_bonus = 1
                elif con_score >= 17:
                    con_bonus = 2
                elif con_score <= 6:
                    con_bonus = -1
                elif con_score <= 3:
                    con_bonus = -2

            # Default hit points based on class
            if class_name == 'fighter' or class_name == 'paladin':
                hp = 10 + con_bonus
            elif class_name == 'cleric' or class_name == 'druid' or class_name == 'ranger':
                hp = 8 + con_bonus
            elif class_name == 'thief' or class_name == 'assassin' or class_name == 'monk':
                hp = 6 + con_bonus
            elif class_name == 'magic-user' or class_name == 'illusionist':
                hp = 4 + con_bonus
            else:
                hp = 8 + con_bonus  # Default

            # Ensure minimum of 1 HP
            hp = max(1, hp)

            # Update character
            self.game_state['characters'][character_id]['hp'] = {
                "current": hp,
                "maximum": hp
            }

            print(f"Applied default hit points: {hp}")

        elif step_id == "equipment_money":
            # Apply default equipment based on class
            character = self.game_state['characters'][character_id]
            class_name = character.get('class', '').lower()

            # Default gold based on class
            if class_name == 'fighter' or class_name == 'paladin' or class_name == 'ranger':
                gold = 150  # Average of 5d4 × 10
            elif class_name == 'cleric' or class_name == 'druid':
                gold = 105  # Average of 3d6 × 10
            elif class_name == 'magic-user' or class_name == 'illusionist':
                gold = 50   # Average of 2d4 × 10
            elif class_name == 'thief' or class_name == 'assassin':
                gold = 70   # Average of 2d6 × 10
            elif class_name == 'monk':
                gold = 12   # Average of 5d4
            else:
                gold = 100  # Default

            # Default equipment based on class
            if class_name == 'fighter':
                weapons = [{"name": "Longsword", "damage": "1d8"}, {"name": "Shortbow", "damage": "1d6"}]
                equipment = ["Chain Mail", "Shield", "Backpack", "Bedroll", "Rations (5 days)", "Waterskin", "Torches (10)"]
                armor_class = 4  # Chain Mail + Shield
            elif class_name == 'cleric':
                weapons = [{"name": "Mace", "damage": "1d6"}]
                equipment = ["Chain Mail", "Shield", "Holy Symbol", "Backpack", "Bedroll", "Rations (5 days)", "Waterskin", "Torches (10)"]
                armor_class = 4  # Chain Mail + Shield
            elif class_name == 'magic-user':
                weapons = [{"name": "Dagger", "damage": "1d4"}, {"name": "Staff", "damage": "1d6"}]
                equipment = ["Spellbook", "Backpack", "Bedroll", "Rations (5 days)", "Waterskin", "Torches (10)"]
                armor_class = 10  # No armor
            elif class_name == 'thief':
                weapons = [{"name": "Short Sword", "damage": "1d6"}, {"name": "Dagger", "damage": "1d4"}]
                equipment = ["Leather Armor", "Thieves' Tools", "Backpack", "Bedroll", "Rations (5 days)", "Waterskin", "Torches (10)"]
                armor_class = 8  # Leather Armor
            else:
                weapons = [{"name": "Dagger", "damage": "1d4"}]
                equipment = ["Backpack", "Bedroll", "Rations (5 days)", "Waterskin", "Torches (10)"]
                armor_class = 10  # No armor

            # Update character
            self.game_state['characters'][character_id]['weapons'] = weapons
            self.game_state['characters'][character_id]['equipment'] = equipment
            self.game_state['characters'][character_id]['armor_class'] = armor_class
            self.game_state['characters'][character_id]['gold'] = gold

            print(f"Applied default equipment and {gold} gold")

        elif step_id == "spell_selection":
            # Apply default spells based on class
            character = self.game_state['characters'][character_id]
            class_name = character.get('class', '').lower()

            # Only apply spells for spellcasting classes
            if class_name in ['magic-user', 'illusionist', 'cleric', 'druid']:
                if class_name == 'magic-user':
                    spells = ["Read Magic", "Magic Missile", "Sleep", "Shield"]
                elif class_name == 'illusionist':
                    spells = ["Read Magic", "Color Spray", "Light", "Wall of Fog"]
                elif class_name == 'cleric':
                    spells = ["Cure Light Wounds", "Detect Magic", "Protection from Evil"]
                elif class_name == 'druid':
                    spells = ["Detect Magic", "Entangle", "Faerie Fire"]
                else:
                    spells = []

                # Update character
                self.game_state['characters'][character_id]['spells'] = {
                    "level_1": spells,
                    "memorized": spells[:1] if spells else []  # Memorize first spell
                }

                print(f"Applied default spells: {spells}")

        elif step_id == "character_details":
            # Calculate derived statistics
            character = self.game_state['characters'][character_id]

            # Calculate saving throws based on class and level
            class_name = character.get('class', '').lower()
            level = character.get('level', 1)

            # Default saving throws (these would normally be looked up in tables)
            if class_name in ['fighter', 'paladin', 'ranger']:
                saving_throws = {
                    "paralyzation_poison_death": 14,
                    "rod_staff_wand": 16,
                    "petrification_polymorph": 15,
                    "breath_weapon": 17,
                    "spell": 17
                }
            elif class_name in ['cleric', 'druid']:
                saving_throws = {
                    "paralyzation_poison_death": 10,
                    "rod_staff_wand": 14,
                    "petrification_polymorph": 13,
                    "breath_weapon": 16,
                    "spell": 15
                }
            elif class_name in ['magic-user', 'illusionist']:
                saving_throws = {
                    "paralyzation_poison_death": 14,
                    "rod_staff_wand": 11,
                    "petrification_polymorph": 13,
                    "breath_weapon": 15,
                    "spell": 12
                }
            elif class_name in ['thief', 'assassin']:
                saving_throws = {
                    "paralyzation_poison_death": 13,
                    "rod_staff_wand": 14,
                    "petrification_polymorph": 12,
                    "breath_weapon": 16,
                    "spell": 15
                }
            else:
                saving_throws = {
                    "paralyzation_poison_death": 14,
                    "rod_staff_wand": 15,
                    "petrification_polymorph": 14,
                    "breath_weapon": 16,
                    "spell": 15
                }

            # Update character
            self.game_state['characters'][character_id]['saving_throws'] = saving_throws

            # Calculate next level XP if not already set
            if not character.get('next_level_xp'):
                self.game_state['characters'][character_id]['next_level_xp'] = self.get_next_level_xp(class_name, level)

            print(f"Applied default character details including saving throws and XP requirements")

    def get_creation_step_name(self, step_index=None):
        """Get the name of the current or specified step in character creation"""
        if 'character_creation' not in self.game_state:
            self.get_current_creation_step()

        if step_index is None:
            step_index = self.game_state['character_creation']['current_step']

        steps = self.game_state['character_creation']['steps']

        if 0 <= step_index < len(steps):
            return steps[step_index]
        else:
            return "unknown"

    def process_player_input(self, player_input):
        """Process player input through the agents"""
        try:
            # Add to conversation history
            self.conversation_history.append(f"Player: {player_input}")

            print(f"Processing player input: '{player_input}'")

            # Check if we're in character creation mode
            if self.mode == 'create_character':
                print(f"In character creation mode, processing input: {player_input}")

                try:
                    # Get the current step in character creation
                    current_step = self.get_current_creation_step()
                    current_step_name = self.get_creation_step_name(current_step)
                    print(f"Current character creation step: {current_step} - {current_step_name}")

                    # Handle skip command
                    if player_input.lower() == 'skip':
                        print(f"Skipping step: {current_step_name}")

                        # Get step configuration
                        step_config = self.game_state['character_creation'].get('config', {}).get(current_step_name, {})

                        # Check if step is required
                        if step_config.get('required', True):
                            return f"Cannot skip required step: {current_step_name}. Please complete this step."

                        # Apply defaults for the current step
                        self.apply_default_for_step(current_step_name)

                        # Advance to next step
                        self.advance_creation_step()

                        # Get the new step
                        new_step = self.get_creation_step_name()

                        # Start the new step
                        if new_step == "ability_scores":
                            return self.start_ability_scores_step()
                        elif new_step == "race":
                            return self.start_race_step()
                        elif new_step == "class":
                            return self.start_class_step()
                        elif new_step == "alignment":
                            return self.start_alignment_step()
                        elif new_step == "hit_points":
                            return self.start_hit_points_step()
                        elif new_step == "equipment_money":
                            return self.start_equipment_money_step()
                        elif new_step == "spell_selection":
                            return self.start_spell_selection_step()
                        elif new_step == "character_details":
                            return self.start_character_details_step()
                        elif new_step == "name":
                            return self.start_name_step()
                        elif new_step == "complete":
                            return self.complete_character_creation()
                        else:
                            return f"Advanced to step: {new_step}"

                    # Handle auto command to complete all remaining steps automatically
                    if player_input.lower() in ['auto', 'auto complete', 'autocomplete']:
                        print("Auto-completing character creation...")

                        # Apply defaults for current step if not introduction
                        if current_step_name != "introduction":
                            self.apply_default_for_step(current_step_name)

                        # Get all remaining steps
                        steps = self.game_state['character_creation']['steps']
                        current_index = self.game_state['character_creation']['current_step']

                        # Apply defaults for all remaining steps
                        for i in range(current_index + 1, len(steps) - 1):  # Skip the final "complete" step
                            self.apply_default_for_step(steps[i])
                            self.game_state['character_creation']['completed_steps'].append(steps[i])

                        # Set current step to complete
                        self.game_state['character_creation']['current_step'] = len(steps) - 1

                        # Complete character creation
                        return self.complete_character_creation()

                    # Handle create character command to start the process
                    if player_input.lower() == 'create character' and current_step_name == "introduction":
                        print("Starting character creation process...")
                        # Advance to ability scores step
                        self.advance_creation_step()
                        return self.start_ability_scores_step()

                    # Handle commands based on the current step
                    if current_step_name == "ability_scores":
                        if player_input.lower().startswith('roll ability') or player_input.lower() == 'roll ability scores':
                            print("Processing ability score rolling...")
                            result = self.handle_ability_score_generation("roll")
                            # Advance to race step
                            self.advance_creation_step()
                            return result

                        elif player_input.lower().startswith('use standard array') or player_input.lower() == 'standard array':
                            print("Processing standard array selection...")
                            result = self.handle_ability_score_generation("standard_array")
                            # Advance to race step
                            self.advance_creation_step()
                            return result

                        elif player_input.lower().startswith('use point buy') or player_input.lower() == 'point buy':
                            print("Processing point buy selection...")
                            result = self.handle_ability_score_generation("point_buy")
                            # Advance to race step
                            self.advance_creation_step()
                            return result
                        else:
                            # If the input doesn't match any ability score command, show the options again
                            return self.start_ability_scores_step()

                    elif current_step_name == "race":
                        if player_input.lower().startswith('choose race:') or player_input.lower().startswith('choose race '):
                            try:
                                race = player_input.split(':', 1)[1].strip() if ':' in player_input else player_input.split('race ', 1)[1].strip()
                                print(f"Processing race selection: {race}")
                                result = self.handle_race_selection(race)
                                # Advance to class step
                                self.advance_creation_step()
                                return result
                            except IndexError:
                                print("Error parsing race selection, using default")
                                result = self.handle_race_selection("Human")
                                # Advance to class step
                                self.advance_creation_step()
                                return result
                        else:
                            # If the input doesn't match a race command, show the options again
                            return self.start_race_step()

                    elif current_step_name == "class":
                        if player_input.lower().startswith('choose class:') or player_input.lower().startswith('choose class '):
                            try:
                                character_class = player_input.split(':', 1)[1].strip() if ':' in player_input else player_input.split('class ', 1)[1].strip()
                                print(f"Processing class selection: {character_class}")
                                result = self.handle_class_selection(character_class)
                                # Advance to alignment step
                                self.advance_creation_step()
                                return result
                            except IndexError:
                                print("Error parsing class selection, using default")
                                result = self.handle_class_selection("Fighter")
                                # Advance to alignment step
                                self.advance_creation_step()
                                return result
                        else:
                            # If the input doesn't match a class command, show the options again
                            return self.start_class_step()

                    elif current_step_name == "alignment":
                        if player_input.lower().startswith('choose alignment:') or player_input.lower().startswith('choose alignment '):
                            try:
                                alignment = player_input.split(':', 1)[1].strip() if ':' in player_input else player_input.split('alignment ', 1)[1].strip()
                                print(f"Processing alignment selection: {alignment}")
                                result = self.handle_alignment_selection(alignment)
                                # Advance to hit points step
                                self.advance_creation_step()
                                return result
                            except IndexError:
                                print("Error parsing alignment selection, using default")
                                result = self.handle_alignment_selection("Neutral Good")
                                # Advance to hit points step
                                self.advance_creation_step()
                                return result
                        else:
                            # If the input doesn't match an alignment command, show the options again
                            return self.start_alignment_step()

                    elif current_step_name == "hit_points":
                        if player_input.lower() == 'roll hit points':
                            print("Processing hit point rolling...")
                            # Roll hit points based on class
                            character_id = next(iter(self.game_state.get('characters', {})), "player1")
                            character = self.game_state['characters'].get(character_id, {})
                            class_name = character.get('class', 'Fighter').lower()
                            con_score = character.get('abilities', {}).get('constitution', 10)

                            # Determine hit die and roll
                            hit_die = 10  # Default for Fighter
                            if class_name in ['fighter', 'paladin']:
                                hit_die = 10
                            elif class_name in ['cleric', 'druid', 'ranger']:
                                hit_die = 8
                            elif class_name in ['thief', 'assassin', 'monk']:
                                hit_die = 6
                            elif class_name in ['magic-user', 'illusionist']:
                                hit_die = 4

                            # Roll the die
                            import random
                            roll = random.randint(1, hit_die)

                            # Apply constitution bonus
                            con_bonus = 0
                            if con_score >= 15:
                                con_bonus = 1
                            elif con_score >= 17:
                                con_bonus = 2
                            elif con_score <= 6:
                                con_bonus = -1
                            elif con_score <= 3:
                                con_bonus = -2

                            # Calculate total HP (minimum 1)
                            hp = max(1, roll + con_bonus)

                            # Update character
                            self.game_state['characters'][character_id]['hp'] = {
                                "current": hp,
                                "maximum": hp
                            }

                            result = f"You rolled a {roll} on a d{hit_die} and added your Constitution modifier of {con_bonus:+d} for a total of {hp} hit points."

                            # Add to DM messages for web UI
                            if 'dm_messages' in self.game_state:
                                self.game_state['dm_messages'].append(result)

                            # Advance to equipment step
                            self.advance_creation_step()
                            return result

                        elif player_input.lower() == 'average hit points':
                            print("Processing average hit points...")
                            # Calculate average hit points based on class
                            character_id = next(iter(self.game_state.get('characters', {})), "player1")
                            character = self.game_state['characters'].get(character_id, {})
                            class_name = character.get('class', 'Fighter').lower()
                            con_score = character.get('abilities', {}).get('constitution', 10)

                            # Determine hit die average
                            hit_die = 10  # Default for Fighter
                            if class_name in ['fighter', 'paladin']:
                                hit_die = 10
                                avg = 5.5
                            elif class_name in ['cleric', 'druid', 'ranger']:
                                hit_die = 8
                                avg = 4.5
                            elif class_name in ['thief', 'assassin', 'monk']:
                                hit_die = 6
                                avg = 3.5
                            elif class_name in ['magic-user', 'illusionist']:
                                hit_die = 4
                                avg = 2.5
                            else:
                                hit_die = 8
                                avg = 4.5

                            # Apply constitution bonus
                            con_bonus = 0
                            if con_score >= 15:
                                con_bonus = 1
                            elif con_score >= 17:
                                con_bonus = 2
                            elif con_score <= 6:
                                con_bonus = -1
                            elif con_score <= 3:
                                con_bonus = -2

                            # Calculate total HP (minimum 1)
                            hp = max(1, int(avg + con_bonus))

                            # Update character
                            self.game_state['characters'][character_id]['hp'] = {
                                "current": hp,
                                "maximum": hp
                            }

                            result = f"You take the average value of {avg} on a d{hit_die} and add your Constitution modifier of {con_bonus:+d} for a total of {hp} hit points."

                            # Add to DM messages for web UI
                            if 'dm_messages' in self.game_state:
                                self.game_state['dm_messages'].append(result)

                            # Advance to equipment step
                            self.advance_creation_step()
                            return result
                        else:
                            # If the input doesn't match a hit points command, show the options again
                            return self.start_hit_points_step()

                    elif current_step_name == "equipment_money":
                        if player_input.lower() == 'roll gold':
                            print("Processing gold rolling...")
                            # Roll gold based on class
                            character_id = next(iter(self.game_state.get('characters', {})), "player1")
                            character = self.game_state['characters'].get(character_id, {})
                            class_name = character.get('class', 'Fighter').lower()

                            # Determine gold formula and roll
                            import random
                            if class_name in ['fighter', 'paladin', 'ranger']:
                                # 5d4 × 10
                                rolls = [random.randint(1, 4) for _ in range(5)]
                                gold = sum(rolls) * 10
                                formula = "5d4 × 10"
                            elif class_name in ['cleric', 'druid']:
                                # 3d6 × 10
                                rolls = [random.randint(1, 6) for _ in range(3)]
                                gold = sum(rolls) * 10
                                formula = "3d6 × 10"
                            elif class_name in ['magic-user', 'illusionist']:
                                # 2d4 × 10
                                rolls = [random.randint(1, 4) for _ in range(2)]
                                gold = sum(rolls) * 10
                                formula = "2d4 × 10"
                            elif class_name in ['thief', 'assassin']:
                                # 2d6 × 10
                                rolls = [random.randint(1, 6) for _ in range(2)]
                                gold = sum(rolls) * 10
                                formula = "2d6 × 10"
                            elif class_name == 'monk':
                                # 5d4
                                rolls = [random.randint(1, 4) for _ in range(5)]
                                gold = sum(rolls)
                                formula = "5d4"
                            else:
                                # Default: 3d6 × 10
                                rolls = [random.randint(1, 6) for _ in range(3)]
                                gold = sum(rolls) * 10
                                formula = "3d6 × 10"

                            # Update character
                            self.game_state['characters'][character_id]['gold'] = gold

                            result = f"You rolled {formula} and got {gold} gold pieces. You can now purchase equipment with this gold."

                            # Add to DM messages for web UI
                            if 'dm_messages' in self.game_state:
                                self.game_state['dm_messages'].append(result)

                            # Advance to spell selection step
                            self.advance_creation_step()
                            return result

                        elif player_input.lower() == 'standard equipment':
                            print("Processing standard equipment selection...")
                            # Apply standard equipment based on class
                            character_id = next(iter(self.game_state.get('characters', {})), "player1")
                            character = self.game_state['characters'].get(character_id, {})
                            class_name = character.get('class', 'Fighter').lower()

                            # Apply standard equipment based on class
                            if class_name == 'fighter':
                                weapons = [{"name": "Longsword", "damage": "1d8"}, {"name": "Shortbow", "damage": "1d6"}]
                                equipment = ["Chain Mail", "Shield", "Backpack", "Bedroll", "Rations (5 days)", "Waterskin", "Torches (10)"]
                                armor_class = 4  # Chain Mail + Shield
                                gold = 20  # Remaining gold
                            elif class_name == 'cleric':
                                weapons = [{"name": "Mace", "damage": "1d6"}]
                                equipment = ["Chain Mail", "Shield", "Holy Symbol", "Backpack", "Bedroll", "Rations (5 days)", "Waterskin", "Torches (10)"]
                                armor_class = 4  # Chain Mail + Shield
                                gold = 15  # Remaining gold
                            elif class_name == 'magic-user':
                                weapons = [{"name": "Dagger", "damage": "1d4"}, {"name": "Staff", "damage": "1d6"}]
                                equipment = ["Spellbook", "Backpack", "Bedroll", "Rations (5 days)", "Waterskin", "Torches (10)"]
                                armor_class = 10  # No armor
                                gold = 25  # Remaining gold
                            elif class_name == 'thief':
                                weapons = [{"name": "Short Sword", "damage": "1d6"}, {"name": "Dagger", "damage": "1d4"}]
                                equipment = ["Leather Armor", "Thieves' Tools", "Backpack", "Bedroll", "Rations (5 days)", "Waterskin", "Torches (10)"]
                                armor_class = 8  # Leather Armor
                                gold = 20  # Remaining gold
                            else:
                                weapons = [{"name": "Dagger", "damage": "1d4"}]
                                equipment = ["Backpack", "Bedroll", "Rations (5 days)", "Waterskin", "Torches (10)"]
                                armor_class = 10  # No armor
                                gold = 30  # Remaining gold

                            # Update character
                            self.game_state['characters'][character_id]['weapons'] = weapons
                            self.game_state['characters'][character_id]['equipment'] = equipment
                            self.game_state['characters'][character_id]['armor_class'] = armor_class
                            self.game_state['characters'][character_id]['gold'] = gold

                            result = f"You've been equipped with standard gear for a {class_name}. You have {gold} gold pieces remaining."

                            # Add to DM messages for web UI
                            if 'dm_messages' in self.game_state:
                                self.game_state['dm_messages'].append(result)

                            # Advance to spell selection step
                            self.advance_creation_step()
                            return result
                        else:
                            # If the input doesn't match an equipment command, show the options again
                            return self.start_equipment_money_step()

                    elif current_step_name == "spell_selection":
                        # Check if character is a spellcaster
                        character_id = next(iter(self.game_state.get('characters', {})), "player1")
                        character = self.game_state['characters'].get(character_id, {})
                        class_name = character.get('class', 'Fighter').lower()
                        is_spellcaster = class_name in ['magic-user', 'illusionist', 'cleric', 'druid']

                        if not is_spellcaster:
                            # Skip this step for non-spellcasters
                            self.advance_creation_step()
                            next_step = self.get_creation_step_name()
                            if next_step == "character_details":
                                return self.start_character_details_step()
                            elif next_step == "name":
                                return self.start_name_step()
                            else:
                                return f"Advanced to step: {next_step}"

                        if player_input.lower() == 'random spells':
                            print("Processing random spell selection...")
                            # Generate random spells based on class
                            import random

                            if class_name == 'magic-user':
                                # Magic-User gets Read Magic plus 1d4 random spells
                                all_spells = ["Read Magic", "Magic Missile", "Sleep", "Shield", "Charm Person", "Detect Magic", "Identify", "Light", "Mage Armor", "Burning Hands"]
                                num_spells = random.randint(1, 4)
                                spells = ["Read Magic"]  # Always get Read Magic
                                spells.extend(random.sample([s for s in all_spells if s != "Read Magic"], num_spells))
                            elif class_name == 'illusionist':
                                # Illusionist gets Read Magic plus 1d4 random spells
                                all_spells = ["Read Magic", "Color Spray", "Detect Illusion", "Light", "Wall of Fog", "Hypnotic Pattern", "Phantasmal Force", "Ventriloquism"]
                                num_spells = random.randint(1, 4)
                                spells = ["Read Magic"]  # Always get Read Magic
                                spells.extend(random.sample([s for s in all_spells if s != "Read Magic"], num_spells))
                            elif class_name == 'cleric':
                                # Cleric gets access to all 1st-level spells, can memorize based on Wisdom
                                spells = ["Cure Light Wounds", "Detect Magic", "Protection from Evil", "Bless", "Command", "Create Water", "Light", "Purify Food and Drink", "Sanctuary"]
                            elif class_name == 'druid':
                                # Druid gets access to all 1st-level spells, can memorize based on Wisdom
                                spells = ["Detect Magic", "Entangle", "Faerie Fire", "Goodberry", "Speak with Animals", "Animal Friendship", "Create Water", "Cure Light Wounds"]
                            else:
                                spells = []

                            # Update character
                            self.game_state['characters'][character_id]['spells'] = {
                                "level_1": spells,
                                "memorized": spells[:1] if spells else []  # Memorize first spell
                            }

                            result = f"You've been granted the following spells: {', '.join(spells)}."

                            # Add to DM messages for web UI
                            if 'dm_messages' in self.game_state:
                                self.game_state['dm_messages'].append(result)

                            # Advance to character details step
                            self.advance_creation_step()
                            return result

                        elif player_input.lower() == 'choose spells':
                            print("Processing spell selection...")

                            # Define available spells based on class
                            if class_name == 'magic-user':
                                available_spells = {
                                    "Read Magic": "Allows you to read magical writings",
                                    "Magic Missile": "Creates magical darts that automatically hit targets",
                                    "Sleep": "Puts creatures into magical slumber",
                                    "Shield": "Creates an invisible barrier that protects you",
                                    "Charm Person": "Makes a humanoid creature regard you as a friend",
                                    "Detect Magic": "Reveals the presence of magic",
                                    "Identify": "Determines the properties of a magic item",
                                    "Light": "Creates light in a 20-foot radius",
                                    "Mage Armor": "Gives subject +4 armor bonus",
                                    "Burning Hands": "Creates a cone of fire dealing 1d4 damage per level"
                                }
                                required_spells = ["Read Magic"]  # Magic-Users always get Read Magic
                                max_additional = 4  # Can have up to 4 additional spells
                            elif class_name == 'illusionist':
                                available_spells = {
                                    "Read Magic": "Allows you to read magical writings",
                                    "Color Spray": "Stuns, blinds, or knocks unconscious weak creatures",
                                    "Detect Illusion": "Reveals illusions for what they are",
                                    "Light": "Creates light in a 20-foot radius",
                                    "Wall of Fog": "Creates a wall of fog that obscures vision",
                                    "Hypnotic Pattern": "Fascinates creatures",
                                    "Phantasmal Force": "Creates an illusion of your design",
                                    "Ventriloquism": "Throws your voice for 1 min./level"
                                }
                                required_spells = ["Read Magic"]  # Illusionists always get Read Magic
                                max_additional = 4  # Can have up to 4 additional spells
                            elif class_name == 'cleric':
                                available_spells = {
                                    "Cure Light Wounds": "Heals 1d8 damage +1/level (max +5)",
                                    "Detect Magic": "Reveals the presence of magic",
                                    "Protection from Evil": "Protects from evil creatures",
                                    "Bless": "Allies gain +1 on attack rolls and saves against fear",
                                    "Command": "One subject obeys selected command for 1 round",
                                    "Create Water": "Creates 2 gallons/level of pure water",
                                    "Light": "Creates light in a 20-foot radius",
                                    "Purify Food and Drink": "Purifies 1 cu. ft./level of food or water",
                                    "Sanctuary": "Opponents can't attack you, and you can't attack"
                                }
                                required_spells = []  # Clerics don't have required spells
                                max_additional = 9  # Can have all spells
                            elif class_name == 'druid':
                                available_spells = {
                                    "Detect Magic": "Reveals the presence of magic",
                                    "Entangle": "Plants entangle everyone in a 40-ft. radius",
                                    "Faerie Fire": "Outlines subjects with light, canceling blur, invisibility, etc.",
                                    "Goodberry": "2d4 berries each cure 1 hp (max 8 hp/24 hours)",
                                    "Speak with Animals": "You can communicate with animals",
                                    "Animal Friendship": "Gains permanent animal companion",
                                    "Create Water": "Creates 2 gallons/level of pure water",
                                    "Cure Light Wounds": "Heals 1d8 damage +1/level (max +5)"
                                }
                                required_spells = []  # Druids don't have required spells
                                max_additional = 8  # Can have all spells
                            else:
                                available_spells = {}
                                required_spells = []
                                max_additional = 0

                            # Create a message with spell options
                            spell_options = "\n".join([f"- {spell}: {desc}" for spell, desc in available_spells.items()])

                            spell_selection_message = f"""As a {class_name}, you have access to the following 1st-level spells:

{spell_options}

You automatically receive {', '.join(required_spells) if required_spells else 'no required spells'}.
You may select up to {max_additional} additional spells.

For simplicity, I'll select a good starting set of spells for you. You can change these later.
"""

                            # Select spells
                            spells = required_spells.copy()

                            # Add recommended spells based on class
                            if class_name == 'magic-user':
                                recommended = ["Magic Missile", "Sleep", "Shield"]
                                spells.extend(recommended)
                            elif class_name == 'illusionist':
                                recommended = ["Color Spray", "Phantasmal Force", "Detect Illusion"]
                                spells.extend(recommended)
                            elif class_name == 'cleric':
                                recommended = ["Cure Light Wounds", "Bless", "Protection from Evil"]
                                spells.extend(recommended)
                            elif class_name == 'druid':
                                recommended = ["Entangle", "Faerie Fire", "Speak with Animals"]
                                spells.extend(recommended)

                            # Update character
                            self.game_state['characters'][character_id]['spells'] = {
                                "level_1": spells,
                                "memorized": spells[:1] if spells else []  # Memorize first spell
                            }

                            result = f"{spell_selection_message}\n\nYou've been granted the following spells: {', '.join(spells)}."

                            # Add to DM messages for web UI
                            if 'dm_messages' in self.game_state:
                                self.game_state['dm_messages'].append(result)

                            # Advance to character details step
                            self.advance_creation_step()
                            return result
                        else:
                            # If the input doesn't match a spell command, show the options again
                            return self.start_spell_selection_step()

                    elif current_step_name == "character_details":
                        if player_input.lower() == 'calculate details':
                            print("Processing character details calculation...")
                            # Calculate character details
                            character_id = next(iter(self.game_state.get('characters', {})), "player1")
                            character = self.game_state['characters'].get(character_id, {})
                            class_name = character.get('class', 'Fighter').lower()
                            race = character.get('race', 'Human').lower()
                            level = character.get('level', 1)

                            # Calculate saving throws based on class and level
                            if class_name in ['fighter', 'paladin', 'ranger']:
                                saving_throws = {
                                    "paralyzation_poison_death": 14,
                                    "rod_staff_wand": 16,
                                    "petrification_polymorph": 15,
                                    "breath_weapon": 17,
                                    "spell": 17
                                }
                            elif class_name in ['cleric', 'druid']:
                                saving_throws = {
                                    "paralyzation_poison_death": 10,
                                    "rod_staff_wand": 14,
                                    "petrification_polymorph": 13,
                                    "breath_weapon": 16,
                                    "spell": 15
                                }
                            elif class_name in ['magic-user', 'illusionist']:
                                saving_throws = {
                                    "paralyzation_poison_death": 14,
                                    "rod_staff_wand": 11,
                                    "petrification_polymorph": 13,
                                    "breath_weapon": 15,
                                    "spell": 12
                                }
                            elif class_name in ['thief', 'assassin']:
                                saving_throws = {
                                    "paralyzation_poison_death": 13,
                                    "rod_staff_wand": 14,
                                    "petrification_polymorph": 12,
                                    "breath_weapon": 16,
                                    "spell": 15
                                }
                            else:
                                saving_throws = {
                                    "paralyzation_poison_death": 14,
                                    "rod_staff_wand": 15,
                                    "petrification_polymorph": 14,
                                    "breath_weapon": 16,
                                    "spell": 15
                                }

                            # Calculate languages based on race and Intelligence
                            int_score = character.get('abilities', {}).get('intelligence', 10)
                            languages = ["Common"]

                            if race == 'human':
                                pass  # Humans start with Common only
                            elif race == 'elf':
                                languages.append("Elvish")
                            elif race == 'dwarf':
                                languages.append("Dwarvish")
                            elif race == 'halfling':
                                languages.append("Halfling")
                            elif race == 'gnome':
                                languages.append("Gnomish")
                            elif race == 'half-elf':
                                languages.append("Elvish")
                            elif race == 'half-orc':
                                languages.append("Orcish")

                            # Add additional languages based on Intelligence
                            if int_score >= 12:
                                additional_languages = min(int_score - 11, 5)  # Up to 5 additional languages
                                potential_languages = ["Elvish", "Dwarvish", "Gnomish", "Halfling", "Orcish", "Goblin", "Draconic", "Giant", "Sylvan", "Undercommon"]
                                # Filter out languages already known
                                potential_languages = [lang for lang in potential_languages if lang not in languages]
                                # Add random languages
                                import random
                                if potential_languages:
                                    languages.extend(random.sample(potential_languages, min(additional_languages, len(potential_languages))))

                            # Calculate age, height, and weight based on race
                            import random
                            if race == 'human':
                                age = random.randint(16, 30)
                                height = random.randint(60, 74)  # 5'0" to 6'2"
                                weight = random.randint(120, 220)
                            elif race == 'elf':
                                age = random.randint(100, 300)
                                height = random.randint(60, 72)  # 5'0" to 6'0"
                                weight = random.randint(90, 160)
                            elif race == 'dwarf':
                                age = random.randint(40, 100)
                                height = random.randint(48, 56)  # 4'0" to 4'8"
                                weight = random.randint(130, 220)
                            elif race == 'halfling':
                                age = random.randint(20, 60)
                                height = random.randint(36, 42)  # 3'0" to 3'6"
                                weight = random.randint(60, 90)
                            elif race == 'gnome':
                                age = random.randint(60, 150)
                                height = random.randint(36, 44)  # 3'0" to 3'8"
                                weight = random.randint(70, 100)
                            elif race == 'half-elf':
                                age = random.randint(20, 60)
                                height = random.randint(60, 72)  # 5'0" to 6'0"
                                weight = random.randint(100, 180)
                            elif race == 'half-orc':
                                age = random.randint(14, 30)
                                height = random.randint(60, 76)  # 5'0" to 6'4"
                                weight = random.randint(150, 250)
                            else:
                                age = random.randint(16, 30)
                                height = random.randint(60, 74)  # 5'0" to 6'2"
                                weight = random.randint(120, 220)

                            # Format height in feet and inches
                            height_feet = height // 12
                            height_inches = height % 12
                            height_str = f"{height_feet}'{height_inches}\""

                            # Update character
                            self.game_state['characters'][character_id]['saving_throws'] = saving_throws
                            self.game_state['characters'][character_id]['languages'] = languages
                            self.game_state['characters'][character_id]['physical'] = {
                                "age": age,
                                "height": height_str,
                                "weight": weight
                            }

                            # Calculate next level XP if not already set
                            if not character.get('next_level_xp'):
                                self.game_state['characters'][character_id]['next_level_xp'] = self.get_next_level_xp(class_name, level)

                            result = f"""Your character details have been calculated:

Saving Throws:
- Paralyzation/Poison/Death: {saving_throws['paralyzation_poison_death']}
- Rod/Staff/Wand: {saving_throws['rod_staff_wand']}
- Petrification/Polymorph: {saving_throws['petrification_polymorph']}
- Breath Weapon: {saving_throws['breath_weapon']}
- Spell: {saving_throws['spell']}

Languages: {', '.join(languages)}

Physical Traits:
- Age: {age} years
- Height: {height_str}
- Weight: {weight} lbs

Experience needed for next level: {self.game_state['characters'][character_id]['next_level_xp']}"""

                            # Add to DM messages for web UI
                            if 'dm_messages' in self.game_state:
                                self.game_state['dm_messages'].append(result)

                            # Advance to name step
                            self.advance_creation_step()
                            return result
                        else:
                            # If the input doesn't match a details command, show the options again
                            return self.start_character_details_step()

                    elif current_step_name == "name":
                        if player_input.lower().startswith('name:') or player_input.lower().startswith('name ') or player_input.lower().startswith('set name:') or player_input.lower().startswith('set name '):
                            try:
                                name = player_input.split(':', 1)[1].strip() if ':' in player_input else player_input.split('name ', 1)[1].strip()
                                print(f"Processing name selection: {name}")
                                result = self.handle_name_selection(name)
                                # Advance to complete step
                                self.advance_creation_step()
                                return result
                            except IndexError:
                                print("Error parsing name selection, using default")
                                result = self.handle_name_selection("Adventurer")
                                # Advance to complete step
                                self.advance_creation_step()
                                return result
                        # If the input doesn't match any of the above patterns but seems to be a name
                        elif len(player_input.split()) <= 3 and not any(cmd in player_input.lower() for cmd in ['roll', 'choose', 'use', 'create', 'attack', 'cast', 'move']):
                            print(f"Treating input as character name: {player_input}")
                            result = self.handle_name_selection(player_input)
                            # Advance to complete step
                            self.advance_creation_step()
                            return result
                        else:
                            # If the input doesn't match a name command, show the options again
                            return self.start_name_step()

                    # If we're at the introduction step and the input isn't 'create character', start the process
                    elif current_step_name == "introduction" and not player_input.lower().startswith('create character'):
                        print("Starting character creation process...")
                        # Advance to ability scores step
                        self.advance_creation_step()
                        return self.start_ability_scores_step()

                    # If we're at the complete step, transition to adventure mode
                    elif current_step_name == "complete":
                        print("Character creation complete, transitioning to adventure mode...")
                        self.mode = 'adventure'
                        if 'mode' in self.game_state:
                            self.game_state['mode'] = 'adventure'

                        adventure_message = "Your character is now complete! You're ready to begin your adventure. What would you like to do first?"
                        self.conversation_history.append(f"DM: {adventure_message}")

                        # Add to DM messages for web UI
                        if 'dm_messages' in self.game_state:
                            self.game_state['dm_messages'].append(adventure_message)

                        return adventure_message

                except Exception as e:
                    print(f"Error in character creation command processing: {str(e)}")
                    import traceback
                    traceback.print_exc()

                    # Use the default character creation as fallback
                    print("Using default character creation as fallback")
                    return self.create_default_character()

            # If we're not in character creation mode, process the input normally
            # Build context for DMA
            try:
                context = self.get_simplified_context()
                print(f"Got simplified context with {len(json.dumps(context))} characters")

                # Add mode information to context
                if hasattr(self, 'mode') and self.mode:
                    context['mode'] = self.mode

                # Build DMA prompt with context and history
                full_prompt = f"{self.prompts['DMA']}\n\nGAME STATE:\n{json.dumps(context, indent=2)}\n\nCONVERSATION HISTORY:\n"

                # Add last 3 exchanges from conversation history to keep context manageable
                recent_history = self.conversation_history[-6:] if len(self.conversation_history) > 6 else self.conversation_history
                full_prompt += "\n".join(recent_history)

                # Add current player input
                full_prompt += f"\n\nCURRENT INPUT:\n{player_input}\n\nYour response:"

                print(f"Built DMA prompt with {len(full_prompt)} characters")
            except Exception as e:
                print(f"Error building DMA prompt: {str(e)}")
                import traceback
                traceback.print_exc()

                # Create a simplified prompt if context building fails
                full_prompt = f"{self.prompts['DMA']}\n\nYou are the Dungeon Master for an AD&D 1st Edition game. The player has said: {player_input}\n\nPlease respond appropriately."

            print("Requesting response from DMA...")

            # Call OpenRouter with the DMA prompt
            agent_response_data = self.call_openrouter(full_prompt)

            if agent_response_data and 'choices' in agent_response_data and len(agent_response_data['choices']) > 0:
                agent_response = agent_response_data['choices'][0]['message']['content']
                self.update_token_usage(agent_response_data)

                # Extract any agent requests from the DMA response
                agent_request = self.extract_agent_request(agent_response)

                if agent_request:
                    print(f"DMA is requesting help from {agent_request.get('target_agent', 'unknown agent')}...")

                    # Process the agent request
                    json_response = self.process_agent_request(agent_request)

                    # If we got a response, integrate it with the DMA
                    if json_response:
                        # Get updated context after agent interaction
                        updated_context = self.get_simplified_context()

                        # Add any combat summary if available
                        combat_summary = ""
                        if agent_request.get('target_agent') == 'CRA' and json_response.get('action_type') == 'attack':
                            # Check if there's a combat result to summarize
                            if 'outcome' in json_response and json_response.get('success', False):
                                target_id = json_response.get('target_id', '')
                                damage = json_response.get('damage', 0)

                                # Find the target in the game state
                                target = None
                                for creature in self.game_state.get('environment', {}).get('creatures', []):
                                    if creature.get('id') == target_id:
                                        target = creature
                                        break

                                if target:
                                    combat_summary = f"\n\nCombat Summary:\n{target.get('name', 'Enemy')} took {damage} damage and now has {target.get('hp', {}).get('current', 0)}/{target.get('hp', {}).get('maximum', 0)} HP."
                                    if target.get('hp', {}).get('current', 0) <= 0:
                                        combat_summary += f" {target.get('name', 'Enemy')} has been defeated!"

                        # Build integration prompt
                        target_agent = agent_request.get('target_agent', 'unknown')
                        integration_prompt = f"{self.prompts['DMA']}\n\nGAME STATE:\n{json.dumps(updated_context, indent=2)}\n\nYou asked for information from {target_agent} about the player's action: {player_input}\n\nThe {target_agent} responded with:\n{json.dumps(json_response, indent=2) if json_response else agent_response}{combat_summary}\n\nPlease integrate this information into your narrative response to the player, making sure to accurately reflect the current HP values. If a creature was defeated (reduced to 0 HP), clearly state that it has been defeated:"

                        print(f"Integrating {target_agent} response with DMA...")

                        # Call OpenRouter for the integration
                        final_response_data = self.call_openrouter(integration_prompt)

                        if final_response_data and 'choices' in final_response_data and len(final_response_data['choices']) > 0:
                            agent_response = final_response_data['choices'][0]['message']['content']
                            self.update_token_usage(final_response_data)

                # Add to conversation history
                self.conversation_history.append(f"DM: {agent_response}")

                # Process any enemy turns if this was a player's combat action
                if "attack" in player_input.lower() and any(creature.get('hp', {}).get('current', 0) > 0 for creature in self.game_state.get('environment', {}).get('creatures', [])):
                    enemy_response = self.enemy_turn()
                    if enemy_response:
                        agent_response += f"\n\n{enemy_response}"

                return agent_response
            else:
                error_message = "I'm having trouble connecting to the game server. Please try again in a moment."
                self.conversation_history.append(f"DM: {error_message}")
                return error_message

        except Exception as e:
            print(f"Error in process_player_input: {str(e)}")
            import traceback
            traceback.print_exc()

            # Check if we're in character creation mode
            if hasattr(self, 'mode') and self.mode == 'create_character':
                print("Using default character creation as global fallback")
                return self.create_default_character()
            else:
                # Provide a fallback response for non-character creation
                error_message = "I encountered an error processing your request. Let's try again. What would you like to do?"

                # Add to conversation history
                self.conversation_history.append(f"DM: {error_message}")

                # Add to DM messages for web UI
                if hasattr(self, 'game_state') and isinstance(self.game_state, dict) and 'dm_messages' in self.game_state:
                    self.game_state['dm_messages'].append(error_message)

                return error_message

    def start_ability_scores_step(self):
        """Start the ability scores step of character creation"""
        print("Starting ability scores step")

        # Create a message explaining ability score options
        ability_message = """Let's begin by determining your ability scores. You have three options:

1. Roll Ability Scores: I'll roll 4d6 and drop the lowest die for each ability score.
2. Standard Array: Use the standard array of 15, 14, 13, 12, 10, 8 for your ability scores.
3. Point Buy: Allocate points to build your ability scores.

Which method would you like to use?"""

        # Add to conversation history
        self.conversation_history.append(f"DM: {ability_message}")
        print(f"\nDM: {ability_message}")

        # Add to DM messages for web UI
        if 'dm_messages' in self.game_state:
            self.game_state['dm_messages'].append(ability_message)

        # If running in terminal mode (not web), wait for user input
        if not hasattr(self, 'web_mode') or not self.web_mode:
            print("\nOptions:")
            print("1. Type 'roll ability scores' to roll for your ability scores")
            print("2. Type 'standard array' to use the standard array")
            print("3. Type 'point buy' to use the point buy system")

        return ability_message

    def start_race_step(self):
        """Start the race step of character creation"""
        print("Starting race step")

        # Create a message explaining race options
        race_message = """Now, let's select your character's race. Each race provides different bonuses and abilities.

Choose from: Human, Elf, Dwarf, Halfling, Half-Elf, Half-Orc, or Gnome.

Which race would you like to play?"""

        # Add to conversation history
        self.conversation_history.append(f"DM: {race_message}")
        print(f"\nDM: {race_message}")

        # Add to DM messages for web UI
        if 'dm_messages' in self.game_state:
            self.game_state['dm_messages'].append(race_message)

        # If running in terminal mode (not web), show options
        if not hasattr(self, 'web_mode') or not self.web_mode:
            print("\nOptions:")
            print("1. Type 'choose race: Human' for Human")
            print("2. Type 'choose race: Elf' for Elf")
            print("3. Type 'choose race: Dwarf' for Dwarf")
            print("4. Type 'choose race: Halfling' for Halfling")
            print("5. Type 'choose race: Half-Elf' for Half-Elf")
            print("6. Type 'choose race: Half-Orc' for Half-Orc")
            print("7. Type 'choose race: Gnome' for Gnome")

        return race_message

    def start_class_step(self):
        """Start the class step of character creation"""
        print("Starting class step")

        # Create a message explaining class options
        class_message = """Now, let's select your character's class. Your class determines your character's abilities, skills, and role in the party.

Choose from: Fighter, Cleric, Mage, Thief, Ranger, Paladin, Druid, or Bard.

Which class would you like to play?"""

        # Add to conversation history
        self.conversation_history.append(f"DM: {class_message}")
        print(f"\nDM: {class_message}")

        # Add to DM messages for web UI
        if 'dm_messages' in self.game_state:
            self.game_state['dm_messages'].append(class_message)

        # If running in terminal mode (not web), show options
        if not hasattr(self, 'web_mode') or not self.web_mode:
            print("\nOptions:")
            print("1. Type 'choose class: Fighter' for Fighter")
            print("2. Type 'choose class: Cleric' for Cleric")
            print("3. Type 'choose class: Mage' for Mage")
            print("4. Type 'choose class: Thief' for Thief")
            print("5. Type 'choose class: Ranger' for Ranger")
            print("6. Type 'choose class: Paladin' for Paladin")
            print("7. Type 'choose class: Druid' for Druid")
            print("8. Type 'choose class: Bard' for Bard")

        return class_message

    def start_alignment_step(self):
        """Start the alignment step of character creation"""
        print("Starting alignment step")

        # Create a message explaining alignment options
        alignment_message = """Now, let's select your character's alignment. Alignment represents your character's moral and ethical outlook.

Choose from: Lawful Good, Neutral Good, Chaotic Good, Lawful Neutral, True Neutral, Chaotic Neutral, Lawful Evil, Neutral Evil, or Chaotic Evil.

Which alignment best represents your character?"""

        # Add to conversation history
        self.conversation_history.append(f"DM: {alignment_message}")
        print(f"\nDM: {alignment_message}")

        # Add to DM messages for web UI
        if 'dm_messages' in self.game_state:
            self.game_state['dm_messages'].append(alignment_message)

        # If running in terminal mode (not web), show options
        if not hasattr(self, 'web_mode') or not self.web_mode:
            print("\nOptions:")
            print("1. Type 'choose alignment: Lawful Good' for Lawful Good")
            print("2. Type 'choose alignment: Neutral Good' for Neutral Good")
            print("3. Type 'choose alignment: Chaotic Good' for Chaotic Good")
            print("4. Type 'choose alignment: Lawful Neutral' for Lawful Neutral")
            print("5. Type 'choose alignment: True Neutral' for True Neutral")
            print("6. Type 'choose alignment: Chaotic Neutral' for Chaotic Neutral")
            print("7. Type 'choose alignment: Lawful Evil' for Lawful Evil")
            print("8. Type 'choose alignment: Neutral Evil' for Neutral Evil")
            print("9. Type 'choose alignment: Chaotic Evil' for Chaotic Evil")

        return alignment_message

    def start_hit_points_step(self):
        """Start the hit points step of character creation"""
        print("Starting hit points step")

        # Get character information
        character_id = next(iter(self.game_state.get('characters', {})), "player1")
        character = self.game_state['characters'].get(character_id, {})
        class_name = character.get('class', 'Fighter')
        con_score = character.get('abilities', {}).get('constitution', 10)

        # Determine hit die based on class
        hit_die = "d10"  # Default
        if class_name.lower() in ['fighter', 'paladin']:
            hit_die = "d10"
        elif class_name.lower() in ['cleric', 'druid', 'ranger']:
            hit_die = "d8"
        elif class_name.lower() in ['thief', 'assassin', 'monk']:
            hit_die = "d6"
        elif class_name.lower() in ['magic-user', 'illusionist']:
            hit_die = "d4"

        # Determine constitution bonus
        con_bonus = 0
        if con_score >= 15:
            con_bonus = 1
        elif con_score >= 17:
            con_bonus = 2
        elif con_score <= 6:
            con_bonus = -1
        elif con_score <= 3:
            con_bonus = -2

        # Create a message explaining hit point options
        hit_points_message = f"""Now, let's determine your character's hit points. As a {class_name}, you use a {hit_die} for hit points.

Your Constitution score of {con_score} gives you a {'bonus' if con_bonus >= 0 else 'penalty'} of {con_bonus:+d} to your hit points.

You have three options:
1. Roll for hit points: I'll roll your hit die and add your Constitution modifier.
2. Take average hit points: Take the average value of your hit die plus your Constitution modifier.
3. Skip: Use the default hit points for your class.

Type 'roll hit points', 'average hit points', or 'skip' to continue."""

        # Add to conversation history
        self.conversation_history.append(f"DM: {hit_points_message}")
        print(f"\nDM: {hit_points_message}")

        # Add to DM messages for web UI
        if 'dm_messages' in self.game_state:
            self.game_state['dm_messages'].append(hit_points_message)

        return hit_points_message

    def start_equipment_money_step(self):
        """Start the equipment and money step of character creation"""
        print("Starting equipment and money step")

        # Get character information
        character_id = next(iter(self.game_state.get('characters', {})), "player1")
        character = self.game_state['characters'].get(character_id, {})
        class_name = character.get('class', 'Fighter')

        # Determine starting gold formula based on class
        gold_formula = "5d4 × 10"  # Default for Fighter
        if class_name.lower() in ['fighter', 'paladin', 'ranger']:
            gold_formula = "5d4 × 10"
        elif class_name.lower() in ['cleric', 'druid']:
            gold_formula = "3d6 × 10"
        elif class_name.lower() in ['magic-user', 'illusionist']:
            gold_formula = "2d4 × 10"
        elif class_name.lower() in ['thief', 'assassin']:
            gold_formula = "2d6 × 10"
        elif class_name.lower() == 'monk':
            gold_formula = "5d4"

        # Create a message explaining equipment options
        equipment_message = f"""Now, let's determine your character's starting equipment and money. As a {class_name}, you start with {gold_formula} gold pieces.

You have three options:
1. Roll for gold: I'll roll the dice and you can purchase equipment with the result.
2. Choose standard equipment: Take the standard equipment package for your class.
3. Skip: Use the default equipment for your class.

Type 'roll gold', 'standard equipment', or 'skip' to continue."""

        # Add to conversation history
        self.conversation_history.append(f"DM: {equipment_message}")
        print(f"\nDM: {equipment_message}")

        # Add to DM messages for web UI
        if 'dm_messages' in self.game_state:
            self.game_state['dm_messages'].append(equipment_message)

        return equipment_message

    def start_spell_selection_step(self):
        """Start the spell selection step of character creation"""
        print("Starting spell selection step")

        # Get character information
        character_id = next(iter(self.game_state.get('characters', {})), "player1")
        character = self.game_state['characters'].get(character_id, {})
        class_name = character.get('class', 'Fighter')

        # Check if character is a spellcaster
        is_spellcaster = class_name.lower() in ['magic-user', 'illusionist', 'cleric', 'druid']

        if not is_spellcaster:
            # Skip this step for non-spellcasters
            skip_message = f"As a {class_name}, you don't have spellcasting abilities. Skipping spell selection."

            # Add to conversation history
            self.conversation_history.append(f"DM: {skip_message}")
            print(f"\nDM: {skip_message}")

            # Add to DM messages for web UI
            if 'dm_messages' in self.game_state:
                self.game_state['dm_messages'].append(skip_message)

            # Advance to next step
            self.advance_creation_step()

            # Start the next step
            next_step = self.get_creation_step_name()
            if next_step == "character_details":
                return self.start_character_details_step()
            elif next_step == "name":
                return self.start_name_step()
            else:
                return f"Advanced to step: {next_step}"

        # Determine spell options based on class
        if class_name.lower() == 'magic-user':
            spell_options = "Read Magic plus 1d4 additional 1st-level spells from the Magic-User spell list"
            ability = "Intelligence"
        elif class_name.lower() == 'illusionist':
            spell_options = "Read Magic plus 1d4 additional 1st-level spells from the Illusionist spell list"
            ability = "Intelligence"
        elif class_name.lower() == 'cleric':
            spell_options = "All 1st-level Cleric spells (you can memorize a number based on your Wisdom)"
            ability = "Wisdom"
        elif class_name.lower() == 'druid':
            spell_options = "All 1st-level Druid spells (you can memorize a number based on your Wisdom)"
            ability = "Wisdom"
        else:
            spell_options = "Unknown"
            ability = "Unknown"

        # Create a message explaining spell options
        spell_message = f"""Now, let's select your character's starting spells. As a {class_name}, you have access to {spell_options}.

Your {ability} score determines how many spells you can memorize and cast.

You have three options:
1. Choose spells: Select specific spells for your spellbook or repertoire.
2. Random spells: Let me randomly determine your starting spells.
3. Skip: Use the default spells for your class.

Type 'choose spells', 'random spells', or 'skip' to continue."""

        # Add to conversation history
        self.conversation_history.append(f"DM: {spell_message}")
        print(f"\nDM: {spell_message}")

        # Add to DM messages for web UI
        if 'dm_messages' in self.game_state:
            self.game_state['dm_messages'].append(spell_message)

        return spell_message

    def start_character_details_step(self):
        """Start the character details step of character creation"""
        print("Starting character details step")

        # Get character information
        character_id = next(iter(self.game_state.get('characters', {})), "player1")
        character = self.game_state['characters'].get(character_id, {})
        class_name = character.get('class', 'Fighter')
        race = character.get('race', 'Human')

        # Create a message explaining character details
        details_message = f"""Now, let's finalize your character's details. This includes:

1. Saving throws: Based on your class ({class_name})
2. Attack matrices: Based on your class and level
3. Languages: Based on your race ({race}) and Intelligence
4. Age, height, and weight: Based on your race
5. Background details: Family, homeland, appearance, etc.

You have two options:
1. Calculate details: Go through each detail one by one.
2. Skip: Use the default values for all details.

Type 'calculate details' or 'skip' to continue."""

        # Add to conversation history
        self.conversation_history.append(f"DM: {details_message}")
        print(f"\nDM: {details_message}")

        # Add to DM messages for web UI
        if 'dm_messages' in self.game_state:
            self.game_state['dm_messages'].append(details_message)

        return details_message

    def complete_character_creation(self):
        """Complete the character creation process"""
        print("Completing character creation")

        # Get character information
        character_id = next(iter(self.game_state.get('characters', {})), "player1")
        character = self.game_state['characters'].get(character_id, {})

        # Create a summary of the character
        name = character.get('name', 'Unnamed')
        race = character.get('race', 'Unknown')
        class_name = character.get('class', 'Unknown')
        level = character.get('level', 1)
        alignment = character.get('alignment', 'Unknown')
        hp = character.get('hp', {})
        hp_current = hp.get('current', 0)
        hp_maximum = hp.get('maximum', 0)
        abilities = character.get('abilities', {})

        summary = f"""Character creation complete! Here's a summary of your character:

Name: {name}
Race: {race}
Class: {class_name}
Level: {level}
Alignment: {alignment}
Hit Points: {hp_current}/{hp_maximum}

Abilities:
- Strength: {abilities.get('strength', 'N/A')}
- Dexterity: {abilities.get('dexterity', 'N/A')}
- Constitution: {abilities.get('constitution', 'N/A')}
- Intelligence: {abilities.get('intelligence', 'N/A')}
- Wisdom: {abilities.get('wisdom', 'N/A')}
- Charisma: {abilities.get('charisma', 'N/A')}

Your character is now ready for adventure! You can view your character details in the Character Stats panel.
"""

        # Add to conversation history
        self.conversation_history.append(f"DM: {summary}")
        print(f"\nDM: {summary}")

        # Add to DM messages for web UI
        if 'dm_messages' in self.game_state:
            self.game_state['dm_messages'].append(summary)

        # Set mode to normal gameplay
        self.mode = 'normal'
        self.game_state['mode'] = 'normal'

        return summary

    def start_name_step(self):
        """Start the name step of character creation"""
        print("Starting name step")

        # Create a message asking for a character name
        name_message = """Finally, let's give your character a name. What would you like to name your character?"""

        # Add to conversation history
        self.conversation_history.append(f"DM: {name_message}")
        print(f"\nDM: {name_message}")

        # Add to DM messages for web UI
        if 'dm_messages' in self.game_state:
            self.game_state['dm_messages'].append(name_message)

        # If running in terminal mode (not web), show options
        if not hasattr(self, 'web_mode') or not self.web_mode:
            print("\nOptions:")
            print("Type 'name: YourCharacterName' to set your character's name")
            print("For example: 'name: Aragorn' or 'name: Gandalf'")

        return name_message

    def get_simplified_context(self):
        """Get a simplified version of the game state to reduce token usage"""
        # Get the first character (usually player1)
        player_character = {}
        if self.game_state.get("characters"):
            # Get the first character in the dictionary
            char_id = next(iter(self.game_state.get("characters", {})), None)
            if char_id:
                player_character = self.game_state["characters"][char_id]

        # Create a copy of the game state with only the essential information
        simplified = {
            "player": player_character,
            "environment": {
                "location": self.game_state.get("environment", {}).get("location", ""),
                "description": self.game_state.get("environment", {}).get("description", ""),
                "creatures": self.game_state.get("environment", {}).get("creatures", []),
                "npcs": self.game_state.get("environment", {}).get("npcs", [])
            },
            "world": self.game_state.get("world", {
                "time": {"day": 1, "hour": 12, "minute": 0},
                "weather": {"condition": "Clear"},
                "light": {"condition": "Bright"},
                "resources": {}
            }),
            "exploration": self.game_state.get("exploration", {
                "movement": {},
                "mapping": {},
                "search": {}
            })
        }
        return simplified

    def display_token_usage(self):
        """Display token usage and estimated cost"""
        print("\n=== Token Usage ===")
        print(f"Prompt tokens: {self.token_usage['prompt_tokens']}")
        print(f"Completion tokens: {self.token_usage['completion_tokens']}")
        print(f"Total tokens: {self.token_usage['total_tokens']}")
        print(f"Estimated cost: ${self.token_usage['estimated_cost']:.6f}")
        print("===================")

    def enemy_turn(self):
        """Process enemy turns after player action"""
        # Check if there are any enemies
        enemies = self.game_state.get('environment', {}).get('creatures', [])
        if not enemies:
            return None  # No enemies to take turns

        # Get player character
        player = self.game_state.get('characters', {}).get('player1')
        if not player:
            return None  # No player to attack

        # For each enemy, generate an attack against the player
        enemy_responses = []

        for enemy in enemies:
            # Create a CRA request for the enemy attack
            enemy_request = {
                "request_id": f"enemy_attack_{uuid.uuid4()}",
                "requesting_agent": "DMA",
                "target_agent": "CRA",
                "action_type": "attack",
                "parameters": {
                    "character_id": enemy.get('id'),
                    "character_name": enemy.get('name'),
                    "target": player.get('name'),
                    "target_id": "player1",
                    "weapon": enemy.get('weapons', [{}])[0].get('name', 'Unarmed attack'),
                    "is_enemy_attack": True
                }
            }

            # Build target agent prompt
            context = self.get_simplified_context()
            agent_prompt = f"{self.prompts['CRA']}\n\nGAME STATE:\n{json.dumps(context, indent=2)}\n\nREQUEST:\n{json.dumps(enemy_request, indent=2)}"

            # Call OpenRouter with the CRA prompt
            print(f"{enemy.get('name')} is attacking {player.get('name')}...")
            agent_response_data = self.call_openrouter(agent_prompt)

            if agent_response_data and 'choices' in agent_response_data and len(agent_response_data['choices']) > 0:
                agent_response = agent_response_data['choices'][0]['message']['content']
                self.update_token_usage(agent_response_data)

                # Extract JSON response if present
                json_response = self.extract_json_from_text(agent_response)

                if json_response:
                    # Update player HP based on enemy attack
                    self.update_player_hp(json_response)

                    # Add to enemy responses
                    enemy_responses.append({
                        "enemy_name": enemy.get('name'),
                        "attack_result": json_response
                    })

        # If we have enemy responses, generate a narrative
        if enemy_responses:
            # Build DMA prompt to narrate enemy actions
            context = self.get_simplified_context()

            # Build a detailed combat summary for each enemy action
            combat_summaries = []
            for enemy_response in enemy_responses:
                enemy_name = enemy_response.get('enemy_name', 'Unknown enemy')
                attack_result = enemy_response.get('attack_result', {})
                player_result = attack_result.get('player_combat_result', {})

                if player_result:
                    summary = f"\n{enemy_name.upper()} ATTACK SUMMARY:\n"
                    summary += f"- Player: {player_result.get('player_name', 'Unknown')}\n"
                    summary += f"- Damage dealt: {player_result.get('damage_taken', 0)}\n"
                    summary += f"- Player HP before: {player_result.get('player_hp_before', 0)}/{player_result.get('player_hp_max', 0)}\n"
                    summary += f"- Player HP after: {player_result.get('player_hp_after', 0)}/{player_result.get('player_hp_max', 0)}\n"
                    summary += f"- Player defeated: {'Yes' if player_result.get('player_defeated', False) else 'No'}\n"
                    combat_summaries.append(summary)

            combat_summary_text = "".join(combat_summaries)

            narrative_prompt = f"{self.prompts['DMA']}\n\nGAME STATE:\n{json.dumps(context, indent=2)}\n\nENEMY ACTIONS:\n{json.dumps(enemy_responses, indent=2)}{combat_summary_text}\n\nPlease provide a narrative description of the enemy actions, making sure to accurately reflect the current HP values:"

            # Call OpenRouter with the DMA prompt
            print("Generating enemy action narrative...")
            narrative_response_data = self.call_openrouter(narrative_prompt)

            if narrative_response_data and 'choices' in narrative_response_data and len(narrative_response_data['choices']) > 0:
                narrative = narrative_response_data['choices'][0]['message']['content']
                self.update_token_usage(narrative_response_data)
                return narrative

        return None

    def update_player_hp(self, enemy_attack_response):
        """Update player HP based on enemy attack"""
        if not enemy_attack_response or not isinstance(enemy_attack_response, dict):
            return

        # Create a result object to track what happened
        result = {
            "player_defeated": False,
            "damage_taken": 0,
            "player_name": "",
            "player_hp_before": 0,
            "player_hp_after": 0,
            "player_hp_max": 0
        }

        # Check if attack was successful and caused damage
        if enemy_attack_response.get('success') and enemy_attack_response.get('outcome') == 'hit' and 'damage' in enemy_attack_response:
            damage = enemy_attack_response.get('damage', 0)
            result["damage_taken"] = damage

            if damage <= 0:
                enemy_attack_response["player_combat_result"] = result
                return result

            # Get player character
            player = self.game_state.get('characters', {}).get('player1')
            if not player:
                enemy_attack_response["player_combat_result"] = result
                return result

            # Store player information
            result["player_name"] = player.get('name', "Unknown")
            result["player_hp_max"] = player.get('hp', {}).get('maximum', 0)
            result["player_hp_before"] = player.get('hp', {}).get('current', 0)

            # Apply damage to player
            current_hp = player.get('hp', {}).get('current', 0)
            max_hp = player.get('hp', {}).get('maximum', 0)
            new_hp = max(0, current_hp - damage)

            # Update player HP
            self.game_state['characters']['player1']['hp']['current'] = new_hp

            # Update result
            result["player_hp_after"] = new_hp

            print(f"{player.get('name')} took {damage} damage. HP now {new_hp}/{max_hp}")

            # Check if player is defeated
            if new_hp <= 0:
                result["player_defeated"] = True
                print(f"{player.get('name')} has been defeated!")

        # Add the result to the response
        enemy_attack_response["player_combat_result"] = result
        return result

    def update_exploration_state(self, agent_request, agent_response):
        """Update exploration state based on EEA response"""
        # Use the AgentStateHandlers to update the exploration state
        self.game_state = AgentStateHandlers.update_exploration_state(
            self.game_state, agent_request, agent_response
        )
        print("Updated exploration state")

    def update_world_state(self, agent_request, agent_response):
        """Update world state based on WEA response"""
        # Use the AgentStateHandlers to update the world state
        self.game_state = AgentStateHandlers.update_world_state(
            self.game_state, agent_request, agent_response
        )
        print("Updated world state")

    def update_npc_state(self, agent_request, agent_response):
        """Update NPC state based on NEA response"""
        # Use the AgentStateHandlers to update the NPC state
        self.game_state = AgentStateHandlers.update_npc_state(
            self.game_state, agent_request, agent_response
        )
        print("Updated NPC state")

    def update_character_state(self, agent_request, agent_response):
        """Update character state based on CMA response"""
        print("Updating character state with improved method")

        # Make sure we have a valid response
        if not agent_response or not isinstance(agent_response, dict):
            print("Invalid agent response for character update")
            return

        # Get the action type
        action_type = agent_response.get('action_type', '')

        # Initialize characters dictionary if it doesn't exist
        if 'characters' not in self.game_state:
            self.game_state['characters'] = {}

        # Handle character creation steps
        if action_type == 'character_creation_step':
            # Get the step
            step = agent_request.get('parameters', {}).get('step', '')
            print(f"Processing character creation step: {step}")

            # Get the character ID
            character_id = agent_response.get('character_id', agent_request.get('parameters', {}).get('character_id', 'player1'))
            print(f"Using character ID: {character_id}")

            # Check if we have character data in the outcome
            if 'outcome' not in agent_response:
                print("No 'outcome' field found in CMA response")
                # Try to find character data directly in the response
                if isinstance(agent_response, dict) and 'name' in agent_response:
                    print("Using top-level response as character data")
                    character_data = agent_response
                else:
                    print("No usable character data found in CMA response")
                    return
            elif not isinstance(agent_response['outcome'], dict):
                print(f"'outcome' is not a dictionary: {type(agent_response['outcome'])}")
                return
            else:
                # Get the character data from outcome
                character_data = agent_response['outcome']

            # Ensure we have a valid character data dictionary
            if not isinstance(character_data, dict):
                print(f"Character data is not a dictionary: {type(character_data)}")
                return

            # Create or update the character
            if character_id not in self.game_state['characters']:
                # Create a new character
                self.game_state['characters'][character_id] = {
                    "name": "Unnamed",
                    "race": "",
                    "class": "",
                    "level": 1,
                    "alignment": "",
                    "abilities": {},
                    "hp": {
                        "current": 0,
                        "maximum": 0
                    },
                    "armor_class": 10,
                    "weapons": [],
                    "equipment": [],
                    "gold": 0,
                    "experience_points": 0,
                    "next_level_xp": 0
                }

            # Get the existing character
            existing_character = self.game_state['characters'][character_id]

            # Merge the character data with the existing character
            # For each field in character_data, update the existing character
            for key, value in character_data.items():
                # Special handling for certain fields
                if key == 'abilities' and isinstance(value, dict) and isinstance(existing_character.get('abilities'), dict):
                    # Merge abilities
                    for ability, score in value.items():
                        if score is not None:  # Only update if not None
                            existing_character['abilities'][ability] = score
                elif key == 'hp' and isinstance(value, dict) and isinstance(existing_character.get('hp'), dict):
                    # Merge HP
                    for hp_key, hp_value in value.items():
                        if hp_value is not None:  # Only update if not None
                            existing_character['hp'][hp_key] = hp_value
                elif key == 'weapons' and isinstance(value, list) and isinstance(existing_character.get('weapons'), list):
                    # Merge weapons
                    existing_character['weapons'] = value
                elif key == 'equipment' and isinstance(value, list) and isinstance(existing_character.get('equipment'), list):
                    # Merge equipment
                    existing_character['equipment'] = value
                else:
                    # For other fields, only update if the value is not empty
                    if value is not None and value != "":
                        existing_character[key] = value

            # Special handling for race and class to prevent them from being overwritten
            if step == 'race_selection' and 'race' in character_data:
                existing_character['race'] = character_data['race']

            if step == 'class_selection' and 'class' in character_data:
                existing_character['class'] = character_data['class']
                # Update next_level_xp based on class
                existing_character['next_level_xp'] = self.get_next_level_xp(character_data['class'], 1)

            if step == 'alignment_selection' and 'alignment' in character_data:
                existing_character['alignment'] = character_data['alignment']

            if step == 'name_selection' and 'name' in character_data:
                existing_character['name'] = character_data['name']
                # Final check for next_level_xp
                if existing_character.get('next_level_xp', 0) == 0 and 'class' in existing_character:
                    existing_character['next_level_xp'] = self.get_next_level_xp(existing_character['class'], 1)

            # Add creation timestamp if not present
            if 'created_at' not in existing_character:
                existing_character['created_at'] = agent_request.get('timestamp', 'unknown')

            # Initialize history if not present
            if 'history' not in existing_character:
                existing_character['history'] = []

            # Add step to history
            existing_character['history'].append({
                'type': 'creation_step',
                'step': step,
                'timestamp': agent_request.get('timestamp', 'unknown'),
                'explanation': agent_response.get('explanation', f'Character {step} completed')
            })

            print(f"Updated character {character_id} with {step} data")

        else:
            # For other action types, use the AgentStateHandlers
            self.game_state = AgentStateHandlers.update_character_state(
                self.game_state, agent_request, agent_response
            )

    def update_magic_state(self, agent_request, agent_response):
        """Update magic state based on MSA response"""
        # Use the AgentStateHandlers to update the magic state
        self.game_state = AgentStateHandlers.update_magic_state(
            self.game_state, agent_request, agent_response
        )
        print("Updated magic state")

    def update_campaign_state(self, agent_request, agent_response):
        """Update campaign state based on CaMA response"""
        # Use the AgentStateHandlers to update the campaign state
        self.game_state = AgentStateHandlers.update_campaign_state(
            self.game_state, agent_request, agent_response
        )
        print("Updated campaign state")

    def handle_ability_score_generation(self, method):
        """Handle ability score generation during character creation"""
        print(f"Handling ability score generation with method: {method}")

        try:
            # Ensure we have a character ID
            character_id = "player1"
            if 'characters' not in self.game_state:
                self.game_state['characters'] = {}

            # Create a basic character if none exists
            if character_id not in self.game_state['characters']:
                self.game_state['characters'][character_id] = {
                    "name": "Unnamed",
                    "race": "",
                    "class": "",
                    "level": 1,
                    "alignment": "",
                    "abilities": {},
                    "hp": {
                        "current": 0,
                        "maximum": 0
                    },
                    "armor_class": 10,
                    "weapons": [],
                    "equipment": [],
                    "gold": 0,
                    "experience_points": 0,
                    "next_level_xp": 0
                }

            # Create a CMA request for ability score generation
            cma_request = {
                "request_id": f"ability_scores_{uuid.uuid4()}",
                "requesting_agent": "DMA",
                "target_agent": "CMA",
                "action_type": "character_creation_step",
                "workflow": "interactive",  # Add workflow parameter
                "timestamp": datetime.datetime.now().isoformat(),
                "parameters": {
                    "step": "ability_scores",
                    "method": method,
                    "character_id": character_id
                }
            }

            print(f"Created CMA request: {json.dumps(cma_request, indent=2)}")

            # Build CMA prompt
            context = self.get_simplified_context()
            print(f"Got simplified context with {len(json.dumps(context))} characters")

            agent_prompt = f"{self.prompts['CMA']}\n\nGAME STATE:\n{json.dumps(context, indent=2)}\n\nREQUEST:\n{json.dumps(cma_request, indent=2)}\n\nIMPORTANT: This is step 1 of character creation - ability score generation. The player has chosen the {method} method. Generate appropriate ability scores and provide a clear explanation of the results."

            print(f"Built CMA prompt with {len(agent_prompt)} characters")

            # Call OpenRouter with the CMA prompt
            print("Requesting ability score generation from CMA...")
            agent_response_data = self.call_openrouter(agent_prompt)

            if agent_response_data and 'choices' in agent_response_data and len(agent_response_data['choices']) > 0:
                agent_response = agent_response_data['choices'][0]['message']['content']
                self.update_token_usage(agent_response_data)

                print(f"Got CMA response: {agent_response[:100]}...")

                # Extract JSON response
                json_response = self.extract_json_from_text(agent_response)

                if json_response:
                    print(f"Extracted JSON response: {json.dumps(json_response, indent=2)[:200]}...")

                    # Update game state with character data
                    try:
                        self.update_character_state(cma_request, json_response)
                    except Exception as e:
                        print(f"Error updating character state: {str(e)}")
                        # Apply fallback ability scores directly
                        self.apply_fallback_ability_scores(character_id, method)

                    # Extract the explanation from the CMA response
                    explanation = json_response.get('explanation', '')

                    # Add the CMA's guidance to DM messages
                    if explanation:
                        dm_guidance = explanation
                        self.conversation_history.append(f"DM: {dm_guidance}")
                        print(f"\nDM: {dm_guidance}")

                        # Add to DM messages for web UI
                        if 'dm_messages' in self.game_state:
                            self.game_state['dm_messages'].append(dm_guidance)
                    else:
                        # If no explanation, create a default one
                        dm_guidance = self.get_default_ability_score_explanation(method)
                        self.conversation_history.append(f"DM: {dm_guidance}")
                        print(f"\nDM: {dm_guidance}")

                        # Add to DM messages for web UI
                        if 'dm_messages' in self.game_state:
                            self.game_state['dm_messages'].append(dm_guidance)

                    # Now ask for race selection
                    race_prompt = "Now that we have your ability scores, let's select your race. Choose from: Human, Elf, Dwarf, Halfling, Half-Elf, Half-Orc, or Gnome."
                    self.conversation_history.append(f"DM: {race_prompt}")
                    print(f"\nDM: {race_prompt}")

                    # Add to DM messages for web UI
                    if 'dm_messages' in self.game_state:
                        self.game_state['dm_messages'].append(race_prompt)

                    return race_prompt
                else:
                    print("Failed to extract JSON from CMA response")

                    # If we couldn't extract JSON, generate default ability scores
                    return self.generate_default_ability_scores(method)
            else:
                print("Failed to get valid response from OpenRouter")

                # If we couldn't get a response, generate default ability scores
                return self.generate_default_ability_scores(method)

        except Exception as e:
            print(f"Error in handle_ability_score_generation: {str(e)}")
            import traceback
            traceback.print_exc()

            # If there was an exception, generate default ability scores
            return self.generate_default_ability_scores(method)

    def apply_fallback_ability_scores(self, character_id, method):
        """Apply fallback ability scores directly to the character"""
        print(f"Applying fallback ability scores for method: {method}")

        # Generate ability scores based on method
        if method == "standard_array":
            abilities = {
                "strength": 15,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8
            }
        elif method == "point_buy":
            abilities = {
                "strength": 14,
                "dexterity": 14,
                "constitution": 14,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10
            }
        else:  # roll
            import random
            abilities = {
                "strength": sum(sorted([random.randint(1, 6) for _ in range(4)])[1:]),
                "dexterity": sum(sorted([random.randint(1, 6) for _ in range(4)])[1:]),
                "constitution": sum(sorted([random.randint(1, 6) for _ in range(4)])[1:]),
                "intelligence": sum(sorted([random.randint(1, 6) for _ in range(4)])[1:]),
                "wisdom": sum(sorted([random.randint(1, 6) for _ in range(4)])[1:]),
                "charisma": sum(sorted([random.randint(1, 6) for _ in range(4)])[1:])
            }

        # Apply the ability scores to the character
        if 'characters' in self.game_state and character_id in self.game_state['characters']:
            self.game_state['characters'][character_id]['abilities'] = abilities
            print(f"Applied fallback ability scores: {json.dumps(abilities, indent=2)}")
        else:
            print(f"Warning: Could not find character {character_id} to apply fallback ability scores")

    def get_default_ability_score_explanation(self, method):
        """Get a default explanation for ability scores based on method"""
        if method == "standard_array":
            return "Using the standard array (15, 14, 13, 12, 10, 8), I've assigned your ability scores. Strength is your highest at 15, followed by Dexterity at 14, Constitution at 13, Intelligence at 12, Wisdom at 10, and Charisma at 8."
        elif method == "point_buy":
            return "Using the point buy system, I've created a balanced character with Strength, Dexterity, and Constitution all at 14, and Intelligence, Wisdom, and Charisma all at 10."
        else:  # roll
            return "I've rolled 4d6 (dropping the lowest die) for each of your ability scores. Your character has a good mix of strengths and weaknesses that will make for interesting gameplay."

    def get_next_level_xp(self, character_class, current_level):
        """Get the XP required for the next level based on class and current level"""
        print(f"Looking up next level XP for {character_class} at level {current_level}")

        # Normalize class name
        class_name = character_class.lower().strip()

        # XP tables for AD&D 1st Edition classes
        xp_tables = {
            "fighter": [0, 2000, 4000, 8000, 16000, 32000, 64000, 125000, 250000, 500000, 750000],
            "paladin": [0, 2750, 5500, 12000, 24000, 45000, 95000, 175000, 350000, 700000, 1050000],
            "ranger": [0, 2250, 4500, 10000, 20000, 40000, 90000, 150000, 300000, 600000, 900000],
            "cleric": [0, 1500, 3000, 6000, 13000, 27500, 55000, 110000, 225000, 450000, 675000],
            "druid": [0, 2000, 4000, 7500, 12500, 20000, 35000, 60000, 90000, 125000, 200000],
            "magic-user": [0, 2500, 5000, 10000, 22500, 40000, 60000, 90000, 135000, 250000, 375000],
            "illusionist": [0, 2250, 4500, 9000, 18000, 35000, 70000, 140000, 250000, 400000, 600000],
            "thief": [0, 1250, 2500, 5000, 10000, 20000, 40000, 70000, 110000, 160000, 220000],
            "assassin": [0, 1500, 3000, 6000, 12000, 25000, 50000, 100000, 200000, 300000, 400000],
            "monk": [0, 2000, 4000, 8000, 16000, 32000, 64000, 125000, 250000, 500000, 750000],
            "bard": [0, 1500, 3000, 6000, 12000, 25000, 50000, 100000, 200000, 300000, 400000]
        }

        # Default XP table for unknown classes
        default_xp_table = [0, 2000, 4000, 8000, 16000, 32000, 64000, 125000, 250000, 500000, 750000]

        # Find the closest matching class
        matching_class = None
        for known_class in xp_tables.keys():
            if known_class in class_name or class_name in known_class:
                matching_class = known_class
                break

        # Get the XP table for the class
        xp_table = xp_tables.get(matching_class, default_xp_table)

        # Make sure the current level is valid
        if current_level < 0:
            current_level = 0
        if current_level >= len(xp_table) - 1:
            # For levels beyond the table, use a formula
            return xp_table[-1] + (xp_table[-1] - xp_table[-2]) * (current_level - len(xp_table) + 2)

        # Return the XP required for the next level
        next_level_xp = xp_table[current_level]
        print(f"Next level XP for {character_class} at level {current_level}: {next_level_xp}")
        return next_level_xp

    def generate_default_ability_scores(self, method):
        """Generate default ability scores as a fallback"""
        print(f"Generating default ability scores using method: {method}")

        # Create a basic character with default ability scores
        character_id = "player1"

        # Generate ability scores based on method
        if method == "standard_array":
            abilities = {
                "strength": 15,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8
            }
            explanation = "Using the standard array (15, 14, 13, 12, 10, 8), I've assigned your ability scores. Strength is your highest at 15, followed by Dexterity at 14, Constitution at 13, Intelligence at 12, Wisdom at 10, and Charisma at 8."
        elif method == "point_buy":
            abilities = {
                "strength": 14,
                "dexterity": 14,
                "constitution": 14,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 10
            }
            explanation = "Using the point buy system, I've created a balanced character with Strength, Dexterity, and Constitution all at 14, and Intelligence, Wisdom, and Charisma all at 10."
        else:  # roll
            import random
            abilities = {
                "strength": sum(sorted([random.randint(1, 6) for _ in range(4)])[1:]),
                "dexterity": sum(sorted([random.randint(1, 6) for _ in range(4)])[1:]),
                "constitution": sum(sorted([random.randint(1, 6) for _ in range(4)])[1:]),
                "intelligence": sum(sorted([random.randint(1, 6) for _ in range(4)])[1:]),
                "wisdom": sum(sorted([random.randint(1, 6) for _ in range(4)])[1:]),
                "charisma": sum(sorted([random.randint(1, 6) for _ in range(4)])[1:])
            }
            explanation = f"I've rolled your ability scores using the 4d6 drop lowest method. Your scores are: Strength {abilities['strength']}, Dexterity {abilities['dexterity']}, Constitution {abilities['constitution']}, Intelligence {abilities['intelligence']}, Wisdom {abilities['wisdom']}, and Charisma {abilities['charisma']}."

        # Create or update the character in the game state
        if 'characters' not in self.game_state:
            self.game_state['characters'] = {}

        # Create the character with default values
        character_class = "Fighter"  # Default class
        self.game_state['characters'][character_id] = {
            "name": "",
            "race": "",
            "class": character_class,
            "level": 1,
            "alignment": "",
            "abilities": abilities,
            "hp": {
                "current": 0,
                "maximum": 0
            },
            "armor_class": 10,
            "weapons": [],
            "equipment": [],
            "gold": 0,
            "experience_points": 0,
            "next_level_xp": self.get_next_level_xp(character_class, 1)
        }

        # Add the explanation to DM messages
        self.conversation_history.append(f"DM: {explanation}")
        print(f"\nDM: {explanation}")

        # Add to DM messages for web UI
        if 'dm_messages' in self.game_state:
            self.game_state['dm_messages'].append(explanation)

        # Now ask for race selection
        race_prompt = "Now that we have your ability scores, let's select your race. Choose from: Human, Elf, Dwarf, Halfling, Half-Elf, Half-Orc, or Gnome."
        self.conversation_history.append(f"DM: {race_prompt}")
        print(f"\nDM: {race_prompt}")

        # Add to DM messages for web UI
        if 'dm_messages' in self.game_state:
            self.game_state['dm_messages'].append(race_prompt)

        return race_prompt

    def get_race_documentation(self, race_name):
        """Query and store race documentation from rulebooks"""
        print(f"Querying rulebooks for race documentation: {race_name}")

        # Query the rulebooks for race information
        race_query = f"{race_name} race abilities and restrictions AD&D"
        race_docs = self.rulebook_integration.query_rules(race_query, max_results=3)

        # Store the documentation in the game state
        if 'reference_material' not in self.game_state:
            self.game_state['reference_material'] = {}

        if 'races' not in self.game_state['reference_material']:
            self.game_state['reference_material']['races'] = {}

        self.game_state['reference_material']['races'][race_name.lower()] = {
            'documentation': race_docs,
            'queried_at': datetime.datetime.now().isoformat()
        }

        print(f"Stored race documentation for {race_name}")
        return race_docs

    def get_class_documentation(self, class_name):
        """Query and store class documentation from rulebooks"""
        print(f"Querying rulebooks for class documentation: {class_name}")

        # Query the rulebooks for class information
        class_query = f"{class_name} class abilities and restrictions AD&D"
        class_docs = self.rulebook_integration.query_rules(class_query, max_results=3)

        # Store the documentation in the game state
        if 'reference_material' not in self.game_state:
            self.game_state['reference_material'] = {}

        if 'classes' not in self.game_state['reference_material']:
            self.game_state['reference_material']['classes'] = {}

        self.game_state['reference_material']['classes'][class_name.lower()] = {
            'documentation': class_docs,
            'queried_at': datetime.datetime.now().isoformat()
        }

        print(f"Stored class documentation for {class_name}")
        return class_docs

    def get_alignment_documentation(self, alignment):
        """Query and store alignment documentation from rulebooks"""
        print(f"Querying rulebooks for alignment documentation: {alignment}")

        # Query the rulebooks for alignment information
        alignment_query = f"{alignment} alignment restrictions and implications AD&D"
        alignment_docs = self.rulebook_integration.query_rules(alignment_query, max_results=2)

        # Store the documentation in the game state
        if 'reference_material' not in self.game_state:
            self.game_state['reference_material'] = {}

        if 'alignments' not in self.game_state['reference_material']:
            self.game_state['reference_material']['alignments'] = {}

        self.game_state['reference_material']['alignments'][alignment.lower()] = {
            'documentation': alignment_docs,
            'queried_at': datetime.datetime.now().isoformat()
        }

        print(f"Stored alignment documentation for {alignment}")
        return alignment_docs

    def get_race_class_restrictions(self):
        """Query and store race-class restrictions from rulebooks"""
        print("Querying rulebooks for race-class restrictions")

        # Query the rulebooks for race-class restrictions
        restrictions_query = "race class restrictions and level limitations AD&D"
        restrictions_docs = self.rulebook_integration.query_rules(restrictions_query, max_results=2)

        # Store the documentation in the game state
        if 'reference_material' not in self.game_state:
            self.game_state['reference_material'] = {}

        self.game_state['reference_material']['race_class_restrictions'] = {
            'documentation': restrictions_docs,
            'queried_at': datetime.datetime.now().isoformat()
        }

        print("Stored race-class restrictions documentation")
        return restrictions_docs

    def get_class_alignment_restrictions(self):
        """Query and store class-alignment restrictions from rulebooks"""
        print("Querying rulebooks for class-alignment restrictions")

        # Query the rulebooks for class-alignment restrictions
        restrictions_query = "class alignment restrictions AD&D"
        restrictions_docs = self.rulebook_integration.query_rules(restrictions_query, max_results=2)

        # Store the documentation in the game state
        if 'reference_material' not in self.game_state:
            self.game_state['reference_material'] = {}

        self.game_state['reference_material']['class_alignment_restrictions'] = {
            'documentation': restrictions_docs,
            'queried_at': datetime.datetime.now().isoformat()
        }

        print("Stored class-alignment restrictions documentation")
        return restrictions_docs

    def handle_race_selection(self, race):
        """Handle race selection during character creation"""
        print(f"Handling race selection: {race}")

        try:
            # Get race documentation from rulebooks
            race_docs = self.get_race_documentation(race)

            # Get race-class restrictions
            restrictions_docs = self.get_race_class_restrictions()

            # Create a CMA request for race selection
            cma_request = {
                "request_id": f"race_selection_{uuid.uuid4()}",
                "requesting_agent": "DMA",
                "target_agent": "CMA",
                "action_type": "character_creation_step",
                "workflow": "interactive",  # Add workflow parameter
                "timestamp": datetime.datetime.now().isoformat(),
                "parameters": {
                    "step": "race_selection",
                    "race": race,
                    "character_id": next(iter(self.game_state.get('characters', {})), "player1"),
                    "race_documentation": race_docs,
                    "race_class_restrictions": restrictions_docs
                }
            }

            print(f"Created race selection CMA request: {json.dumps(cma_request, indent=2)}")

            # Build CMA prompt
            context = self.get_simplified_context()
            agent_prompt = f"{self.prompts['CMA']}\n\nGAME STATE:\n{json.dumps(context, indent=2)}\n\nREQUEST:\n{json.dumps(cma_request, indent=2)}\n\nIMPORTANT: This is step 2 of character creation - race selection. The player has chosen the {race} race. Update the character with racial traits and provide a clear explanation of the race's benefits and limitations."

            # Call OpenRouter with the CMA prompt
            print("Requesting race selection processing from CMA...")
            agent_response_data = self.call_openrouter(agent_prompt)

            if agent_response_data and 'choices' in agent_response_data and len(agent_response_data['choices']) > 0:
                agent_response = agent_response_data['choices'][0]['message']['content']
                self.update_token_usage(agent_response_data)

                print(f"Got race selection CMA response: {agent_response[:100]}...")

                # Extract JSON response
                json_response = self.extract_json_from_text(agent_response)

                if json_response:
                    print(f"Extracted race selection JSON response")

                    # Update game state with character data
                    self.update_character_state(cma_request, json_response)

                    # Extract the explanation from the CMA response
                    explanation = json_response.get('explanation', '')

                    # Add the CMA's guidance to DM messages
                    if explanation:
                        dm_guidance = explanation
                        self.conversation_history.append(f"DM: {dm_guidance}")
                        print(f"\nDM: {dm_guidance}")

                        # Add to DM messages for web UI
                        if 'dm_messages' in self.game_state:
                            self.game_state['dm_messages'].append(dm_guidance)

                    # Now ask for class selection
                    class_prompt = "Now that you've chosen your race, let's select your class. Choose from: Fighter, Cleric, Mage, Thief, Ranger, Paladin, Druid, or Bard."
                    self.conversation_history.append(f"DM: {class_prompt}")
                    print(f"\nDM: {class_prompt}")

                    # Add to DM messages for web UI
                    if 'dm_messages' in self.game_state:
                        self.game_state['dm_messages'].append(class_prompt)

                    return class_prompt
                else:
                    print("Failed to extract JSON from race selection CMA response")

                    # If we couldn't extract JSON, use a fallback
                    return self.apply_default_race(race)
            else:
                print("Failed to get valid response from OpenRouter for race selection")

                # If we couldn't get a response, use a fallback
                return self.apply_default_race(race)

        except Exception as e:
            print(f"Error in handle_race_selection: {str(e)}")
            import traceback
            traceback.print_exc()

            # If there was an exception, use a fallback
            return self.apply_default_race(race)

    def create_default_character(self):
        """Create a complete default character as a fallback for character creation"""
        print("Creating default character...")

        try:
            # Generate default ability scores
            abilities = {
                "strength": 15,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8
            }

            # Create a basic character
            character_id = "player1"

            # Make sure we have a characters dictionary
            if 'characters' not in self.game_state:
                self.game_state['characters'] = {}

            # Create the character with default values
            character_class = "Fighter"
            self.game_state['characters'][character_id] = {
                "name": "Adventurer",
                "race": "Human",
                "class": character_class,
                "level": 1,
                "alignment": "Neutral Good",
                "abilities": abilities,
                "hp": {
                    "current": 10,
                    "maximum": 10
                },
                "armor_class": 12,
                "weapons": ["Longsword", "Shortbow"],
                "equipment": ["Backpack", "Bedroll", "Rations (5 days)", "Waterskin", "Torches (10)"],
                "gold": 50,
                "experience_points": 0,
                "next_level_xp": self.get_next_level_xp(character_class, 1),
                "racial_traits": {
                    "versatile": "Humans can excel in any class"
                },
                "class_features": {
                    "fighting_style": "One-handed weapons",
                    "second_wind": "Once per rest, regain 1d10 + level HP"
                }
            }

            # Add messages to guide the player
            ability_message = "I've created a default character for you with the following ability scores: Strength 15, Dexterity 14, Constitution 13, Intelligence 12, Wisdom 10, and Charisma 8."
            race_message = "Your character is a Human. Humans are versatile and adaptable, with no specific ability score bonuses but also no penalties. They can advance to unlimited levels in any class."
            class_message = "Your character is a Fighter. Fighters are masters of combat, skilled with all weapons and armor. They have high hit points and excel at dealing and absorbing damage."
            summary_message = "Your character is a level 1 Neutral Good Human Fighter named 'Adventurer'. You have 10 HP, an Armor Class of 12, and are equipped with a longsword and shortbow. You also have basic adventuring gear and 50 gold pieces."
            next_steps_message = "You can now begin your adventure! If you'd like to customize your character further, you can change your name, alignment, or equipment. What would you like to do?"

            # Add messages to conversation history and game state
            for message in [ability_message, race_message, class_message, summary_message, next_steps_message]:
                self.conversation_history.append(f"DM: {message}")
                print(f"\nDM: {message}")

                # Add to DM messages for web UI
                if 'dm_messages' in self.game_state:
                    self.game_state['dm_messages'].append(message)

            return summary_message

        except Exception as e:
            print(f"Error in create_default_character: {str(e)}")
            import traceback
            traceback.print_exc()

            # Provide a very basic fallback response
            error_message = "I encountered an error creating your character. Let's try again. What would you like to do?"
            self.conversation_history.append(f"DM: {error_message}")

            # Add to DM messages for web UI
            if 'dm_messages' in self.game_state:
                self.game_state['dm_messages'].append(error_message)

            return error_message

    def apply_default_race(self, race):
        """Apply default race traits as a fallback"""
        print(f"Applying default race traits for: {race}")

        # Get the character ID (default to player1)
        character_id = next(iter(self.game_state.get('characters', {})), "player1")

        # Make sure we have a character
        if 'characters' not in self.game_state or character_id not in self.game_state['characters']:
            if 'characters' not in self.game_state:
                self.game_state['characters'] = {}

            # Create a basic character if none exists
            character_class = "Fighter"  # Default class
            self.game_state['characters'][character_id] = {
                "name": "",
                "race": "",
                "class": character_class,
                "level": 1,
                "alignment": "",
                "abilities": {
                    "strength": 10,
                    "dexterity": 10,
                    "constitution": 10,
                    "intelligence": 10,
                    "wisdom": 10,
                    "charisma": 10
                },
                "hp": {
                    "current": 0,
                    "maximum": 0
                },
                "armor_class": 10,
                "weapons": [],
                "equipment": [],
                "gold": 0,
                "experience_points": 0,
                "next_level_xp": self.get_next_level_xp(character_class, 1)
            }

        # Apply the race
        self.game_state['characters'][character_id]['race'] = race

        # Try to get race documentation from rulebooks
        race_docs = None
        try:
            if hasattr(self, 'rulebooks_available') and self.rulebooks_available:
                race_docs = self.get_race_documentation(race)
        except Exception as e:
            print(f"Error getting race documentation: {str(e)}")

        # Apply racial traits based on race
        racial_traits = {}
        racial_bonuses = {}

        if race.lower() == "human":
            explanation = f"You've chosen to play as a Human. Humans are versatile and adaptable, with no specific ability score bonuses but also no penalties. They can advance to unlimited levels in any class and are the most common race in most campaign settings."
            racial_traits = {
                "versatile": "Humans can excel in any class and profession",
                "adaptable": "Humans receive a +1 bonus to all ability scores",
                "skilled": "Humans gain proficiency in one additional skill of their choice",
                "ambitious": "Humans gain experience points 10% faster than other races"
            }

        elif race.lower() == "elf":
            explanation = f"You've chosen to play as an Elf. Elves gain +1 to Dexterity but -1 to Constitution. They have infravision, resistance to charm spells, and can detect secret doors more easily. Elves are graceful and long-lived, with a deep connection to nature and magic."
            racial_traits = {
                "infravision": "60 feet",
                "charm_resistance": "90% resistance to charm spells",
                "secret_door_detection": "1-in-6 chance to detect secret doors when passing within 10 feet",
                "keen_senses": "Elves have advantage on Perception checks involving sight or hearing",
                "fey_ancestry": "Elves are immune to sleep magic and have advantage on saves against charm effects",
                "trance": "Elves don't need to sleep, instead they meditate for 4 hours per day",
                "natural_archer": "Elves gain +1 to attack rolls with bows"
            }
            racial_bonuses = {"dexterity": 1, "constitution": -1}

        elif race.lower() == "dwarf":
            explanation = f"You've chosen to play as a Dwarf. Dwarves gain +1 to Constitution but -1 to Charisma. They have infravision, can detect sloping passages, and have resistance to magic and poison. Dwarves are sturdy and resilient, with a strong connection to stone and metalwork."
            racial_traits = {
                "infravision": "60 feet",
                "detect_stonework": "1-in-3 chance to detect stonework traps, sliding walls, or sloping passages",
                "magic_resistance": "+3 bonus to saving throws against magic",
                "poison_resistance": "+3 bonus to saving throws against poison",
                "darkvision": "Dwarves can see in dim light within 60 feet as if it were bright light",
                "dwarven_resilience": "Dwarves have advantage on saving throws against poison and resistance to poison damage",
                "stonecunning": "Dwarves add double their proficiency bonus on History checks related to stonework",
                "dwarven_toughness": "Dwarves gain +2 hit points per level",
                "dwarven_combat_training": "Dwarves are proficient with battleaxes, handaxes, throwing hammers, and warhammers"
            }
            racial_bonuses = {"constitution": 1, "charisma": -1}

        elif race.lower() == "halfling":
            explanation = f"You've chosen to play as a Halfling. Halflings gain +1 to Dexterity but -1 to Strength. They have excellent saving throws, are difficult to hit with missiles, and can hide easily in natural surroundings. Halflings are small but nimble, with a knack for stealth and comfort."
            racial_traits = {
                "saving_throw_bonus": "+4 bonus to saving throws against magic and poison",
                "missile_defense": "+3 bonus to AC against missile attacks",
                "stealth": "90% chance to hide in outdoor settings when motionless",
                "lucky": "Halflings can reroll any 1 on an attack roll, ability check, or saving throw",
                "brave": "Halflings have advantage on saving throws against fear",
                "halfling_nimbleness": "Halflings can move through the space of any creature that is of a size larger than them",
                "naturally_stealthy": "Halflings can attempt to hide even when only obscured by a creature one size larger than them"
            }
            racial_bonuses = {"dexterity": 1, "strength": -1}

        elif race.lower() == "half-elf":
            explanation = f"You've chosen to play as a Half-Elf. Half-Elves combine the best qualities of humans and elves, with the grace of elves and the ambition of humans."
            racial_traits = {
                "infravision": "60 feet",
                "secret_door_detection": "1-in-6 chance to detect secret doors when searching",
                "charm_resistance": "30% resistance to charm and sleep spells",
                "fey_ancestry": "Half-elves have advantage on saving throws against being charmed, and magic can't put them to sleep",
                "skill_versatility": "Half-elves gain proficiency in two skills of their choice",
                "darkvision": "Half-elves can see in dim light within 60 feet as if it were bright light",
                "dual_heritage": "Half-elves count as both human and elf for any effect related to race"
            }
            racial_bonuses = {"charisma": 2, "dexterity": 1, "intelligence": 1}

        elif race.lower() == "half-orc":
            explanation = f"You've chosen to play as a Half-Orc. Half-Orcs combine the strength of orcs with the adaptability of humans, making them formidable warriors."
            racial_traits = {
                "infravision": "60 feet",
                "detect_construction": "3-in-12 chance to detect new construction, sliding walls, or sloping passages",
                "darkvision": "Half-orcs can see in dim light within 60 feet as if it were bright light",
                "relentless_endurance": "When reduced to 0 hit points, a half-orc can drop to 1 hit point instead once per long rest",
                "savage_attacks": "Half-orcs add an extra weapon die on critical hits with melee weapons",
                "intimidating": "Half-orcs have proficiency in the Intimidation skill"
            }
            racial_bonuses = {"strength": 1, "constitution": 1, "charisma": -2}

        elif race.lower() == "gnome":
            explanation = f"You've chosen to play as a Gnome. Gnomes gain +1 to Intelligence but -1 to Wisdom. They have infravision, can detect sloping passages, and have magic resistance. Gnomes are small and clever, with a natural affinity for illusion magic and gem-working."
            racial_traits = {
                "infravision": "60 feet",
                "detect_stonework": "1-in-3 chance to detect stonework traps, sliding walls, or sloping passages",
                "magic_resistance": "+3 bonus to saving throws against magic",
                "darkvision": "Gnomes can see in dim light within 60 feet as if it were bright light",
                "gnome_cunning": "Gnomes have advantage on Intelligence, Wisdom, and Charisma saving throws against magic",
                "artificers_lore": "Gnomes add double their proficiency bonus on History checks related to magic items or technological devices",
                "tinker": "Gnomes can create small mechanical devices with specific simple effects"
            }
            racial_bonuses = {"intelligence": 1, "wisdom": -1}

        else:
            explanation = f"You've chosen to play as a {race}. This race will have standard traits and no special abilities."
            racial_traits = {
                "standard_traits": f"Standard racial traits for {race}"
            }

        # If we have race documentation, try to extract more detailed traits
        if race_docs:
            # Look for trait descriptions in the documentation
            for trait_name in list(racial_traits.keys()):
                # Convert trait name to search terms
                search_term = trait_name.replace('_', ' ')

                # Look for the trait in the documentation
                if search_term.lower() in race_docs.lower():
                    # Find the relevant section
                    start_idx = race_docs.lower().find(search_term.lower())
                    if start_idx != -1:
                        # Extract a reasonable chunk of text
                        end_idx = race_docs.find('\n\n', start_idx)
                        if end_idx == -1:
                            end_idx = min(start_idx + 300, len(race_docs))

                        # Extract the description
                        trait_text = race_docs[start_idx:end_idx].strip()

                        # Update the trait description if we found something substantial
                        if len(trait_text) > len(search_term) + 10:
                            racial_traits[trait_name] = trait_text

        # Apply racial bonuses to ability scores
        if racial_bonuses:
            for ability, bonus in racial_bonuses.items():
                if ability in self.game_state['characters'][character_id]['abilities']:
                    self.game_state['characters'][character_id]['abilities'][ability] += bonus

        # Add racial traits to character
        self.game_state['characters'][character_id]['racial_traits'] = racial_traits

        # Add the explanation to DM messages
        self.conversation_history.append(f"DM: {explanation}")
        print(f"\nDM: {explanation}")

        # Add to DM messages for web UI
        if 'dm_messages' in self.game_state:
            self.game_state['dm_messages'].append(explanation)

        # Now ask for class selection
        class_prompt = "Now that you've chosen your race, let's select your class. Choose from: Fighter, Cleric, Mage, Thief, Ranger, Paladin, Druid, or Bard."
        self.conversation_history.append(f"DM: {class_prompt}")
        print(f"\nDM: {class_prompt}")

        # Add to DM messages for web UI
        if 'dm_messages' in self.game_state:
            self.game_state['dm_messages'].append(class_prompt)

        return class_prompt

    def handle_alignment_selection(self, alignment):
        """Handle alignment selection during character creation"""
        print(f"Handling alignment selection: {alignment}")

        try:
            # Get the character ID (default to player1)
            character_id = next(iter(self.game_state.get('characters', {})), "player1")

            # Get the character's class and race
            character_class = ""
            character_race = ""
            if 'characters' in self.game_state and character_id in self.game_state['characters']:
                character_class = self.game_state['characters'][character_id].get('class', "")
                character_race = self.game_state['characters'][character_id].get('race', "")

            # Validate class-alignment combination
            is_valid, message = self.validate_race_class_alignment(race=character_race, character_class=character_class, alignment=alignment)
            if not is_valid:
                print(f"Invalid class-alignment combination: {message}")
                return message

            # Get alignment documentation from rulebooks
            alignment_docs = self.get_alignment_documentation(alignment)

            # Get class-alignment restrictions if not already loaded
            if 'reference_material' not in self.game_state or 'class_alignment_restrictions' not in self.game_state['reference_material']:
                alignment_restrictions = self.get_class_alignment_restrictions()
            else:
                alignment_restrictions = self.game_state['reference_material']['class_alignment_restrictions']['documentation']

            # Create a CMA request for alignment selection
            cma_request = {
                "request_id": f"alignment_selection_{uuid.uuid4()}",
                "requesting_agent": "DMA",
                "target_agent": "CMA",
                "action_type": "character_creation_step",
                "workflow": "interactive",  # Add workflow parameter
                "timestamp": datetime.datetime.now().isoformat(),
                "parameters": {
                    "step": "alignment_selection",
                    "alignment": alignment,
                    "character_id": character_id,
                    "character_class": character_class,
                    "alignment_documentation": alignment_docs,
                    "class_alignment_restrictions": alignment_restrictions
                }
            }

            print(f"Created alignment selection CMA request: {json.dumps(cma_request, indent=2)}")

            # Build CMA prompt
            context = self.get_simplified_context()
            agent_prompt = f"{self.prompts['CMA']}\n\nGAME STATE:\n{json.dumps(context, indent=2)}\n\nREQUEST:\n{json.dumps(cma_request, indent=2)}\n\nIMPORTANT: This is step 4 of character creation - alignment selection. The player has chosen the {alignment} alignment. Update the character with alignment information and provide a clear explanation of the alignment's implications."

            # Call OpenRouter with the CMA prompt
            print("Requesting alignment selection processing from CMA...")
            agent_response_data = self.call_openrouter(agent_prompt)

            if agent_response_data and 'choices' in agent_response_data and len(agent_response_data['choices']) > 0:
                agent_response = agent_response_data['choices'][0]['message']['content']
                self.update_token_usage(agent_response_data)

                print(f"Got alignment selection CMA response: {agent_response[:100]}...")

                # Extract JSON response
                json_response = self.extract_json_from_text(agent_response)

                if json_response:
                    print(f"Extracted alignment selection JSON response")

                    # Update game state with character data
                    self.update_character_state(cma_request, json_response)

                    # Extract the explanation from the CMA response
                    explanation = json_response.get('explanation', '')

                    # Add the CMA's guidance to DM messages
                    if explanation:
                        dm_guidance = explanation
                        self.conversation_history.append(f"DM: {dm_guidance}")
                        print(f"\nDM: {dm_guidance}")

                        # Add to DM messages for web UI
                        if 'dm_messages' in self.game_state:
                            self.game_state['dm_messages'].append(dm_guidance)

                    # Now ask for character name
                    name_prompt = "Finally, let's give your character a name. What would you like to name your character?"
                    self.conversation_history.append(f"DM: {name_prompt}")
                    print(f"\nDM: {name_prompt}")

                    # Add to DM messages for web UI
                    if 'dm_messages' in self.game_state:
                        self.game_state['dm_messages'].append(name_prompt)

                    return name_prompt
                else:
                    print("Failed to extract JSON from alignment selection CMA response")

                    # If we couldn't extract JSON, use a fallback
                    return self.apply_default_alignment(alignment)
            else:
                print("Failed to get valid response from OpenRouter for alignment selection")

                # If we couldn't get a response, use a fallback
                return self.apply_default_alignment(alignment)

        except Exception as e:
            print(f"Error in handle_alignment_selection: {str(e)}")
            import traceback
            traceback.print_exc()

            # If there was an exception, use a fallback
            return self.apply_default_alignment(alignment)

    def handle_name_selection(self, name):
        """Handle character name selection during character creation"""
        print(f"Handling name selection: {name}")

        try:
            # Create a CMA request for name selection
            cma_request = {
                "request_id": f"name_selection_{uuid.uuid4()}",
                "requesting_agent": "DMA",
                "target_agent": "CMA",
                "action_type": "character_creation_step",
                "workflow": "interactive",  # Add workflow parameter
                "timestamp": datetime.datetime.now().isoformat(),
                "parameters": {
                    "step": "name_selection",
                    "name": name,
                    "character_id": next(iter(self.game_state.get('characters', {})), "player1")
                }
            }

            print(f"Created name selection CMA request: {json.dumps(cma_request, indent=2)}")

            # Build CMA prompt
            context = self.get_simplified_context()
            agent_prompt = f"{self.prompts['CMA']}\n\nGAME STATE:\n{json.dumps(context, indent=2)}\n\nREQUEST:\n{json.dumps(cma_request, indent=2)}\n\nIMPORTANT: This is the final step of character creation - name selection. The player has chosen the name {name}. Update the character with this name and provide a summary of the completed character."

            # Call OpenRouter with the CMA prompt
            print("Requesting name selection processing from CMA...")
            agent_response_data = self.call_openrouter(agent_prompt)

            if agent_response_data and 'choices' in agent_response_data and len(agent_response_data['choices']) > 0:
                agent_response = agent_response_data['choices'][0]['message']['content']
                self.update_token_usage(agent_response_data)

                print(f"Got name selection CMA response: {agent_response[:100]}...")

                # Extract JSON response
                json_response = self.extract_json_from_text(agent_response)

                if json_response:
                    print(f"Extracted name selection JSON response")

                    # Update game state with character data
                    self.update_character_state(cma_request, json_response)

                    # Extract the explanation from the CMA response
                    explanation = json_response.get('explanation', '')

                    # Add the CMA's guidance to DM messages
                    if explanation:
                        dm_guidance = explanation
                        self.conversation_history.append(f"DM: {dm_guidance}")
                        print(f"\nDM: {dm_guidance}")

                        # Add to DM messages for web UI
                        if 'dm_messages' in self.game_state:
                            self.game_state['dm_messages'].append(dm_guidance)

                    # Character creation is complete, provide a summary
                    character_id = next(iter(self.game_state.get('characters', {})), "player1")
                    character = self.game_state['characters'].get(character_id, {})

                    summary = self.generate_character_summary(character)
                    self.conversation_history.append(f"DM: {summary}")
                    print(f"\nDM: {summary}")

                    # Add to DM messages for web UI
                    if 'dm_messages' in self.game_state:
                        self.game_state['dm_messages'].append(summary)

                    # Add a message about starting the adventure
                    adventure_message = "Your character is now complete! You're ready to begin your adventure. What would you like to do first?"
                    self.conversation_history.append(f"DM: {adventure_message}")
                    print(f"\nDM: {adventure_message}")

                    # Add to DM messages for web UI
                    if 'dm_messages' in self.game_state:
                        self.game_state['dm_messages'].append(adventure_message)

                    # Update the mode to 'adventure'
                    self.mode = 'adventure'
                    if 'mode' in self.game_state:
                        self.game_state['mode'] = 'adventure'

                    return adventure_message
                else:
                    print("Failed to extract JSON from name selection CMA response")

                    # If we couldn't extract JSON, use a fallback
                    return self.apply_default_name(name)
            else:
                print("Failed to get valid response from OpenRouter for name selection")

                # If we couldn't get a response, use a fallback
                return self.apply_default_name(name)

        except Exception as e:
            print(f"Error in handle_name_selection: {str(e)}")
            import traceback
            traceback.print_exc()

            # If there was an exception, use a fallback
            return self.apply_default_name(name)

    def apply_default_name(self, name):
        """Apply default name as a fallback"""
        print(f"Applying default name: {name}")

        # Get the character ID (default to player1)
        character_id = next(iter(self.game_state.get('characters', {})), "player1")

        # Make sure we have a character
        if 'characters' not in self.game_state or character_id not in self.game_state['characters']:
            if 'characters' not in self.game_state:
                self.game_state['characters'] = {}

            # Create a basic character if none exists
            self.game_state['characters'][character_id] = {
                "name": "",
                "race": "Human",
                "class": "Fighter",
                "level": 1,
                "alignment": "Neutral Good",
                "abilities": {
                    "strength": 10,
                    "dexterity": 10,
                    "constitution": 10,
                    "intelligence": 10,
                    "wisdom": 10,
                    "charisma": 10
                },
                "hp": {
                    "current": 10,
                    "maximum": 10
                },
                "armor_class": 10,
                "weapons": [],
                "equipment": [],
                "gold": 0,
                "experience_points": 0,
                "next_level_xp": 0
            }

        # Apply the name
        self.game_state['characters'][character_id]['name'] = name

        # Generate a character summary
        character = self.game_state['characters'][character_id]
        summary = self.generate_character_summary(character)

        # Add the summary to DM messages
        self.conversation_history.append(f"DM: {summary}")
        print(f"\nDM: {summary}")

        # Add to DM messages for web UI
        if 'dm_messages' in self.game_state:
            self.game_state['dm_messages'].append(summary)

        # Add a message about starting the adventure
        adventure_message = "Your character is now complete! You're ready to begin your adventure. What would you like to do first?"
        self.conversation_history.append(f"DM: {adventure_message}")
        print(f"\nDM: {adventure_message}")

        # Add to DM messages for web UI
        if 'dm_messages' in self.game_state:
            self.game_state['dm_messages'].append(adventure_message)

        # Update the mode to 'adventure'
        self.mode = 'adventure'
        if 'mode' in self.game_state:
            self.game_state['mode'] = 'adventure'

        return adventure_message

    def generate_character_summary(self, character):
        """Generate a summary of the character"""
        name = character.get('name', 'Unnamed')
        race = character.get('race', 'Unknown')
        character_class = character.get('class', 'Unknown')
        level = character.get('level', 1)
        alignment = character.get('alignment', 'Unknown')

        # Get ability scores
        abilities = character.get('abilities', {})
        str_score = abilities.get('strength', 10)
        dex_score = abilities.get('dexterity', 10)
        con_score = abilities.get('constitution', 10)
        int_score = abilities.get('intelligence', 10)
        wis_score = abilities.get('wisdom', 10)
        cha_score = abilities.get('charisma', 10)

        # Get HP and AC
        hp = character.get('hp', {})
        current_hp = hp.get('current', 0)
        max_hp = hp.get('maximum', 0)
        ac = character.get('armor_class', 10)

        # Get equipment
        weapons = character.get('weapons', [])
        equipment = character.get('equipment', [])
        gold = character.get('gold', 0)

        # Build the summary
        summary = f"Character Summary:\n\n"
        summary += f"{name} is a level {level} {alignment} {race} {character_class}.\n\n"
        summary += f"Ability Scores:\n"
        summary += f"- Strength: {str_score}\n"
        summary += f"- Dexterity: {dex_score}\n"
        summary += f"- Constitution: {con_score}\n"
        summary += f"- Intelligence: {int_score}\n"
        summary += f"- Wisdom: {wis_score}\n"
        summary += f"- Charisma: {cha_score}\n\n"
        summary += f"HP: {current_hp}/{max_hp}\n"
        summary += f"Armor Class: {ac}\n\n"

        if weapons:
            summary += f"Weapons: {', '.join(weapons)}\n"

        if equipment:
            summary += f"Equipment: {', '.join(equipment)}\n"

        summary += f"Gold: {gold} gp\n"

        return summary

    def apply_default_alignment(self, alignment):
        """Apply default alignment as a fallback"""
        print(f"Applying default alignment: {alignment}")

        # Get the character ID (default to player1)
        character_id = next(iter(self.game_state.get('characters', {})), "player1")

        # Make sure we have a character
        if 'characters' not in self.game_state or character_id not in self.game_state['characters']:
            if 'characters' not in self.game_state:
                self.game_state['characters'] = {}

            # Create a basic character if none exists
            self.game_state['characters'][character_id] = {
                "name": "",
                "race": "Human",
                "class": "Fighter",
                "level": 1,
                "alignment": "",
                "abilities": {
                    "strength": 10,
                    "dexterity": 10,
                    "constitution": 10,
                    "intelligence": 10,
                    "wisdom": 10,
                    "charisma": 10
                },
                "hp": {
                    "current": 10,
                    "maximum": 10
                },
                "armor_class": 10,
                "weapons": [],
                "equipment": [],
                "gold": 0,
                "experience_points": 0,
                "next_level_xp": 0
            }

        # Apply the alignment
        self.game_state['characters'][character_id]['alignment'] = alignment

        # Generate explanation based on alignment
        if alignment.lower() == "lawful good":
            explanation = "You've chosen Lawful Good alignment. Lawful Good characters believe in honor, duty, and a structured society that protects the innocent. They follow rules, keep their word, and work to bring about a society in which all live in harmony."
        elif alignment.lower() == "neutral good":
            explanation = "You've chosen Neutral Good alignment. Neutral Good characters believe in doing good without particular regard for or against order. They do what is good without bias for or against order."
        elif alignment.lower() == "chaotic good":
            explanation = "You've chosen Chaotic Good alignment. Chaotic Good characters act as their conscience directs, with little regard for what others expect. They value freedom, creativity, and individualism above all."
        elif alignment.lower() == "lawful neutral":
            explanation = "You've chosen Lawful Neutral alignment. Lawful Neutral characters act in accordance with law, tradition, or personal codes. Order and organization are paramount to them."
        elif alignment.lower() == "true neutral":
            explanation = "You've chosen True Neutral alignment. True Neutral characters do what seems to be a good idea at the time. They don't feel strongly toward any alignment, or they believe in the balance between all alignments."
        elif alignment.lower() == "chaotic neutral":
            explanation = "You've chosen Chaotic Neutral alignment. Chaotic Neutral characters follow their whims, valuing their freedom above all else. They are individualists first and last."
        elif alignment.lower() == "lawful evil":
            explanation = "You've chosen Lawful Evil alignment. Lawful Evil characters methodically take what they want within the limits of their code of conduct, respecting tradition, loyalty, or order but not caring about whom they hurt."
        elif alignment.lower() == "neutral evil":
            explanation = "You've chosen Neutral Evil alignment. Neutral Evil characters do whatever they can get away with, without compassion or qualms. They are out for themselves, pure and simple."
        elif alignment.lower() == "chaotic evil":
            explanation = "You've chosen Chaotic Evil alignment. Chaotic Evil characters act with arbitrary violence, spurred by their greed, hatred, or bloodlust. They take what they want and destroy as they please."
        else:
            explanation = f"You've chosen {alignment} alignment. This will guide how your character behaves in the world."

        # Add the explanation to DM messages
        self.conversation_history.append(f"DM: {explanation}")
        print(f"\nDM: {explanation}")

        # Add to DM messages for web UI
        if 'dm_messages' in self.game_state:
            self.game_state['dm_messages'].append(explanation)

        # Now ask for character name
        name_prompt = "Finally, let's give your character a name. What would you like to name your character?"
        self.conversation_history.append(f"DM: {name_prompt}")
        print(f"\nDM: {name_prompt}")

        # Add to DM messages for web UI
        if 'dm_messages' in self.game_state:
            self.game_state['dm_messages'].append(name_prompt)

        return name_prompt

    def apply_default_class(self, character_class):
        """Apply default class features as a fallback"""
        print(f"Applying default class features for: {character_class}")

        # Get the character ID (default to player1)
        character_id = next(iter(self.game_state.get('characters', {})), "player1")

        # Make sure we have a character
        if 'characters' not in self.game_state or character_id not in self.game_state['characters']:
            if 'characters' not in self.game_state:
                self.game_state['characters'] = {}

            # Create a basic character if none exists
            self.game_state['characters'][character_id] = {
                "name": "",
                "race": "Human",
                "class": "",
                "level": 1,
                "alignment": "",
                "abilities": {
                    "strength": 10,
                    "dexterity": 10,
                    "constitution": 10,
                    "intelligence": 10,
                    "wisdom": 10,
                    "charisma": 10
                },
                "hp": {
                    "current": 10,
                    "maximum": 10
                },
                "armor_class": 10,
                "weapons": [],
                "equipment": [],
                "gold": 0,
                "experience_points": 0,
                "next_level_xp": 0
            }

        # Apply the class
        self.game_state['characters'][character_id]['class'] = character_class

        # Update next_level_xp based on class
        self.game_state['characters'][character_id]['next_level_xp'] = self.get_next_level_xp(character_class, 1)

        # Try to get class documentation from rulebooks
        class_docs = None
        try:
            if self.rulebooks_available:
                class_docs = self.get_class_documentation(character_class)
        except Exception as e:
            print(f"Error getting class documentation: {str(e)}")

        # Apply class-specific features
        class_name = character_class.lower()

        if class_name == "fighter":
            explanation = f"You've chosen the Fighter class. Fighters are masters of combat, skilled with all weapons and armor. They have high hit points and excel at dealing and absorbing damage."
            class_features = {
                "fighting_style": "One-handed weapons",
                "second_wind": "Once per rest, regain 1d10 + level HP",
                "weapon_specialization": "Gain +1 to hit and +2 to damage with chosen weapon type",
                "multiple_attacks": "At higher levels, fighters can make multiple attacks per round",
                "combat_superiority": "Fighters excel at all aspects of combat and receive bonuses to attack rolls"
            }
            weapons = [{"name": "Longsword", "damage": "1d8"}, {"name": "Shortbow", "damage": "1d6"}]
            hp_max = 10

        elif class_name == "cleric":
            explanation = f"You've chosen the Cleric class. Clerics are divine spellcasters who can heal allies and harm undead. They have good armor proficiency and access to powerful support spells."
            class_features = {
                "turn_undead": "Force undead creatures to flee or be destroyed",
                "divine_magic": "Cast divine spells from the cleric spell list",
                "divine_favor": "Receive special blessings from your deity",
                "healing": "Access to powerful healing spells and abilities",
                "domain_powers": "Special abilities based on your chosen divine domain"
            }
            weapons = [{"name": "Mace", "damage": "1d6"}, {"name": "Sling", "damage": "1d4"}]
            hp_max = 8

        elif class_name == "mage" or class_name == "magic-user":
            explanation = f"You've chosen the Mage class. Mages are arcane spellcasters with access to powerful offensive and utility spells. They have low hit points and armor proficiency but can reshape reality with their magic."
            class_features = {
                "arcane_magic": "Cast arcane spells from the mage spell list",
                "spellbook": "Learn and prepare spells from a spellbook",
                "spell_mastery": "At higher levels, certain spells can be cast without preparation",
                "arcane_recovery": "Recover some spell slots during a short rest",
                "ritual_casting": "Cast certain spells as rituals without using spell slots"
            }
            weapons = [{"name": "Dagger", "damage": "1d4"}, {"name": "Staff", "damage": "1d6"}]
            hp_max = 4

        elif class_name == "thief":
            explanation = f"You've chosen the Thief class. Thieves excel at stealth, trap detection, and picking locks. They can also deal extra damage with sneak attacks."
            class_features = {
                "sneak_attack": "Deal extra damage when attacking from hiding or with advantage",
                "pick_locks": "Open locks without a key",
                "find_traps": "Detect and disarm traps",
                "climb_walls": "Climb vertical surfaces without equipment",
                "read_languages": "Decipher unknown languages and codes",
                "use_magic_items": "Use magic scrolls and items normally restricted to other classes"
            }

            # Add thief abilities with percentages
            thief_abilities = {
                "pick_pockets": {
                    "base_percent": "30%",
                    "adjusted_percent": "30%",
                    "description": "Steal items from a person without being detected"
                },
                "open_locks": {
                    "base_percent": "25%",
                    "adjusted_percent": "25%",
                    "description": "Open locked doors, chests, and other containers without a key"
                },
                "find_traps": {
                    "base_percent": "20%",
                    "adjusted_percent": "20%",
                    "description": "Locate traps before they are triggered"
                },
                "remove_traps": {
                    "base_percent": "20%",
                    "adjusted_percent": "20%",
                    "description": "Safely disarm detected traps"
                },
                "move_silently": {
                    "base_percent": "15%",
                    "adjusted_percent": "15%",
                    "description": "Move without making sound, allowing for stealth"
                },
                "hide_in_shadows": {
                    "base_percent": "10%",
                    "adjusted_percent": "10%",
                    "description": "Conceal yourself in areas of shadow or darkness"
                },
                "hear_noise": {
                    "base_percent": "10%",
                    "adjusted_percent": "10%",
                    "description": "Detect faint or distant sounds"
                },
                "climb_walls": {
                    "base_percent": "85%",
                    "adjusted_percent": "85%",
                    "description": "Scale vertical surfaces without equipment"
                },
                "read_languages": {
                    "base_percent": "0%",
                    "adjusted_percent": "0%",
                    "description": "Decipher unknown languages and codes"
                },
                "backstab": {
                    "base_percent": "x2 damage",
                    "adjusted_percent": "x2 damage",
                    "description": "Deal extra damage when attacking from hiding or with advantage"
                }
            }

            # Apply racial adjustments if race is set
            character_id = next(iter(self.game_state.get('characters', {})), "player1")
            if 'characters' in self.game_state and character_id in self.game_state['characters'] and 'race' in self.game_state['characters'][character_id]:
                race = self.game_state['characters'][character_id]['race'].lower()

                # Apply racial adjustments
                if race == "halfling":
                    # Halfling racial adjustments
                    thief_abilities["pick_pockets"]["adjusted_percent"] = "35%" # +5%
                    thief_abilities["open_locks"]["adjusted_percent"] = "30%" # +5%
                    thief_abilities["find_traps"]["adjusted_percent"] = "25%" # +5%
                    thief_abilities["remove_traps"]["adjusted_percent"] = "25%" # +5%
                    thief_abilities["move_silently"]["adjusted_percent"] = "25%" # +10%
                    thief_abilities["hide_in_shadows"]["adjusted_percent"] = "25%" # +15%
                    thief_abilities["hear_noise"]["adjusted_percent"] = "15%" # +5%
                    thief_abilities["climb_walls"]["adjusted_percent"] = "70%" # -15%
                    thief_abilities["read_languages"]["adjusted_percent"] = "-5%" # -5%
                elif race == "dwarf":
                    # Dwarf racial adjustments
                    thief_abilities["pick_pockets"]["adjusted_percent"] = "15%" # -15%
                    thief_abilities["open_locks"]["adjusted_percent"] = "35%" # +10%
                    thief_abilities["find_traps"]["adjusted_percent"] = "35%" # +15%
                    thief_abilities["remove_traps"]["adjusted_percent"] = "35%" # +15%
                    thief_abilities["climb_walls"]["adjusted_percent"] = "75%" # -10%
                    thief_abilities["read_languages"]["adjusted_percent"] = "-5%" # -5%
                elif race == "elf":
                    # Elf racial adjustments
                    thief_abilities["pick_pockets"]["adjusted_percent"] = "35%" # +5%
                    thief_abilities["open_locks"]["adjusted_percent"] = "20%" # -5%
                    thief_abilities["move_silently"]["adjusted_percent"] = "20%" # +5%
                    thief_abilities["hide_in_shadows"]["adjusted_percent"] = "20%" # +10%
                    thief_abilities["hear_noise"]["adjusted_percent"] = "15%" # +5%
                elif race == "gnome":
                    # Gnome racial adjustments
                    thief_abilities["pick_pockets"]["adjusted_percent"] = "15%" # -15%
                    thief_abilities["open_locks"]["adjusted_percent"] = "30%" # +5%
                    thief_abilities["find_traps"]["adjusted_percent"] = "30%" # +10%
                    thief_abilities["remove_traps"]["adjusted_percent"] = "30%" # +10%
                    thief_abilities["move_silently"]["adjusted_percent"] = "20%" # +5%
                    thief_abilities["hide_in_shadows"]["adjusted_percent"] = "15%" # +5%
                    thief_abilities["hear_noise"]["adjusted_percent"] = "20%" # +10%
                    thief_abilities["climb_walls"]["adjusted_percent"] = "70%" # -15%
                elif race == "half-elf":
                    # Half-Elf racial adjustments
                    thief_abilities["move_silently"]["adjusted_percent"] = "20%" # +5%
                    thief_abilities["hide_in_shadows"]["adjusted_percent"] = "15%" # +5%
                    thief_abilities["hear_noise"]["adjusted_percent"] = "15%" # +5%
                elif race == "half-orc":
                    # Half-Orc racial adjustments
                    thief_abilities["pick_pockets"]["adjusted_percent"] = "35%" # +5%
                    thief_abilities["open_locks"]["adjusted_percent"] = "30%" # +5%
                    thief_abilities["find_traps"]["adjusted_percent"] = "25%" # +5%
                    thief_abilities["remove_traps"]["adjusted_percent"] = "25%" # +5%
                    thief_abilities["hear_noise"]["adjusted_percent"] = "15%" # +5%
                    thief_abilities["read_languages"]["adjusted_percent"] = "-10%" # -10%

                # Apply dexterity adjustments if available
                if 'abilities' in self.game_state['characters'][character_id] and 'dexterity' in self.game_state['characters'][character_id]['abilities']:
                    dex = self.game_state['characters'][character_id]['abilities']['dexterity']

                    # Apply dexterity adjustments based on the table
                    dex_mod = {}
                    if dex == 9:
                        dex_mod = {"pick_pockets": -15, "open_locks": -10, "find_traps": -10, "remove_traps": -10, "move_silently": -20, "hide_in_shadows": -10}
                    elif dex == 10:
                        dex_mod = {"pick_pockets": -10, "open_locks": -5, "find_traps": -10, "remove_traps": -10, "move_silently": -15, "hide_in_shadows": -5}
                    elif dex == 11:
                        dex_mod = {"pick_pockets": -5, "open_locks": 0, "find_traps": -5, "remove_traps": -5, "move_silently": -10, "hide_in_shadows": 0}
                    elif dex == 12:
                        dex_mod = {"pick_pockets": 0, "open_locks": 0, "find_traps": 0, "remove_traps": 0, "move_silently": -5, "hide_in_shadows": 0}
                    elif dex == 16:
                        dex_mod = {"pick_pockets": 5, "open_locks": 5, "find_traps": 0, "remove_traps": 0, "move_silently": 5, "hide_in_shadows": 5}
                    elif dex == 17:
                        dex_mod = {"pick_pockets": 10, "open_locks": 10, "find_traps": 5, "remove_traps": 5, "move_silently": 10, "hide_in_shadows": 10}
                    elif dex == 18:
                        dex_mod = {"pick_pockets": 15, "open_locks": 15, "find_traps": 10, "remove_traps": 10, "move_silently": 15, "hide_in_shadows": 15}
                    elif dex == 19:
                        dex_mod = {"pick_pockets": 20, "open_locks": 20, "find_traps": 15, "remove_traps": 15, "move_silently": 20, "hide_in_shadows": 20}

                    # Apply the modifiers
                    for ability, mod in dex_mod.items():
                        if ability in thief_abilities:
                            current = thief_abilities[ability]["adjusted_percent"]
                            if current.endswith("%"):
                                current_value = int(current[:-1])
                                thief_abilities[ability]["adjusted_percent"] = f"{current_value + mod}%"

            weapons = [{"name": "Short Sword", "damage": "1d6"}, {"name": "Shortbow", "damage": "1d6"}]
            hp_max = 6

            # Add thief abilities to character
            self.game_state['characters'][character_id]['thief_abilities'] = thief_abilities

        elif class_name == "paladin":
            explanation = f"You've chosen the Paladin class. Paladins are holy warriors who combine fighting prowess with divine magic. They are bound by a strict code of conduct and serve as champions of justice and good."
            class_features = {
                "divine_sense": "Detect the presence of evil",
                "lay_on_hands": "Heal wounds with a touch",
                "divine_smite": "Channel divine energy into weapon strikes",
                "aura_of_protection": "Grant bonuses to saving throws to nearby allies",
                "cleansing_touch": "Remove harmful spells and effects"
            }
            weapons = [{"name": "Longsword", "damage": "1d8"}, {"name": "Shield", "damage": "0"}]
            hp_max = 10

        elif class_name == "ranger":
            explanation = f"You've chosen the Ranger class. Rangers are skilled hunters and trackers who combine martial prowess with nature magic. They excel in wilderness environments and are deadly foes against their favored enemies."
            class_features = {
                "favored_enemy": "Gain bonuses against specific types of creatures",
                "natural_explorer": "Navigate and survive in the wilderness with ease",
                "primeval_awareness": "Sense the presence of certain creature types",
                "hunters_mark": "Deal extra damage to a marked target",
                "camouflage": "Hide in natural environments with exceptional skill"
            }
            weapons = [{"name": "Longbow", "damage": "1d8"}, {"name": "Short Sword", "damage": "1d6"}]
            hp_max = 8

        else:
            explanation = f"You've chosen the {character_class} class. This class has standard features and abilities."
            class_features = {}
            weapons = [{"name": "Dagger", "damage": "1d4"}]
            hp_max = 8

        # If we have class documentation, try to extract more detailed features
        if class_docs:
            # Look for ability descriptions in the documentation
            for feature_name in list(class_features.keys()):
                # Convert feature name to search terms
                search_term = feature_name.replace('_', ' ')

                # Look for the feature in the documentation
                if search_term.lower() in class_docs.lower():
                    # Find the relevant section
                    start_idx = class_docs.lower().find(search_term.lower())
                    if start_idx != -1:
                        # Extract a reasonable chunk of text
                        end_idx = class_docs.find('\n\n', start_idx)
                        if end_idx == -1:
                            end_idx = min(start_idx + 300, len(class_docs))

                        # Extract the description
                        feature_text = class_docs[start_idx:end_idx].strip()

                        # Update the feature description if we found something substantial
                        if len(feature_text) > len(search_term) + 10:
                            class_features[feature_name] = feature_text

        # Update the character with class features
        self.game_state['characters'][character_id]['class_features'] = class_features
        self.game_state['characters'][character_id]['weapons'] = weapons
        self.game_state['characters'][character_id]['hp']['maximum'] = hp_max
        self.game_state['characters'][character_id]['hp']['current'] = hp_max

        # Add racial traits if race is set
        if 'race' in self.game_state['characters'][character_id] and self.game_state['characters'][character_id]['race']:
            race = self.game_state['characters'][character_id]['race']

            # Try to get race documentation from rulebooks
            race_docs = None
            try:
                if self.rulebooks_available:
                    race_docs = self.get_race_documentation(race)
            except Exception as e:
                print(f"Error getting race documentation: {str(e)}")

            # Apply race-specific traits
            race_name = race.lower()
            racial_traits = {}

            if race_name == "human":
                racial_traits = {
                    "versatile": "Humans can excel in any class and profession",
                    "adaptable": "Humans receive a +1 bonus to all ability scores",
                    "skilled": "Humans gain proficiency in one additional skill of their choice",
                    "ambitious": "Humans gain experience points 10% faster than other races"
                }
            elif race_name == "elf":
                racial_traits = {
                    "keen_senses": "Elves have advantage on Perception checks involving sight or hearing",
                    "fey_ancestry": "Elves are immune to sleep magic and have advantage on saves against charm effects",
                    "trance": "Elves don't need to sleep, instead they meditate for 4 hours per day",
                    "darkvision": "Elves can see in dim light within 60 feet as if it were bright light",
                    "natural_archer": "Elves gain +1 to attack rolls with bows"
                }
            elif race_name == "dwarf":
                racial_traits = {
                    "darkvision": "Dwarves can see in dim light within 60 feet as if it were bright light",
                    "dwarven_resilience": "Dwarves have advantage on saving throws against poison and resistance to poison damage",
                    "stonecunning": "Dwarves add double their proficiency bonus on History checks related to stonework",
                    "dwarven_toughness": "Dwarves gain +2 hit points per level",
                    "dwarven_combat_training": "Dwarves are proficient with battleaxes, handaxes, throwing hammers, and warhammers"
                }
            elif race_name == "halfling":
                racial_traits = {
                    "lucky": "Halflings can reroll any 1 on an attack roll, ability check, or saving throw",
                    "brave": "Halflings have advantage on saving throws against fear",
                    "halfling_nimbleness": "Halflings can move through the space of any creature that is of a size larger than them",
                    "naturally_stealthy": "Halflings can attempt to hide even when only obscured by a creature one size larger than them"
                }
            elif race_name == "half-elf":
                racial_traits = {
                    "fey_ancestry": "Half-elves have advantage on saving throws against being charmed, and magic can't put them to sleep",
                    "skill_versatility": "Half-elves gain proficiency in two skills of their choice",
                    "darkvision": "Half-elves can see in dim light within 60 feet as if it were bright light",
                    "dual_heritage": "Half-elves count as both human and elf for any effect related to race"
                }
            elif race_name == "half-orc":
                racial_traits = {
                    "darkvision": "Half-orcs can see in dim light within 60 feet as if it were bright light",
                    "relentless_endurance": "When reduced to 0 hit points, a half-orc can drop to 1 hit point instead once per long rest",
                    "savage_attacks": "Half-orcs add an extra weapon die on critical hits with melee weapons",
                    "intimidating": "Half-orcs have proficiency in the Intimidation skill"
                }
            elif race_name == "gnome":
                racial_traits = {
                    "darkvision": "Gnomes can see in dim light within 60 feet as if it were bright light",
                    "gnome_cunning": "Gnomes have advantage on Intelligence, Wisdom, and Charisma saving throws against magic",
                    "artificers_lore": "Gnomes add double their proficiency bonus on History checks related to magic items or technological devices",
                    "tinker": "Gnomes can create small mechanical devices with specific simple effects"
                }
            else:
                racial_traits = {
                    "standard_traits": f"Standard racial traits for {race}"
                }

            # If we have race documentation, try to extract more detailed traits
            if race_docs:
                # Look for trait descriptions in the documentation
                for trait_name in list(racial_traits.keys()):
                    # Convert trait name to search terms
                    search_term = trait_name.replace('_', ' ')

                    # Look for the trait in the documentation
                    if search_term.lower() in race_docs.lower():
                        # Find the relevant section
                        start_idx = race_docs.lower().find(search_term.lower())
                        if start_idx != -1:
                            # Extract a reasonable chunk of text
                            end_idx = race_docs.find('\n\n', start_idx)
                            if end_idx == -1:
                                end_idx = min(start_idx + 300, len(race_docs))

                            # Extract the description
                            trait_text = race_docs[start_idx:end_idx].strip()

                            # Update the trait description if we found something substantial
                            if len(trait_text) > len(search_term) + 10:
                                racial_traits[trait_name] = trait_text

            # Add racial traits to character
            self.game_state['characters'][character_id]['racial_traits'] = racial_traits

        # Add the explanation to DM messages
        self.conversation_history.append(f"DM: {explanation}")
        print(f"\nDM: {explanation}")

        # Add to DM messages for web UI
        if 'dm_messages' in self.game_state:
            self.game_state['dm_messages'].append(explanation)

        # Now ask for alignment selection
        alignment_prompt = "Now that you've chosen your class, let's select your alignment. Choose from: Lawful Good, Neutral Good, Chaotic Good, Lawful Neutral, True Neutral, Chaotic Neutral, Lawful Evil, Neutral Evil, or Chaotic Evil."
        self.conversation_history.append(f"DM: {alignment_prompt}")
        print(f"\nDM: {alignment_prompt}")

        # Add to DM messages for web UI
        if 'dm_messages' in self.game_state:
            self.game_state['dm_messages'].append(alignment_prompt)

        return alignment_prompt

    def validate_race_class_alignment(self, race=None, character_class=None, alignment=None):
        """Validate race, class, and alignment combinations according to AD&D 1st Edition rules"""
        print(f"Validating race: {race}, class: {character_class}, alignment: {alignment}")

        # Get character information
        character_id = next(iter(self.game_state.get('characters', {})), "player1")
        character = self.game_state.get('characters', {}).get(character_id, {})

        # If parameters are not provided, use the character's current values
        if race is None and 'race' in character:
            race = character['race']
        if character_class is None and 'class' in character:
            character_class = character['class']
        if alignment is None and 'alignment' in character:
            alignment = character['alignment']

        # Define race-class restrictions
        race_class_restrictions = {
            'Human': ['Fighter', 'Ranger', 'Paladin', 'Cleric', 'Druid', 'Magic-User', 'Illusionist', 'Thief', 'Assassin', 'Monk', 'Bard'],
            'Elf': ['Fighter', 'Ranger', 'Cleric', 'Magic-User', 'Thief', 'Assassin'],
            'Half-Elf': ['Fighter', 'Ranger', 'Cleric', 'Druid', 'Magic-User', 'Thief', 'Assassin', 'Bard'],
            'Dwarf': ['Fighter', 'Cleric', 'Thief', 'Assassin'],
            'Halfling': ['Fighter', 'Thief'],
            'Gnome': ['Fighter', 'Cleric', 'Thief', 'Assassin', 'Illusionist'],
            'Half-Orc': ['Fighter', 'Cleric', 'Thief', 'Assassin']
        }

        # Define class-alignment restrictions
        class_alignment_restrictions = {
            'Paladin': ['Lawful Good'],
            'Ranger': ['Lawful Good', 'Neutral Good', 'Chaotic Good'],
            'Druid': ['True Neutral'],
            'Monk': ['Lawful Good', 'Lawful Neutral', 'Lawful Evil'],
            'Assassin': ['Lawful Evil', 'Neutral Evil', 'Chaotic Evil'],
            'Bard': ['Neutral Good', 'True Neutral', 'Neutral Evil', 'Lawful Neutral', 'Chaotic Neutral']
        }

        # Check race-class compatibility
        if race and character_class:
            if race not in race_class_restrictions:
                return False, f"Invalid race: {race}. Choose from: Human, Elf, Half-Elf, Dwarf, Halfling, Gnome, Half-Orc."

            if character_class not in race_class_restrictions[race]:
                return False, f"{race} characters cannot be {character_class}s. Available classes for {race}: {', '.join(race_class_restrictions[race])}."

            # Special case for Paladin - Human only
            if character_class == 'Paladin' and race != 'Human':
                return False, f"Only Humans can be Paladins. Please choose a different class for your {race} character."

        # Check class-alignment compatibility
        if character_class and alignment:
            if character_class in class_alignment_restrictions and alignment not in class_alignment_restrictions[character_class]:
                return False, f"{character_class}s must be {' or '.join(class_alignment_restrictions[character_class])}. Please choose a compatible alignment."

        # All checks passed
        return True, "Valid combination"

    def handle_class_selection(self, character_class):
        """Handle class selection during character creation"""
        print(f"Handling class selection: {character_class}")

        try:
            # Get character's race
            character_id = next(iter(self.game_state.get('characters', {})), "player1")
            character_race = ""
            if 'characters' in self.game_state and character_id in self.game_state['characters']:
                character_race = self.game_state['characters'][character_id].get('race', "")

            # Validate race-class combination
            is_valid, message = self.validate_race_class_alignment(race=character_race, character_class=character_class)
            if not is_valid:
                print(f"Invalid race-class combination: {message}")
                return message

            # Get class documentation from rulebooks
            class_docs = self.get_class_documentation(character_class)

            # Get race-class restrictions if not already loaded
            if 'reference_material' not in self.game_state or 'race_class_restrictions' not in self.game_state['reference_material']:
                restrictions_docs = self.get_race_class_restrictions()
            else:
                restrictions_docs = self.game_state['reference_material']['race_class_restrictions']['documentation']

            # Get class-alignment restrictions
            alignment_restrictions = self.get_class_alignment_restrictions()

            # Get the character's race
            character_race = ""
            if 'characters' in self.game_state and character_id in self.game_state['characters']:
                character_race = self.game_state['characters'][character_id].get('race', "")

            # Create a CMA request for class selection
            cma_request = {
                "request_id": f"class_selection_{uuid.uuid4()}",
                "requesting_agent": "DMA",
                "target_agent": "CMA",
                "action_type": "character_creation_step",
                "timestamp": datetime.datetime.now().isoformat(),
                "parameters": {
                    "step": "class_selection",
                    "class": character_class,
                    "character_id": character_id,
                    "character_race": character_race,
                    "class_documentation": class_docs,
                    "race_class_restrictions": restrictions_docs,
                    "class_alignment_restrictions": alignment_restrictions
                }
            }

            # Build CMA prompt
            context = self.get_simplified_context()
            agent_prompt = f"{self.prompts['CMA']}\n\nGAME STATE:\n{json.dumps(context, indent=2)}\n\nREQUEST:\n{json.dumps(cma_request, indent=2)}\n\nIMPORTANT: This is step 3 of character creation - class selection. The player has chosen the {character_class} class. Update the character with class abilities and provide a clear explanation of the class's features and role."

            # Call OpenRouter with the CMA prompt
            print("Requesting class selection processing from CMA...")
            agent_response_data = self.call_openrouter(agent_prompt)

            if agent_response_data and 'choices' in agent_response_data and len(agent_response_data['choices']) > 0:
                agent_response = agent_response_data['choices'][0]['message']['content']
                self.update_token_usage(agent_response_data)

                print(f"Got CMA response: {agent_response[:100]}...")

                # Extract JSON response
                json_response = self.extract_json_from_text(agent_response)

                if json_response:
                    print(f"Extracted JSON response: {json.dumps(json_response, indent=2)[:200]}...")

                    # Update game state with character data
                    self.update_character_state(cma_request, json_response)

                    # Extract the explanation from the CMA response
                    explanation = json_response.get('explanation', '')

                    # Add the CMA's guidance to DM messages
                    if explanation:
                        dm_guidance = explanation
                        self.conversation_history.append(f"DM: {dm_guidance}")
                        print(f"\nDM: {dm_guidance}")

                        # Add to DM messages for web UI
                        if 'dm_messages' in self.game_state:
                            self.game_state['dm_messages'].append(dm_guidance)

                    # Now ask for alignment selection
                    alignment_prompt = "Now that you've chosen your class, let's select your alignment. Choose from: Lawful Good, Neutral Good, Chaotic Good, Lawful Neutral, True Neutral, Chaotic Neutral, Lawful Evil, Neutral Evil, or Chaotic Evil."
                    self.conversation_history.append(f"DM: {alignment_prompt}")
                    print(f"\nDM: {alignment_prompt}")

                    # Add to DM messages for web UI
                    if 'dm_messages' in self.game_state:
                        self.game_state['dm_messages'].append(alignment_prompt)

                    return alignment_prompt
                else:
                    print("Failed to extract JSON from class selection CMA response")

                    # If we couldn't extract JSON, use a fallback
                    return self.apply_default_class(character_class)
            else:
                print("Failed to get valid response from OpenRouter for class selection")

                # If we couldn't get a response, use a fallback
                return self.apply_default_class(character_class)

        except Exception as e:
            print(f"Error in handle_class_selection: {str(e)}")
            import traceback
            traceback.print_exc()

            # If there was an exception, use a fallback
            return self.apply_default_class(character_class)



    def display_combat_stats(self):
        """Display the current stats of all characters in the game"""
        # Display a simple one-line status for player characters
        if self.game_state.get('characters', {}):
            print("=== Characters ===")
            for char_id, char_data in self.game_state.get('characters', {}).items():
                name = char_data.get('name', 'Unknown')
                level = char_data.get('level', 1)
                char_class = char_data.get('class', 'Unknown')
                current_hp = char_data.get('hp', {}).get('current', 0)
                max_hp = char_data.get('hp', {}).get('maximum', 0)
                print(f"[{name} (Level {level} {char_class}) HP: {current_hp}/{max_hp}]", end=" ")
            print()  # Add a newline after characters

        # Display a simple one-line status for each enemy
        enemies = self.game_state.get('environment', {}).get('creatures', [])
        if enemies:
            print("=== Enemies ===")
            for enemy in enemies:
                name = enemy.get('name', 'Unknown')
                current_hp = enemy.get('hp', {}).get('current', 0)
                max_hp = enemy.get('hp', {}).get('maximum', 0)
                print(f"[{name} HP: {current_hp}/{max_hp}]", end=" ")
            print()  # Add a newline after enemies
        else:
            print("[No enemies present]")

        print()  # Add an extra newline at the end

        # Display world information if available
        if 'world' in self.game_state:
            world = self.game_state['world']

            # Display time
            if 'time' in world:
                time = world['time']
                print(f"Time: Day {time.get('day', 1)}, {time.get('hour', 12):02d}:{time.get('minute', 0):02d}", end=" | ")

            # Display weather
            if 'weather' in world:
                weather = world['weather']
                print(f"Weather: {weather.get('condition', 'Clear')}", end=" | ")

            # Display light
            if 'light' in world:
                light = world['light']
                print(f"Light: {light.get('condition', 'Bright')} ({light.get('source', 'Daylight')})", end=" | ")

            # Display resources
            if 'resources' in world:
                resources = world['resources']
                print(f"Food: {resources.get('food', 0)}, Water: {resources.get('water', 0)}, Torches: {resources.get('torches', 0)}")
            else:
                print()  # Add a newline if no resources

        # Display exploration information if available
        if 'exploration' in self.game_state and 'movement' in self.game_state['exploration']:
            movement = self.game_state['exploration']['movement']
            print(f"Movement: {movement.get('rate', 120)} feet/turn ({movement.get('encumbrance', 'Unencumbered')})")

        print()  # Add an extra newline for spacing

    def run(self, web_mode=False):
        """Run the continuous interaction loop"""
        # Set the web_mode flag
        self.web_mode = web_mode

        print("AD&D 1st Edition Test App")
        print("Type 'exit' to quit, 'stats' to see token usage, 'rules:query' to search rulebooks")

        # Check if we're in character creation mode
        if self.mode == 'create_character':
            print("You are in character creation mode.")
            print("Type 'create character' to begin the character creation process.")
            print("Follow the prompts to create your character step by step.")
        else:
            print("Type 'create character' to start character creation")

        print("\nAvailable Agents:")
        print("- DMA: Dungeon Master Agent (main narrative and game flow)")
        print("- CRA: Combat Resolution Agent (handles attacks and damage)")
        print("- CMA: Character Management Agent (handles character stats and abilities)")
        print("- NEA: NPC & Encounter Agent (manages NPCs, monsters, and treasure)")
        print("- EEA: Exploration Engine Agent (handles movement, searching, and obstacles)")
        print("- WEA: World & Environment Agent (manages time, weather, and resources)")
        print("- MSA: Magic System Agent (manages spells, magic items, and magical effects)")
        print("- CaMA: Campaign Manager Agent (handles campaign creation and management)")

        # Describe the initial scene
        initial_context = self.get_simplified_context()
        print("\nDM:", initial_context['environment']['description'])

        if 'creatures' in initial_context['environment'] and len(initial_context['environment']['creatures']) > 0:
            creatures = [c['name'] for c in initial_context['environment']['creatures']]
            print(f"You see: {', '.join(creatures)}")

        # Display initial combat stats
        self.display_combat_stats()

        print()  # Empty line for readability

        # If web mode, return here as the web interface will handle the input loop
        if self.web_mode:
            return

        # If we're in character creation mode, start the process automatically
        if self.mode == 'create_character':
            print("\nStarting character creation process...")
            # Set the current step to introduction
            if 'character_creation' in self.game_state:
                self.game_state['character_creation']['current_step'] = 0
            # Process the create character command
            response = self.process_player_input("create character")
            print("\nDM:", response)
            print()  # Empty line for readability

        while True:
            player_input = input("Player> ")

            if player_input.lower() == 'exit':
                break

            if player_input.lower() == 'stats':
                self.display_token_usage()
                continue

            # Check for rulebook query
            if player_input.lower().startswith('rules:'):
                if hasattr(self, 'rulebooks_available') and self.rulebooks_available:
                    query = player_input[6:].strip()
                    print(f"\nQuerying rulebooks for: {query}")
                    rules = self.rulebook_integration.query_rules(query, max_results=3)
                    print("\nRelevant Rules:")
                    print(rules)
                else:
                    print("\nRulebook system is not available")
                continue

            # Check for character creation command
            if player_input.lower().startswith('create character'):
                print("\nStarting character creation process...")

                # Clear any existing combat or game state that might interfere with character creation
                if 'combat' in self.game_state:
                    del self.game_state['combat']

                # Add debug information
                print("DEBUG: Starting character creation with game state:", json.dumps(self.game_state, indent=2))

                # Add DM message to guide the player
                dm_welcome_message = "Welcome to character creation! I'll guide you through creating your AD&D 1st Edition character step by step."
                self.conversation_history.append(f"DM: {dm_welcome_message}")
                print(f"\nDM: {dm_welcome_message}")

                # Add explanation of the process with better formatting
                dm_explanation = """We'll follow these steps:

1) Roll ability scores
2) Select race
3) Choose class
4) Pick alignment
5) Roll hit points
6) Get equipment
7) Choose spells if applicable
8) Add final details"""
                self.conversation_history.append(f"DM: {dm_explanation}")
                print(f"\nDM: {dm_explanation}")

                # Add to DM messages for web UI
                if 'dm_messages' not in self.game_state:
                    self.game_state['dm_messages'] = []
                self.game_state['dm_messages'].append(dm_welcome_message)
                self.game_state['dm_messages'].append(dm_explanation)

                # Add a message about button options
                button_message = "You'll see clickable options appear below for each choice. Simply click an option to select it, or type your response if you prefer."
                self.conversation_history.append(f"DM: {button_message}")
                print(f"\nDM: {button_message}")
                if 'dm_messages' in self.game_state:
                    self.game_state['dm_messages'].append(button_message)

                # Create a CMA request for character creation
                cma_request = {
                    "request_id": f"character_creation_{uuid.uuid4()}",
                    "requesting_agent": "DMA",
                    "target_agent": "CMA",
                    "action_type": "character_creation",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "parameters": {
                        "method": "standard",  # standard, 3d6, 4d6_drop_lowest
                        "character_id": "new",
                        "workflow": "interactive"  # Indicate we want an interactive workflow
                    }
                }

                # Build CMA prompt with specific instructions for interactive guidance
                context = self.get_simplified_context()
                agent_prompt = f"{self.prompts['CMA']}\n\nGAME STATE:\n{json.dumps(context, indent=2)}\n\nREQUEST:\n{json.dumps(cma_request, indent=2)}\n\nIMPORTANT: This is an interactive character creation process. Guide the player through each step of character creation according to the AD&D 1st Edition rules. Provide clear instructions and options at each step. Start with ability score generation and wait for player input before proceeding to the next step."

                # Call OpenRouter with the CMA prompt
                print("Requesting character creation from CMA...")
                if 'agent_debug' in self.game_state:
                    self.game_state['agent_debug'].append("Requesting character creation from CMA...")

                try:
                    agent_response_data = self.call_openrouter(agent_prompt)
                    print("DEBUG: Received response from OpenRouter")
                except Exception as e:
                    error_message = f"Error calling OpenRouter: {str(e)}"
                    print(f"ERROR: {error_message}")
                    if 'agent_debug' in self.game_state:
                        self.game_state['agent_debug'].append(f"ERROR: {error_message}")
                    if 'dm_messages' in self.game_state:
                        self.game_state['dm_messages'].append(f"There was an error starting character creation. Please try again.")
                    return "There was an error starting character creation. Please try again."

                if agent_response_data and 'choices' in agent_response_data and len(agent_response_data['choices']) > 0:
                    agent_response = agent_response_data['choices'][0]['message']['content']
                    self.update_token_usage(agent_response_data)

                    # Extract JSON response
                    try:
                        json_response = self.extract_json_from_text(agent_response)
                        print("DEBUG: Extracted JSON response:", json.dumps(json_response, indent=2) if json_response else "None")
                    except Exception as e:
                        error_message = f"Error extracting JSON: {str(e)}"
                        print(f"ERROR: {error_message}")
                        if 'agent_debug' in self.game_state:
                            self.game_state['agent_debug'].append(f"ERROR: {error_message}")
                        json_response = None

                    if json_response:
                        # Update game state with character data
                        try:
                            self.update_character_state(cma_request, json_response)
                            print("DEBUG: Updated character state successfully")
                        except Exception as e:
                            error_message = f"Error updating character state: {str(e)}"
                            print(f"ERROR: {error_message}")
                            if 'agent_debug' in self.game_state:
                                self.game_state['agent_debug'].append(f"ERROR: {error_message}")
                            if 'dm_messages' in self.game_state:
                                self.game_state['dm_messages'].append(f"There was an error creating your character. Please try again.")

                        # Extract the explanation from the CMA response
                        explanation = json_response.get('explanation', '')

                        # Add the CMA's guidance to DM messages
                        if explanation:
                            dm_guidance = explanation
                            self.conversation_history.append(f"DM: {dm_guidance}")
                            print(f"\nDM: {dm_guidance}")

                            # Add to DM messages for web UI
                            if 'dm_messages' in self.game_state:
                                self.game_state['dm_messages'].append(dm_guidance)

                        # Get the character ID
                        character_id = next(iter(self.game_state.get('characters', {})), None)
                        if character_id:
                            # Get the character data
                            character = self.game_state['characters'][character_id]

                            # Display character information
                            char_info = f"Character started: {character.get('name', 'Unnamed Character')}"
                            if 'abilities' in character:
                                abilities_str = ", ".join([f"{k.capitalize()}: {v}" for k, v in character.get('abilities', {}).items()])
                                char_info += f"\nAbility Scores: {abilities_str}"

                            print(f"\n{char_info}")
                            if 'agent_debug' in self.game_state:
                                self.game_state['agent_debug'].append(char_info)

                            # Set player1 as the active character
                            self.game_state['player'] = character

                            # Add next steps guidance
                            next_steps = "Please respond to the prompts to continue character creation. For example, you can choose your race, class, and other character details."
                            self.conversation_history.append(f"DM: {next_steps}")
                            print(f"\nDM: {next_steps}")

                            # Add to DM messages for web UI
                            if 'dm_messages' in self.game_state:
                                self.game_state['dm_messages'].append(next_steps)
                        else:
                            # Display error message
                            error_message = "Error: No character ID found after creation. Please try again."
                            self.conversation_history.append(f"DM: {error_message}")
                            print(f"\nDM: {error_message}")

                            # Add to DM messages for web UI
                            if 'dm_messages' in self.game_state:
                                self.game_state['dm_messages'].append(error_message)

                        # Continue the game loop
                        continue
                    else:
                        # Display error message
                        error_message = "Error: Could not parse character creation response. Please try again."
                        self.conversation_history.append(f"DM: {error_message}")
                        print(f"\nDM: {error_message}")

                        # Add to DM messages for web UI
                        if 'dm_messages' in self.game_state:
                            self.game_state['dm_messages'].append(error_message)
                        continue
                else:
                    # Display error message
                    error_message = "Error: Failed to get response from CMA for character creation. Please try again."
                    self.conversation_history.append(f"DM: {error_message}")
                    print(f"\nDM: {error_message}")

                    # Add to DM messages for web UI
                    if 'dm_messages' in self.game_state:
                        self.game_state['dm_messages'].append(error_message)
                    continue

            # Check for character advancement command
            if player_input.lower().startswith('level up'):
                print("\nStarting character advancement process...")

                # Get the character ID (default to player1)
                character_id = "player1"
                if len(player_input) > 8:  # "level up " is 9 chars
                    specified_id = player_input[9:].strip()
                    if specified_id and specified_id in self.game_state.get('characters', {}):
                        character_id = specified_id

                # Check if character exists
                if character_id not in self.game_state.get('characters', {}):
                    # Display error message
                    error_message = f"Error: Character '{character_id}' not found."
                    print(f"\nDM: {error_message}")
                    print()  # Empty line for readability
                    continue

                # Get character data
                character = self.game_state['characters'][character_id]

                # Create a CMA request for character advancement
                cma_request = {
                    "request_id": f"character_advancement_{uuid.uuid4()}",
                    "requesting_agent": "DMA",
                    "target_agent": "CMA",
                    "action_type": "character_advancement",
                    "timestamp": datetime.datetime.now().isoformat(),
                    "parameters": {
                        "character_id": character_id,
                        "current_level": character.get('level', 1),
                        "current_xp": character.get('experience_points', 0),
                        "class": character.get('class', 'Fighter')
                    }
                }

                # Build CMA prompt
                context = self.get_simplified_context()
                agent_prompt = f"{self.prompts['CMA']}\n\nGAME STATE:\n{json.dumps(context, indent=2)}\n\nREQUEST:\n{json.dumps(cma_request, indent=2)}"

                # Call OpenRouter with the CMA prompt
                print(f"Requesting character advancement for {character_id} from CMA...")
                agent_response_data = self.call_openrouter(agent_prompt)

                if agent_response_data and 'choices' in agent_response_data and len(agent_response_data['choices']) > 0:
                    agent_response = agent_response_data['choices'][0]['message']['content']
                    self.update_token_usage(agent_response_data)

                    # Extract JSON response
                    json_response = self.extract_json_from_text(agent_response)

                    if json_response:
                        # Clean up any comments in the JSON response
                        if isinstance(json_response, dict):
                            # Remove any keys that start with // or # (comments)
                            keys_to_remove = [k for k in json_response.keys() if k.startswith('//') or k.startswith('#')]
                            for key in keys_to_remove:
                                json_response.pop(key, None)

                        # Update game state with advanced character
                        self.update_character_state(cma_request, json_response)

                        # Return success message
                        level = json_response.get('level', 'unknown')
                        if isinstance(json_response.get('outcome'), dict):
                            level = json_response.get('outcome', {}).get('level', level)

                        # Add success message to conversation history
                        success_message = f"Character advancement completed successfully! {character.get('name', 'Your character')} is now level {level}."
                        self.conversation_history.append(f"DM: {success_message}")

                        # Display the success message and updated stats
                        print(f"\nDM: {success_message}")
                        self.display_combat_stats()
                        print()  # Empty line for readability

                        # Continue the game loop
                        continue
                    else:
                        # Try to extract just the JSON part without comments
                        try:
                            # Find the first { and the matching }
                            start = agent_response.find('{')
                            if start >= 0:
                                # Find the matching closing brace
                                open_braces = 1
                                for i in range(start + 1, len(agent_response)):
                                    if agent_response[i] == '{':
                                        open_braces += 1
                                    elif agent_response[i] == '}':
                                        open_braces -= 1
                                        if open_braces == 0:
                                            end = i + 1
                                            break

                                if 'end' in locals():
                                    # Extract just the JSON part
                                    json_str = agent_response[start:end]
                                    # Remove any comment lines
                                    json_lines = [line for line in json_str.split('\n') if not line.strip().startswith('//')]
                                    clean_json = '\n'.join(json_lines)

                                    # Try to parse the cleaned JSON
                                    try:
                                        json_response = json.loads(clean_json)

                                        # Update game state with advanced character
                                        self.update_character_state(cma_request, json_response)

                                        # Return success message
                                        level = json_response.get('level', 'unknown')
                                        if isinstance(json_response.get('outcome'), dict):
                                            level = json_response.get('outcome', {}).get('level', level)

                                        # Add success message to conversation history
                                        success_message = f"Character advancement completed successfully! {character.get('name', 'Your character')} is now level {level}."
                                        self.conversation_history.append(f"DM: {success_message}")

                                        # Display the success message and updated stats
                                        print(f"\nDM: {success_message}")
                                        self.display_combat_stats()
                                        print()  # Empty line for readability

                                        # Continue the game loop
                                        continue
                                    except json.JSONDecodeError:
                                        pass
                        except Exception as e:
                            print(f"Error cleaning JSON: {e}")

                        # Display error message
                        error_message = "Error: Could not parse character advancement response."
                        print(f"\nDM: {error_message}")
                        print()  # Empty line for readability
                        continue
                else:
                    # Display error message
                    error_message = "Error: Failed to get response from CMA for character advancement."
                    print(f"\nDM: {error_message}")
                    print()  # Empty line for readability
                    continue

            # Process the player input
            response = self.process_player_input(player_input)
            print("\nDM:", response)
            # Display combat stats after DM's response
            self.display_combat_stats()
            print()  # Empty line for readability

# Run the app if executed directly
if __name__ == "__main__":
    app = SimpleADDTest(mode='create_character')
    app.run()