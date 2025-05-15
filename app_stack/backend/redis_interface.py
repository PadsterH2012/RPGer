# redis_interface.py
import json
import redis
from typing import Dict, Any, List, Optional

class RedisInterface:
    def __init__(self, host='localhost', port=6379, db=0):
        """Initialize Redis connection"""
        try:
            self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
            self.redis.ping()  # Test connection
            print("Connected to Redis server")
        except redis.ConnectionError:
            print("WARNING: Could not connect to Redis server. Using in-memory fallback.")
            self.redis = None
            self.memory_store = {}
            self.conversation_history = []

    def get_game_state(self) -> Dict[str, Any]:
        """Get the current game state from Redis"""
        if self.redis is None:
            return self._get_memory_game_state()

        game_state = {
            'characters': {},
            'environment': {}
        }

        # Get character data
        char_keys = self.redis.keys('game:state:characters:*')
        for key in char_keys:
            char_id = key.split(':')[-1]
            char_data = self.redis.get(key)
            if char_data:
                game_state['characters'][char_id] = json.loads(char_data)

        # Get environment data
        env_data = self.redis.get('game:state:environment')
        if env_data:
            game_state['environment'] = json.loads(env_data)

        return game_state

    def update_game_state(self, state_changes: Dict[str, Any]) -> None:
        """Update game state with changes"""
        if self.redis is None:
            self._update_memory_game_state(state_changes)
            return

        # Process character changes
        if 'characters' in state_changes:
            for char_id, char_data in state_changes['characters'].items():
                # Get existing data
                existing_data = self.redis.get(f'game:state:characters:{char_id}')
                if existing_data:
                    existing_char = json.loads(existing_data)
                    # Update with new data
                    existing_char.update(char_data)
                    self.redis.set(f'game:state:characters:{char_id}', json.dumps(existing_char))
                else:
                    # New character
                    self.redis.set(f'game:state:characters:{char_id}', json.dumps(char_data))

        # Process environment changes
        if 'environment' in state_changes:
            existing_data = self.redis.get('game:state:environment')
            if existing_data:
                existing_env = json.loads(existing_data)
                # Update with new data
                existing_env.update(state_changes['environment'])
                self.redis.set('game:state:environment', json.dumps(existing_env))
            else:
                # New environment
                self.redis.set('game:state:environment', json.dumps(state_changes['environment']))

    def update_creature_hp(self, creature_id: str, damage: int) -> None:
        """Update a creature's HP after taking damage"""
        if self.redis is None:
            self._update_memory_creature_hp(creature_id, damage)
            return

        # Get environment data
        env_data = self.redis.get('game:state:environment')
        if not env_data:
            print("ERROR: No environment data found")
            return

        environment = json.loads(env_data)

        # Find the creature and update HP
        if 'creatures' in environment:
            for i, creature in enumerate(environment['creatures']):
                if creature.get('id') == creature_id:
                    # Apply damage
                    current_hp = creature.get('hp', {}).get('current', 0)
                    new_hp = max(0, current_hp - damage)
                    environment['creatures'][i]['hp']['current'] = new_hp

                    # If creature is defeated, remove it
                    if new_hp <= 0:
                        print(f"{creature.get('name')} has been defeated and removed from the game.")
                        environment['creatures'].pop(i)
                    else:
                        print(f"{creature.get('name')} took {damage} damage.")

                    # Update environment in Redis
                    self.redis.set('game:state:environment', json.dumps(environment))
                    return

        # Check if it's a player character
        char_data = self.redis.get(f'game:state:characters:{creature_id}')
        if char_data:
            character = json.loads(char_data)
            # Apply damage
            current_hp = character.get('hp', {}).get('current', 0)
            new_hp = max(0, current_hp - damage)
            character['hp']['current'] = new_hp

            # Update character in Redis
            self.redis.set(f'game:state:characters:{creature_id}', json.dumps(character))
            print(f"{character.get('name')} took {damage} damage.")
            return

        print(f"WARNING: Could not find character or creature with ID {creature_id}")

    def update_character_hp(self, char_id: str, damage: int, healing: bool = False) -> None:
        """Update a player character's HP (damage or healing)"""
        if self.redis is None:
            self._update_memory_character_hp(char_id, damage, healing)
            return

        # Get character data
        char_data = self.redis.get(f'game:state:characters:{char_id}')
        if not char_data:
            print(f"ERROR: No character data found for ID {char_id}")
            return

        character = json.loads(char_data)

        # Apply damage or healing
        current_hp = character.get('hp', {}).get('current', 0)
        max_hp = character.get('hp', {}).get('maximum', 0)

        if healing:
            # Healing
            new_hp = min(max_hp, current_hp + damage)
            character['hp']['current'] = new_hp
            print(f"{character.get('name')} was healed for {damage} points. HP now {new_hp}/{max_hp}")
        else:
            # Damage
            new_hp = max(0, current_hp - damage)
            character['hp']['current'] = new_hp

            if new_hp <= 0:
                print(f"{character.get('name')} has fallen unconscious!")
            else:
                print(f"{character.get('name')} took {damage} damage.")

        # Update character in Redis
        self.redis.set(f'game:state:characters:{char_id}', json.dumps(character))

    def add_to_memory(self, agent: str, content: str, is_player: bool = False) -> None:
        """Add a message to the agent's memory"""
        if self.redis is None:
            self._add_to_memory_store(agent, content, is_player)
            return

        # Add to conversation history
        timestamp = self.redis.time()[0]  # Unix timestamp
        entry = {
            'timestamp': timestamp,
            'agent': 'Player' if is_player else agent,
            'content': content
        }

        self.redis.lpush('memory:conversation', json.dumps(entry))

        # Trim to last 100 messages
        self.redis.ltrim('memory:conversation', 0, 99)

    def get_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history"""
        if self.redis is None:
            return self._get_memory_conversation_history(limit)

        history = []
        entries = self.redis.lrange('memory:conversation', 0, limit - 1)

        for entry in entries:
            history.append(json.loads(entry))

        return history

    # In-memory fallback methods
    def _get_memory_game_state(self) -> Dict[str, Any]:
        """Get game state from memory"""
        return self.memory_store.get('game_state', {
            'characters': {},
            'environment': {}
        })

    def _update_memory_game_state(self, state_changes: Dict[str, Any]) -> None:
        """Update in-memory game state"""
        if 'game_state' not in self.memory_store:
            self.memory_store['game_state'] = {
                'characters': {},
                'environment': {}
            }

        game_state = self.memory_store['game_state']

        # Process character changes
        if 'characters' in state_changes:
            for char_id, char_data in state_changes['characters'].items():
                if char_id in game_state['characters']:
                    game_state['characters'][char_id].update(char_data)
                else:
                    game_state['characters'][char_id] = char_data

        # Process environment changes
        if 'environment' in state_changes:
            game_state['environment'].update(state_changes['environment'])

    def _update_memory_creature_hp(self, creature_id: str, damage: int) -> None:
        """Update a creature's HP in memory"""
        if 'game_state' not in self.memory_store or 'environment' not in self.memory_store['game_state']:
            print("ERROR: No environment data found in memory")
            return

        environment = self.memory_store['game_state']['environment']

        # Find the creature and update HP
        if 'creatures' in environment:
            for i, creature in enumerate(environment['creatures']):
                if creature.get('id') == creature_id:
                    # Apply damage
                    current_hp = creature.get('hp', {}).get('current', 0)
                    new_hp = max(0, current_hp - damage)
                    environment['creatures'][i]['hp']['current'] = new_hp

                    # If creature is defeated, remove it
                    if new_hp <= 0:
                        print(f"{creature.get('name')} has been defeated and removed from the game.")
                        environment['creatures'].pop(i)
                    else:
                        print(f"{creature.get('name')} took {damage} damage.")
                    return

        # Check if it's a player character
        if 'characters' in self.memory_store['game_state']:
            if creature_id in self.memory_store['game_state']['characters']:
                character = self.memory_store['game_state']['characters'][creature_id]
                # Apply damage
                current_hp = character.get('hp', {}).get('current', 0)
                new_hp = max(0, current_hp - damage)
                character['hp']['current'] = new_hp

                print(f"{character.get('name')} took {damage} damage.")
                return

        print(f"WARNING: Could not find character or creature with ID {creature_id}")

    def _update_memory_character_hp(self, char_id: str, damage: int, healing: bool = False) -> None:
        """Update a player character's HP in memory (damage or healing)"""
        if 'game_state' not in self.memory_store or 'characters' not in self.memory_store['game_state']:
            print("ERROR: No character data found in memory")
            return

        if char_id not in self.memory_store['game_state']['characters']:
            print(f"ERROR: No character data found for ID {char_id}")
            return

        character = self.memory_store['game_state']['characters'][char_id]

        # Apply damage or healing
        current_hp = character.get('hp', {}).get('current', 0)
        max_hp = character.get('hp', {}).get('maximum', 0)

        if healing:
            # Healing
            new_hp = min(max_hp, current_hp + damage)
            character['hp']['current'] = new_hp
            print(f"{character.get('name')} was healed for {damage} points. HP now {new_hp}/{max_hp}")
        else:
            # Damage
            new_hp = max(0, current_hp - damage)
            character['hp']['current'] = new_hp

            if new_hp <= 0:
                print(f"{character.get('name')} has fallen unconscious!")
            else:
                print(f"{character.get('name')} took {damage} damage.")

    def _add_to_memory_store(self, agent: str, content: str, is_player: bool = False) -> None:
        """Add a message to the in-memory conversation history"""
        import time

        entry = {
            'timestamp': int(time.time()),
            'agent': 'Player' if is_player else agent,
            'content': content
        }

        self.conversation_history.insert(0, entry)

        # Trim to last 100 messages
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[:100]

    def _get_memory_conversation_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get conversation history from memory"""
        return self.conversation_history[:limit]