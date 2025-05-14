import json
import logging
import random
from typing import Dict, Any, List, Optional

# Import the communication manager for real-time updates
from . import communication_manager

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('AgentStateHandlers')

class AgentStateHandlers:
    """
    Handlers for updating game state based on agent responses.
    This class contains methods for updating the game state based on responses from different agents.
    Each method integrates with the communication manager to provide real-time updates to clients.
    """

    @staticmethod
    def update_exploration_state(game_state: Dict[str, Any], agent_request: Dict[str, Any], agent_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the exploration state based on the EEA agent response.

        Args:
            game_state: The current game state
            agent_request: The request sent to the EEA
            agent_response: The response from the EEA

        Returns:
            Updated game state
        """
        logger.info("Updating exploration state")

        # Make sure we have a valid response
        if not agent_response or not isinstance(agent_response, dict):
            logger.warning("Invalid agent response for exploration update")
            return game_state

        # Get the action type
        action_type = agent_response.get('action_type', '')

        # Initialize exploration state if it doesn't exist
        if 'exploration' not in game_state:
            game_state['exploration'] = {
                'movement': {'rate': 120, 'encumbrance': 'Unencumbered'},
                'mapping': {'areas_explored': [], 'areas_mapped': []},
                'search': {'last_area_searched': '', 'found_items': [], 'found_traps': [], 'found_secret_doors': []}
            }
            
            # Notify clients about the new exploration state
            communication_manager.notify_state_change('exploration', 'init', game_state['exploration'])

        # Handle different action types
        if action_type == 'movement':
            # Update movement rate and position
            if 'result' in agent_response and 'rate' in agent_response['result']:
                game_state['exploration']['movement']['rate'] = agent_response['result']['rate']
                # Notify clients about movement rate change
                communication_manager.notify_state_change('exploration', 'movement',
                                                         game_state['exploration']['movement'])

            # Add current location to areas explored if not already there
            current_location = game_state.get('environment', {}).get('location', '')
            if current_location and current_location not in game_state['exploration']['mapping']['areas_explored']:
                game_state['exploration']['mapping']['areas_explored'].append(current_location)
                # Notify clients about new explored area
                communication_manager.notify_state_change('exploration', 'mapping',
                                                         game_state['exploration']['mapping'])

        elif action_type == 'search':
            # Update search results
            if 'result' in agent_response:
                # Record the area being searched
                game_state['exploration']['search']['last_area_searched'] = game_state.get('environment', {}).get('location', '')
                
                # Track if any changes were made to notify clients
                search_updated = False

                # Add any found items
                if 'found_items' in agent_response['result']:
                    for item in agent_response['result']['found_items']:
                        if item not in game_state['exploration']['search']['found_items']:
                            game_state['exploration']['search']['found_items'].append(item)
                            search_updated = True

                # Add any found traps
                if 'found_traps' in agent_response['result']:
                    for trap in agent_response['result']['found_traps']:
                        if trap not in game_state['exploration']['search']['found_traps']:
                            game_state['exploration']['search']['found_traps'].append(trap)
                            search_updated = True

                # Add any found secret doors
                if 'found_secret_doors' in agent_response['result']:
                    for door in agent_response['result']['found_secret_doors']:
                        if door not in game_state['exploration']['search']['found_secret_doors']:
                            game_state['exploration']['search']['found_secret_doors'].append(door)
                            search_updated = True
                
                # Notify clients if search results were updated
                if search_updated:
                    communication_manager.notify_state_change('exploration', 'search',
                                                             game_state['exploration']['search'])

        elif action_type == 'obstacle':
            # Handle obstacle interaction (doors, locks, climbing)
            if 'result' in agent_response and 'obstacle' in agent_response['result']:
                # Implement obstacle interaction logic here
                # For now, just notify about the obstacle interaction
                communication_manager.notify_state_change('exploration', 'obstacle',
                                                         agent_response['result'])

        elif action_type == 'wilderness':
            # Handle wilderness travel
            if 'result' in agent_response and 'wilderness' in agent_response['result']:
                # Implement wilderness travel logic here
                # For now, just notify about the wilderness travel
                communication_manager.notify_state_change('exploration', 'wilderness',
                                                         agent_response['result'])

        # Broadcast the complete updated exploration state
        communication_manager.update_game_state({"exploration": game_state['exploration']},
                                              "exploration_state_update")
        
        return game_state

    @staticmethod
    def update_world_state(game_state: Dict[str, Any], agent_request: Dict[str, Any], agent_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the world state based on the WEA agent response.

        Args:
            game_state: The current game state
            agent_request: The request sent to the WEA
            agent_response: The response from the WEA

        Returns:
            Updated game state
        """
        logger.info("Updating world state")

        # Make sure we have a valid response
        if not agent_response or not isinstance(agent_response, dict):
            logger.warning("Invalid agent response for world update")
            return game_state

        # Get the action type
        action_type = agent_response.get('action_type', '')

        # Initialize world state if it doesn't exist
        if 'world' not in game_state:
            game_state['world'] = {
                'time': {'round': 0, 'turn': 0, 'day': 1, 'hour': 12, 'minute': 0},
                'weather': {'condition': 'Clear', 'temperature': 'Mild', 'wind': 'Light'},
                'light': {'condition': 'Bright', 'source': 'Daylight', 'duration_remaining': 0},
                'resources': {'food': 5, 'water': 1, 'torches': 3, 'oil': 0}
            }
            
            # Notify clients about the new world state
            communication_manager.notify_state_change('world', 'init', game_state['world'])

        # Handle different action types
        if action_type == 'time':
            # Update time tracking
            if 'result' in agent_response and 'time' in agent_response['result']:
                time_update = agent_response['result']['time']
                time_changed = False

                # Update rounds
                if 'round' in time_update:
                    game_state['world']['time']['round'] = time_update['round']
                    time_changed = True

                # Update turns
                if 'turn' in time_update:
                    game_state['world']['time']['turn'] = time_update['turn']
                    time_changed = True

                # Update days
                if 'day' in time_update:
                    game_state['world']['time']['day'] = time_update['day']
                    time_changed = True

                # Update hours
                if 'hour' in time_update:
                    game_state['world']['time']['hour'] = time_update['hour']
                    time_changed = True

                # Update minutes
                if 'minute' in time_update:
                    game_state['world']['time']['minute'] = time_update['minute']
                    time_changed = True
                
                # Notify clients if time was updated
                if time_changed:
                    communication_manager.notify_state_change('world', 'time',
                                                             game_state['world']['time'])

        elif action_type == 'weather':
            # Update weather conditions
            if 'result' in agent_response and 'weather' in agent_response['result']:
                weather_update = agent_response['result']['weather']
                weather_changed = False

                # Update condition
                if 'condition' in weather_update:
                    game_state['world']['weather']['condition'] = weather_update['condition']
                    weather_changed = True

                # Update temperature
                if 'temperature' in weather_update:
                    game_state['world']['weather']['temperature'] = weather_update['temperature']
                    weather_changed = True

                # Update wind
                if 'wind' in weather_update:
                    game_state['world']['weather']['wind'] = weather_update['wind']
                    weather_changed = True
                
                # Notify clients if weather was updated
                if weather_changed:
                    communication_manager.notify_state_change('world', 'weather',
                                                             game_state['world']['weather'])

        elif action_type == 'light':
            # Update light conditions
            if 'result' in agent_response and 'light' in agent_response['result']:
                light_update = agent_response['result']['light']
                light_changed = False

                # Update condition
                if 'condition' in light_update:
                    game_state['world']['light']['condition'] = light_update['condition']
                    light_changed = True

                # Update source
                if 'source' in light_update:
                    game_state['world']['light']['source'] = light_update['source']
                    light_changed = True

                # Update duration
                if 'duration_remaining' in light_update:
                    game_state['world']['light']['duration_remaining'] = light_update['duration_remaining']
                    light_changed = True
                
                # Notify clients if light was updated
                if light_changed:
                    communication_manager.notify_state_change('world', 'light',
                                                             game_state['world']['light'])

        elif action_type == 'resources':
            # Update resource tracking
            if 'result' in agent_response and 'resources' in agent_response['result']:
                resources_update = agent_response['result']['resources']
                resources_changed = False

                # Update food
                if 'food' in resources_update:
                    game_state['world']['resources']['food'] = resources_update['food']
                    resources_changed = True

                # Update water
                if 'water' in resources_update:
                    game_state['world']['resources']['water'] = resources_update['water']
                    resources_changed = True

                # Update torches
                if 'torches' in resources_update:
                    game_state['world']['resources']['torches'] = resources_update['torches']
                    resources_changed = True

                # Update oil
                if 'oil' in resources_update:
                    game_state['world']['resources']['oil'] = resources_update['oil']
                    resources_changed = True
                
                # Notify clients if resources were updated
                if resources_changed:
                    communication_manager.notify_state_change('world', 'resources',
                                                             game_state['world']['resources'])

        # Broadcast the complete updated world state
        communication_manager.update_game_state({"world": game_state['world']},
                                              "world_state_update")
        
        return game_state

    @staticmethod
    def update_npc_state(game_state: Dict[str, Any], agent_request: Dict[str, Any], agent_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the NPC state based on the NEA agent response.

        Args:
            game_state: The current game state
            agent_request: The request sent to the NEA
            agent_response: The response from the NEA

        Returns:
            Updated game state
        """
        logger.info("Updating NPC state")

        # Make sure we have a valid response
        if not agent_response or not isinstance(agent_response, dict):
            logger.warning("Invalid agent response for NPC update")
            return game_state

        # Get the action type
        action_type = agent_response.get('action_type', '')

        # Initialize NPC list if it doesn't exist
        if 'environment' not in game_state:
            game_state['environment'] = {'location': '', 'description': '', 'creatures': [], 'npcs': []}
            # Notify clients about the new environment
            communication_manager.notify_state_change('environment', 'init', game_state['environment'])
        elif 'npcs' not in game_state['environment']:
            game_state['environment']['npcs'] = []
            # Notify clients about the new NPCs list
            communication_manager.notify_state_change('environment', 'npcs', [])

        # Handle different action types
        if action_type == 'npc_reaction':
            # Update NPC reactions
            if 'result' in agent_response and 'npc_id' in agent_response['result']:
                npc_id = agent_response['result']['npc_id']
                reaction = agent_response['result'].get('reaction', 'Neutral')

                # Find the NPC and update its reaction
                for i, npc in enumerate(game_state['environment']['npcs']):
                    if npc.get('id') == npc_id:
                        game_state['environment']['npcs'][i]['reaction'] = reaction
                        
                        # Notify clients about the NPC reaction change
                        communication_manager.notify_state_change('npc', npc_id, {
                            'action': 'reaction_change',
                            'reaction': reaction,
                            'npc': game_state['environment']['npcs'][i]
                        })
                        break

        elif action_type == 'monster_tactics':
            # Update monster tactics
            pass

        elif action_type == 'dialogue':
            # Update NPC dialogue
            if 'result' in agent_response and 'npc_id' in agent_response['result']:
                npc_id = agent_response['result']['npc_id']
                dialogue = agent_response['result'].get('dialogue', '')

                # Find the NPC and update its dialogue
                for i, npc in enumerate(game_state['environment']['npcs']):
                    if npc.get('id') == npc_id:
                        if 'dialogue_history' not in game_state['environment']['npcs'][i]:
                            game_state['environment']['npcs'][i]['dialogue_history'] = []

                        game_state['environment']['npcs'][i]['dialogue_history'].append(dialogue)
                        
                        # Notify clients about the new dialogue
                        communication_manager.notify_state_change('npc', npc_id, {
                            'action': 'dialogue',
                            'dialogue': dialogue,
                            'npc': game_state['environment']['npcs'][i]
                        })
                        break

        elif action_type == 'morale':
            # Update creature morale
            if 'result' in agent_response and 'creature_id' in agent_response['result']:
                creature_id = agent_response['result']['creature_id']
                morale_result = agent_response['result'].get('morale_result', 'Stands')

                # Find the creature and update its morale
                for i, creature in enumerate(game_state['environment']['creatures']):
                    if creature.get('id') == creature_id:
                        game_state['environment']['creatures'][i]['morale'] = morale_result
                        
                        # Notify clients about the morale change
                        communication_manager.notify_state_change('creature', creature_id, {
                            'action': 'morale_change',
                            'morale': morale_result,
                            'creature': game_state['environment']['creatures'][i]
                        })
                        break

        elif action_type == 'treasure':
            # Add treasure to the environment
            if 'result' in agent_response and 'treasure' in agent_response['result']:
                treasure = agent_response['result']['treasure']

                # Add treasure to the environment
                if 'treasure' not in game_state['environment']:
                    game_state['environment']['treasure'] = []

                game_state['environment']['treasure'].append(treasure)
                
                # Notify clients about the new treasure
                communication_manager.notify_state_change('environment', 'treasure', {
                    'action': 'treasure_added',
                    'treasure': treasure
                })

        # Broadcast the complete updated environment state
        communication_manager.update_game_state({"environment": game_state['environment']},
                                              "environment_state_update")
        
        return game_state

    @staticmethod
    def update_character_state(game_state: Dict[str, Any], agent_request: Dict[str, Any], agent_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the character state based on the CMA agent response.

        Args:
            game_state: The current game state
            agent_request: The request sent to the CMA
            agent_response: The response from the CMA

        Returns:
            Updated game state
        """
        logger.info("Updating character state")

        # Make sure we have a valid response
        if not agent_response or not isinstance(agent_response, dict):
            logger.warning("Invalid agent response for character update")
            return game_state

        # Get the action type
        action_type = agent_response.get('action_type', '')

        # Initialize characters dictionary if it doesn't exist
        if 'characters' not in game_state:
            game_state['characters'] = {}
            # Notify clients about the new characters container
            communication_manager.notify_state_change('characters', 'init', {})

        # Handle different action types
        if action_type == 'character_creation':
            # Handle character creation
            updated_state = AgentStateHandlers.handle_character_creation(game_state, agent_request, agent_response)
            # We'll add notification in the handle_character_creation method
            return updated_state

        elif action_type == 'character_advancement':
            # Handle character advancement
            updated_state = AgentStateHandlers.handle_character_advancement(game_state, agent_request, agent_response)
            # We'll add notification in the handle_character_advancement method
            return updated_state

        elif action_type == 'ability_check' or action_type == 'save':
            # Handle ability checks and saving throws
            character_id = agent_response.get('character_id')
            if not character_id or character_id not in game_state['characters']:
                logger.warning(f"Character {character_id} not found for ability check/save")
                return game_state

            # Record the check result in character history if it exists
            if 'history' not in game_state['characters'][character_id]:
                game_state['characters'][character_id]['history'] = []

            # Add the check result to history
            check_entry = {
                'type': action_type,
                'timestamp': agent_request.get('timestamp', 'unknown'),
                'rolls': agent_response.get('rolls', []),
                'outcome': agent_response.get('outcome', 'unknown'),
                'explanation': agent_response.get('explanation', '')
            }

            game_state['characters'][character_id]['history'].append(check_entry)
            
            # Notify clients about the ability check or save
            communication_manager.notify_state_change('character', character_id, {
                'action': action_type,
                'result': check_entry
            })

        # Broadcast the complete updated character state
        if 'characters' in game_state and game_state['characters']:
            communication_manager.update_game_state({"characters": game_state['characters']},
                                                  "character_state_update")

        return game_state

    @staticmethod
    def handle_character_creation(game_state: Dict[str, Any], agent_request: Dict[str, Any], agent_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle character creation from CMA response.

        Args:
            game_state: The current game state
            agent_request: The request sent to the CMA
            agent_response: The response from the CMA

        Returns:
            Updated game state with new character
        """
        logger.info("Handling character creation")

        try:
            # Log the input data for debugging
            logger.info(f"Character creation request: {json.dumps(agent_request, indent=2)}")
            logger.info(f"Character creation response: {json.dumps(agent_response, indent=2)}")

            # Check if we have character data in the outcome
            if 'outcome' not in agent_response:
                logger.warning("No 'outcome' field found in CMA response")
                # Try to find character data directly in the response
                if isinstance(agent_response, dict) and 'name' in agent_response:
                    logger.info("Using top-level response as character data")
                    character_data = agent_response
                else:
                    logger.warning("No usable character data found in CMA response")
                    return game_state
            elif not isinstance(agent_response['outcome'], dict):
                logger.warning(f"'outcome' is not a dictionary: {type(agent_response['outcome'])}")
                return game_state
            else:
                # Get the character data from outcome
                character_data = agent_response['outcome']

            # Ensure we have a valid character data dictionary
            if not isinstance(character_data, dict):
                logger.warning(f"Character data is not a dictionary: {type(character_data)}")
                return game_state

            # Initialize characters dictionary if it doesn't exist
            if 'characters' not in game_state:
                logger.info("Initializing characters dictionary in game state")
                game_state['characters'] = {}

            # Generate a character ID if not provided
            character_id = agent_response.get('character_id', 'new')
            if character_id == 'new':
                # Generate a unique ID
                character_id = f"player{len(game_state['characters']) + 1}"

            logger.info(f"Using character ID: {character_id}")

            # Add creation timestamp
            character_data['created_at'] = agent_request.get('timestamp', 'unknown')

            # Initialize history
            character_data['history'] = [{
                'type': 'creation',
                'timestamp': agent_request.get('timestamp', 'unknown'),
                'explanation': agent_response.get('explanation', 'Character created')
            }]

            # Ensure required fields exist
            if 'name' not in character_data:
                character_data['name'] = "Unnamed Character"

            if 'class' not in character_data:
                character_data['class'] = "Fighter"

            if 'level' not in character_data:
                character_data['level'] = 1

            if 'hp' not in character_data:
                character_data['hp'] = {'current': 10, 'maximum': 10}
            elif not isinstance(character_data['hp'], dict):
                character_data['hp'] = {'current': character_data['hp'], 'maximum': character_data['hp']}

            if 'abilities' not in character_data:
                character_data['abilities'] = {
                    'strength': 10,
                    'dexterity': 10,
                    'constitution': 10,
                    'intelligence': 10,
                    'wisdom': 10,
                    'charisma': 10
                }

            # Add the character to the game state
            game_state['characters'][character_id] = character_data

            # Also set as active player if this is the first character
            if len(game_state['characters']) == 1:
                logger.info("Setting as active player character")
                game_state['player'] = character_data

            logger.info(f"Created new character with ID: {character_id}")
            
            # Notify clients about the new character
            communication_manager.notify_state_change('character', character_id, {
                'action': 'creation',
                'character': character_data
            })
            
            # Broadcast the complete updated character state
            communication_manager.update_game_state({"characters": game_state['characters']},
                                                  "character_state_update")

            return game_state

        except Exception as e:
            logger.error(f"Error in handle_character_creation: {str(e)}")
            # Return the original game state without changes
            return game_state

    @staticmethod
    def handle_character_advancement(game_state: Dict[str, Any], agent_request: Dict[str, Any], agent_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle character advancement from CMA response.

        Args:
            game_state: The current game state
            agent_request: The request sent to the CMA
            agent_response: The response from the CMA

        Returns:
            Updated game state with advanced character
        """
        logger.info("Handling character advancement")

        # Get the character ID
        character_id = agent_response.get('character_id')
        if not character_id or character_id not in game_state['characters']:
            logger.warning(f"Character {character_id} not found for advancement")
            return game_state

        # Check if we have advancement data directly in the response
        advancement_data = {}

        # First check if the data is directly in the response
        if 'level' in agent_response and 'previous_level' in agent_response:
            # Data is directly in the response
            advancement_data = agent_response
        # Then check if it's in the outcome field
        elif 'outcome' in agent_response and isinstance(agent_response['outcome'], dict):
            advancement_data = agent_response['outcome']
        else:
            logger.warning("No advancement data found in CMA response")
            return game_state

        # Update the character with advancement changes
        character = game_state['characters'][character_id]

        # Update level
        if 'level' in advancement_data:
            character['level'] = advancement_data['level']

        # Update HP if provided
        if 'hp' in advancement_data:
            hp_data = advancement_data['hp']
            if isinstance(hp_data, dict):
                if 'current' in hp_data:
                    character['hp']['current'] = hp_data['current']
                if 'maximum' in hp_data:
                    character['hp']['maximum'] = hp_data['maximum']
            elif isinstance(hp_data, (int, float)):
                character['hp']['current'] = hp_data
                character['hp']['maximum'] = hp_data

        # Update ability scores if provided
        if 'ability_score_changes' in advancement_data and isinstance(advancement_data['ability_score_changes'], dict):
            if 'abilities' not in character:
                character['abilities'] = {}

            for ability, change in advancement_data['ability_score_changes'].items():
                if ability in character['abilities']:
                    character['abilities'][ability] += change
                else:
                    character['abilities'][ability] = change

        # Update experience points if provided
        if 'experience_points' in advancement_data:
            character['experience_points'] = advancement_data['experience_points']

        # Update next level XP if provided
        if 'next_level_xp' in advancement_data:
            character['next_level_xp'] = advancement_data['next_level_xp']

        # Add advancement to history
        if 'history' not in character:
            character['history'] = []

        advancement_entry = {
            'type': 'advancement',
            'timestamp': agent_request.get('timestamp', 'unknown'),
            'from_level': advancement_data.get('previous_level', character.get('level', 1) - 1),
            'to_level': advancement_data.get('level', character.get('level', 1)),
            'explanation': agent_response.get('explanation', 'Character advanced')
        }

        character['history'].append(advancement_entry)

        logger.info(f"Advanced character {character_id} to level {advancement_data.get('level', 'unknown')}")
        
        # Notify clients about the character advancement
        communication_manager.notify_state_change('character', character_id, {
            'action': 'advancement',
            'advancement': advancement_entry,
            'character': character
        })
        
        # Broadcast the complete updated character state
        communication_manager.update_game_state({"characters": game_state['characters']},
                                              "character_state_update")

        return game_state

    @staticmethod
    def update_magic_state(game_state: Dict[str, Any], agent_request: Dict[str, Any], agent_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the magic state based on the MSA agent response.

        Args:
            game_state: The current game state
            agent_request: The request sent to the MSA
            agent_response: The response from the MSA

        Returns:
            Updated game state
        """
        logger.info("Updating magic state")

        # Make sure we have a valid response
        if not agent_response or not isinstance(agent_response, dict):
            logger.warning("Invalid agent response for magic update")
            return game_state

        # Get the action type
        action_type = agent_response.get('action_type', '')

        # Initialize magic state if it doesn't exist
        if 'magic' not in game_state:
            game_state['magic'] = {
                'prepared_spells': {},
                'spell_components': {},
                'magic_items': [],
                'spell_research': [],
                'turning_undead': []
            }

        # Handle different action types
        if action_type == 'spell_preparation':
            # Update prepared spells
            if 'result' in agent_response and 'prepared_spells' in agent_response['result']:
                character_id = agent_request.get('parameters', {}).get('character_id', 'player1')

                # Initialize character's prepared spells if needed
                if character_id not in game_state['magic']['prepared_spells']:
                    game_state['magic']['prepared_spells'][character_id] = []

                # Add newly prepared spells
                for spell in agent_response['result']['prepared_spells']:
                    if spell not in game_state['magic']['prepared_spells'][character_id]:
                        game_state['magic']['prepared_spells'][character_id].append(spell)

                # Update components needed
                if 'components_needed' in agent_response['result']:
                    for component in agent_response['result']['components_needed']:
                        if component not in game_state['magic']['spell_components']:
                            game_state['magic']['spell_components'][component] = 1
                        else:
                            game_state['magic']['spell_components'][component] += 1

        elif action_type == 'spell_casting':
            # Process spell casting
            if 'result' in agent_response:
                character_id = agent_request.get('parameters', {}).get('character_id', 'player1')

                # Remove the spell from prepared spells if it's an arcane spell
                spell_name = agent_request.get('parameters', {}).get('spell_name', '')
                caster_class = ''

                # Get the caster's class
                if character_id in game_state.get('characters', {}):
                    caster_class = game_state['characters'][character_id].get('class', '')

                # If it's a wizard/magic-user, remove the spell from prepared list
                if caster_class in ['Magic-User', 'Wizard', 'Illusionist']:
                    if character_id in game_state['magic']['prepared_spells']:
                        prepared_spells = game_state['magic']['prepared_spells'][character_id]
                        for i, spell in enumerate(prepared_spells):
                            if spell.get('name', '') == spell_name:
                                game_state['magic']['prepared_spells'][character_id].pop(i)
                                break

                # Consume components
                if 'components_consumed' in agent_response['result']:
                    for component in agent_response['result']['components_consumed']:
                        if component in game_state['magic']['spell_components']:
                            game_state['magic']['spell_components'][component] -= 1
                            if game_state['magic']['spell_components'][component] <= 0:
                                del game_state['magic']['spell_components'][component]

        elif action_type == 'item_identification':
            # Process magic item identification
            if 'result' in agent_response and 'item_properties' in agent_response['result']:
                item_name = agent_request.get('parameters', {}).get('item_name', 'Unknown Item')

                # Check if the item already exists
                item_exists = False
                for i, item in enumerate(game_state['magic']['magic_items']):
                    if item.get('name', '') == item_name:
                        # Update the item
                        game_state['magic']['magic_items'][i].update(agent_response['result'])
                        item_exists = True
                        break

                # If the item doesn't exist, add it
                if not item_exists:
                    new_item = {'name': item_name}
                    new_item.update(agent_response['result'])
                    game_state['magic']['magic_items'].append(new_item)

        elif action_type == 'magical_research':
            # Process magical research
            if 'result' in agent_response:
                character_id = agent_request.get('parameters', {}).get('character_id', 'player1')
                research_type = agent_request.get('parameters', {}).get('research_type', 'spell')

                # Create a research entry
                research_entry = {
                    'character_id': character_id,
                    'type': research_type,
                    'timestamp': agent_request.get('timestamp', 'unknown'),
                    'result': agent_response['result']
                }

                # Add to research history
                game_state['magic']['spell_research'].append(research_entry)

        elif action_type == 'turning_undead':
            # Process turning undead
            if 'result' in agent_response:
                character_id = agent_request.get('parameters', {}).get('character_id', 'player1')

                # Create a turning entry
                turning_entry = {
                    'character_id': character_id,
                    'timestamp': agent_request.get('timestamp', 'unknown'),
                    'undead_type': agent_request.get('parameters', {}).get('undead_type', 'Unknown'),
                    'result': agent_response['result']
                }

                # Add to turning history
                game_state['magic']['turning_undead'].append(turning_entry)

        elif action_type == 'saving_throw':
            # Process magical saving throws
            if 'result' in agent_response:
                target_id = agent_request.get('parameters', {}).get('target_id', '')

                # If this is a player character
                if target_id in game_state.get('characters', {}):
                    # Add to character history
                    if 'history' not in game_state['characters'][target_id]:
                        game_state['characters'][target_id]['history'] = []

                    save_entry = {
                        'type': 'saving_throw',
                        'timestamp': agent_request.get('timestamp', 'unknown'),
                        'save_type': agent_request.get('parameters', {}).get('save_type', 'Unknown'),
                        'result': agent_response['result']
                    }

                    game_state['characters'][target_id]['history'].append(save_entry)

                # If this is a creature/NPC
                elif target_id:
                    # Find the creature
                    for i, creature in enumerate(game_state.get('environment', {}).get('creatures', [])):
                        if creature.get('id') == target_id:
                            # Apply effects based on save result
                            if 'effect' in agent_response['result']:
                                # Handle effects like damage, status changes, etc.
                                pass
                            break

        return game_state

    @staticmethod
    def update_campaign_state(game_state: Dict[str, Any], agent_request: Dict[str, Any], agent_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update the campaign state based on the CaMA agent response.

        Args:
            game_state: The current game state
            agent_request: The request sent to the CaMA
            agent_response: The response from the CaMA

        Returns:
            Updated game state
        """
        logger.info("Updating campaign state")

        # Make sure we have a valid response
        if not agent_response or not isinstance(agent_response, dict):
            logger.warning("Invalid agent response for campaign update")
            return game_state

        # Get the action type
        action_type = agent_response.get('action_type', '')

        # Initialize campaign state if it doesn't exist
        if 'campaign' not in game_state:
            game_state['campaign'] = {
                'name': 'Unnamed Campaign',
                'concept': '',
                'setting': '',
                'timeline': [],
                'factions': [],
                'locations': [],
                'npcs': [],
                'quests': [],
                'events': [],
                'player_achievements': []
            }

        # Handle different action types
        if action_type == 'campaign_creation':
            # Update campaign details
            if 'result' in agent_response:
                # Update campaign name
                if 'campaign_concept' in agent_response['result']:
                    game_state['campaign']['concept'] = agent_response['result']['campaign_concept']

                # Update setting details
                if 'setting_details' in agent_response['result']:
                    game_state['campaign']['setting'] = agent_response['result']['setting_details']

                # Add important locations
                if 'important_locations' in agent_response['result']:
                    for location in agent_response['result']['important_locations']:
                        if isinstance(location, dict):
                            game_state['campaign']['locations'].append(location)
                        else:
                            game_state['campaign']['locations'].append({'name': location, 'description': ''})

                # Add key NPCs
                if 'key_npcs' in agent_response['result']:
                    for npc in agent_response['result']['key_npcs']:
                        if isinstance(npc, dict):
                            game_state['campaign']['npcs'].append(npc)
                        else:
                            game_state['campaign']['npcs'].append({'name': npc, 'description': ''})

                # Add initial adventures/quests
                if 'initial_adventures' in agent_response['result']:
                    for adventure in agent_response['result']['initial_adventures']:
                        if isinstance(adventure, dict):
                            game_state['campaign']['quests'].append(adventure)
                        else:
                            game_state['campaign']['quests'].append({'name': adventure, 'description': '', 'status': 'Available'})

        elif action_type == 'timeline_tracking':
            # Update campaign timeline
            if 'result' in agent_response:
                # Update current date
                if 'current_date' in agent_response['result']:
                    # Make sure world state exists
                    if 'world' not in game_state:
                        game_state['world'] = {'time': {}}
                    elif 'time' not in game_state['world']:
                        game_state['world']['time'] = {}

                    # Update date components
                    date = agent_response['result']['current_date']
                    if isinstance(date, dict):
                        for key, value in date.items():
                            game_state['world']['time'][key] = value

                # Add recent events to timeline
                if 'recent_events' in agent_response['result']:
                    for event in agent_response['result']['recent_events']:
                        if isinstance(event, dict):
                            game_state['campaign']['timeline'].append(event)
                        else:
                            game_state['campaign']['timeline'].append({
                                'description': event,
                                'date': game_state.get('world', {}).get('time', {}).get('day', 1),
                                'type': 'event'
                            })

                # Add upcoming events
                if 'upcoming_events' in agent_response['result']:
                    for event in agent_response['result']['upcoming_events']:
                        if isinstance(event, dict):
                            game_state['campaign']['events'].append(event)
                        else:
                            game_state['campaign']['events'].append({
                                'description': event,
                                'date': game_state.get('world', {}).get('time', {}).get('day', 1) + 1,
                                'type': 'scheduled'
                            })

        elif action_type == 'faction_management':
            # Update faction information
            if 'result' in agent_response:
                # Update faction status
                if 'faction_status' in agent_response['result']:
                    for faction_update in agent_response['result']['faction_status']:
                        faction_name = faction_update.get('name', '')
                        if not faction_name:
                            continue

                        # Check if faction exists
                        faction_exists = False
                        for i, faction in enumerate(game_state['campaign']['factions']):
                            if faction.get('name', '') == faction_name:
                                # Update faction
                                game_state['campaign']['factions'][i].update(faction_update)
                                faction_exists = True
                                break

                        # If faction doesn't exist, add it
                        if not faction_exists:
                            game_state['campaign']['factions'].append(faction_update)

                # Update faction activities
                if 'faction_activities' in agent_response['result']:
                    for activity in agent_response['result']['faction_activities']:
                        faction_name = activity.get('faction', '')
                        if not faction_name:
                            continue

                        # Find the faction
                        for i, faction in enumerate(game_state['campaign']['factions']):
                            if faction.get('name', '') == faction_name:
                                # Add activity to faction
                                if 'activities' not in game_state['campaign']['factions'][i]:
                                    game_state['campaign']['factions'][i]['activities'] = []

                                game_state['campaign']['factions'][i]['activities'].append(activity)
                                break

        elif action_type == 'campaign_management':
            # Update campaign world state
            if 'result' in agent_response:
                # Update world changes
                if 'world_changes' in agent_response['result']:
                    # Add to campaign timeline
                    for change in agent_response['result']['world_changes']:
                        if isinstance(change, dict):
                            change['type'] = 'world_change'
                            game_state['campaign']['timeline'].append(change)
                        else:
                            game_state['campaign']['timeline'].append({
                                'description': change,
                                'date': game_state.get('world', {}).get('time', {}).get('day', 1),
                                'type': 'world_change'
                            })

                # Update NPC developments
                if 'npc_developments' in agent_response['result']:
                    for development in agent_response['result']['npc_developments']:
                        npc_name = development.get('name', '')
                        if not npc_name:
                            continue

                        # Find the NPC
                        for i, npc in enumerate(game_state['campaign']['npcs']):
                            if npc.get('name', '') == npc_name:
                                # Update NPC
                                game_state['campaign']['npcs'][i].update(development)
                                break

        elif action_type == 'session_preparation':
            # Update session preparation
            if 'result' in agent_response:
                # Add adventure hooks
                if 'adventure_hooks' in agent_response['result']:
                    for hook in agent_response['result']['adventure_hooks']:
                        if isinstance(hook, dict):
                            hook['type'] = 'hook'
                            game_state['campaign']['quests'].append(hook)
                        else:
                            game_state['campaign']['quests'].append({
                                'name': hook,
                                'description': '',
                                'status': 'Available',
                                'type': 'hook'
                            })

                # Add planned encounters
                if 'planned_encounters' in agent_response['result']:
                    # Make sure encounters list exists
                    if 'encounters' not in game_state['campaign']:
                        game_state['campaign']['encounters'] = []

                    for encounter in agent_response['result']['planned_encounters']:
                        game_state['campaign']['encounters'].append(encounter)

        elif action_type == 'record_keeping':
            # Update campaign records
            if 'result' in agent_response:
                # Add character achievements
                if 'character_achievements' in agent_response['result']:
                    for achievement in agent_response['result']['character_achievements']:
                        character_id = achievement.get('character_id', '')

                        # Add to player achievements
                        game_state['campaign']['player_achievements'].append(achievement)

                        # If character exists, add to their history
                        if character_id and character_id in game_state.get('characters', {}):
                            if 'history' not in game_state['characters'][character_id]:
                                game_state['characters'][character_id]['history'] = []

                            game_state['characters'][character_id]['history'].append({
                                'type': 'achievement',
                                'timestamp': achievement.get('timestamp', 'unknown'),
                                'description': achievement.get('description', '')
                            })

                # Add campaign milestones
                if 'campaign_milestones' in agent_response['result']:
                    for milestone in agent_response['result']['campaign_milestones']:
                        if isinstance(milestone, dict):
                            milestone['type'] = 'milestone'
                            game_state['campaign']['timeline'].append(milestone)
                        else:
                            game_state['campaign']['timeline'].append({
                                'description': milestone,
                                'date': game_state.get('world', {}).get('time', {}).get('day', 1),
                                'type': 'milestone'
                            })

        return game_state