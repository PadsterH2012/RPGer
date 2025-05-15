# RPG Database Schema Overview

> **Note**: This document provides a comprehensive reference for all database schemas in the RPGer system. For information on the database infrastructure implementation, see [Database Stack Architecture](database-stack-architecture.md). For a high-level overview of the entire system, see [System Architecture](../system/system-architecture.md).

This document provides a structured overview of all database schema elements for the RPG system, organized into logical groups.

## Database Components and Their Roles

The RPGer system uses three complementary database technologies, each serving a specific purpose:

1. **MongoDB**: Primary database for structured data and document storage
   - Stores all schema elements documented in this overview
   - Provides flexible document-based storage for complex nested data
   - Handles relationships between different data entities
   - Supports indexing for efficient queries

2. **Chroma**: Vector database for embeddings and semantic search capabilities
   - Stores vector embeddings for semantic search functionality
   - Enables natural language queries against content
   - Supports AI agents in finding relevant information
   - Optimized for similarity searches and retrieval

3. **Redis**: In-memory database for caching and real-time data access
   - Caches frequently accessed data for performance
   - Manages session state and temporary data
   - Handles pub/sub messaging between components
   - Provides high-speed access to real-time game data

The schemas documented below primarily describe the structure of data stored in MongoDB, though many entities include `vector_embedding` fields that reference data stored in Chroma.

## Core Reference Materials

### Monster Schema
- `_id`: Unique identifier
- `name`: Monster name
- `category`: Classification
- `stats`: Basic game statistics
  - `frequency`
  - `no_appearing`
  - `armor_class`
  - `move`
  - `hit_dice`
  - `treasure_type`
- `description`: Textual description
- `path`: Reference to source file
- `metadata`: Basic classification data
  - `type`
  - `alignment`
  - `challenge_rating`
  - `size`
  - `languages`
  - `senses`
- `habitat`: Location and environment information
  - `primary_environments`
  - `terrain_preferences`
  - `climate_preferences`
  - `regional_distribution`
  - `specific_locations`
  - `migration_patterns`
  - `lair_description`
- `ecology`: Behavioral and ecosystem information
  - `diet`
  - `predators`
  - `prey`
  - `behavior`
  - `lifecycle`
  - `socialization`
  - `interaction_with_civilization`
- `chunks`: Text segments with vector embeddings
- `related_monsters`: References to similar creatures
- `encounter_suggestions`: Pre-built encounter ideas
- `campaign_usage`: Integration with storylines
  - `plot_hooks`
  - `regional_variants`
- `extended_properties`: Additional capabilities
  - `legendary_actions`
  - `lair_actions`
  - `regional_effects`
  - `custom_abilities`

### Spell Schema
- `_id`: Unique identifier
- `name`: Spell name
- `level`: Spell level
- `class`: Class that can cast the spell
- `components`: Required components
- `range`: Effective range
- `duration`: How long the spell lasts
- `description`: Spell effects
- `metadata`: Classification information
  - `school`
  - `damage_type`
  - `save`
- `vector_embedding`: For semantic search
- `extended_properties`: Additional information
  - `higher_level_casting`
  - `material_components`
  - `ritual`

### Item Schema
- `_id`: Unique identifier
- `name`: Item name
- `type`: Item category
- `subtype`: Specific type
- `rarity`: How rare the item is
- `description`: Item description
- `properties`: Physical characteristics
  - `damage`
  - `damage_type`
  - `weight`
  - `properties`
- `magical_properties`: Magical effects
  - `bonus`
  - `abilities`
  - `attunement`
- `vector_embedding`: For semantic search
- `extended_properties`: Additional information
  - `creator`
  - `lore`
  - `variants`

### Character Class Schema
- `_id`: Unique identifier
- `name`: Class name
- `type`: Entity type
- `description`: Class description
- `hit_die`: Hit die type
- `primary_abilities`: Key ability scores
- `saving_throws`: Proficient saving throws
- `armor_proficiencies`: Armor types usable
- `weapon_proficiencies`: Weapon types usable
- `abilities`: Class features
- `vector_embedding`: For semantic search
- `extended_properties`: Additional information
  - `archetypes`
  - `multiclass_requirements`

## World Building Elements

### Campaign World Schema
- `_id`: Unique identifier
- `name`: World name
- `description`: World description
- `geography`: Physical features
  - `continents`
  - `major_bodies_of_water`
  - `mountain_ranges`
  - `forests`
  - `deserts`
  - `plains`
  - `swamps`
- `climate_zones`: Climate information
- `political_regions`: Nations and territories
- `settlements`: Cities, towns, villages
- `points_of_interest`: Notable locations
- `history`: Historical timeline
- `vector_embedding`: For semantic search
- `maps`: Visual representations
- `extended_properties`: Additional information
  - `magical_properties`
  - `cosmology`

### Settlement Schema
- `_id`: Unique identifier
- `name`: Settlement name
- `type`: Settlement category
- `description`: Settlement description
- `population`: Number of inhabitants
- `demographics`: Population breakdown
- `economy`: Economic information
  - `primary_industries`
  - `wealth_level`
  - `notable_exports`
  - `currency`
  - `trade_partners`
- `locations`: Places within settlement
- `government`: Political structure
- `defenses`: Military and protective measures
- `history`: Settlement timeline
- `hooks`: Adventure hooks
- `vector_embedding`: For semantic search
- `extended_properties`: Additional information
  - `festivals`
  - `local_customs`

### Geographic Feature Schema
- `_id`: Unique identifier
- `name`: Feature name
- `type`: Feature type
- `description`: Feature description
- `location`: Where it's located
- `climate`: Weather patterns
- `flora`: Plant life
- `fauna`: Animal life
- `resources`: Available resources
- `settlements`: Associated settlements
- `points_of_interest`: Notable locations
- `hazards`: Dangers
- `vector_embedding`: For semantic search
- `extended_properties`: Additional information
  - `magical_properties`

### Weather System Schema
- `_id`: Unique identifier
- `region_id`: Associated region
- `climate_type`: Climate classification
- `seasons`: Seasonal information
  - `name`
  - `months`
  - `temperature_range`
  - `precipitation`
  - `wind_patterns`
  - `special_conditions`
- `weather_events`: Special weather phenomena
- `vector_embedding`: For semantic search
- `extended_properties`: Additional information
  - `magical_influences`

### Weather Pattern Schema
- `_id`: Unique identifier
- `region_id`: Associated region
- `year`: Game world year
- `starting_day`: First day in sequence
- `pattern_seed`: Randomization seed
- `region_data`: Geographic information
  - `coordinates`: Map coordinates
  - `elevation`: Height above sea level
  - `terrain_type`: Primary terrain
  - `water_bodies`: Nearby water features
  - `region_size`: Area covered
- `daily_weather`: Array of daily conditions
  - `day_number`: Day in sequence
  - `season`: Current season
  - `temperature`: Temperature value
    - `morning`: Morning temperature
    - `midday`: Midday temperature
    - `evening`: Evening temperature
    - `night`: Night temperature
  - `precipitation`: Precipitation details
    - `type`: Rain, snow, etc.
    - `intensity`: Light, moderate, heavy
    - `duration_hours`: How long it lasts
  - `wind`: Wind conditions
    - `direction`: Wind direction
    - `speed`: Wind speed
    - `gusts`: Gust strength
  - `cloud_cover`: Cloud coverage percentage
  - `special_conditions`: Fog, mist, etc.
  - `description_tags`: Keywords for descriptions
  - `narrative_hooks`: Weather-related story elements
    - `description`: "The rain finally breaks after three days of downpour"
    - `gameplay_effects`: Muddy roads, flooded areas
    - `mood`: Gloomy, refreshing, oppressive
- `weather_transitions`: Patterns of change
  - `from_condition`: Starting weather
  - `to_condition`: Ending weather
  - `transition_description`: How weather changes
  - `duration_days`: How long transition takes
- `seasonal_events`: Special seasonal occurrences
  - `first_frost`
  - `first_snow`
  - `spring_thaw`
  - `monsoon_start`
- `agricultural_indicators`: Farming-related weather
  - `planting_season_start`
  - `harvest_season_start`
  - `drought_risk`
  - `flood_risk`

### Weather Interpolation Schema
- `_id`: Unique identifier
- `name`: Name of interpolation system
- `description`: How the system works
- `interpolation_parameters`: Configuration settings
  - `max_interpolation_distance`: Maximum distance for interpolation
  - `elevation_lapse_rate`: Temperature change per elevation unit
  - `distance_weight_factor`: How distance affects weighting
  - `terrain_influence_factor`: How terrain affects interpolation
- `terrain_modifiers`: Adjustments for terrain types
  - `mountain`: Mountain-specific modifiers
    - `temperature_modifier`: Temperature adjustment
    - `precipitation_modifier`: Precipitation adjustment
    - `wind_modifier`: Wind adjustment
  - `forest`: Forest-specific modifiers
  - `coast`: Coastal area modifiers
  - `valley`: Valley-specific modifiers
  - `desert`: Desert-specific modifiers
  - `plains`: Plains-specific modifiers
- `feature_modifiers`: Adjustments for geographic features
  - `lake_effect`: Effects of nearby lakes
  - `ocean_proximity`: Effects of ocean proximity
  - `mountain_rain_shadow`: Effects of mountain rain shadows
  - `urban_heat_island`: Effects of urban areas
- `interpolation_methods`: Calculation approaches
  - `temperature`: Method for temperature interpolation
  - `precipitation`: Method for precipitation interpolation
  - `wind`: Method for wind interpolation
  - `cloud_cover`: Method for cloud cover interpolation
- `transition_handling`: How to handle weather transitions
  - `boundary_smoothing`: Techniques for smooth transitions
  - `front_movement`: Simulation of weather front movement
  - `storm_tracking`: Tracking of storm systems

## Narrative Elements

### Storyline Schema
- `_id`: Unique identifier
- `title`: Storyline name
- `type`: Storyline category
- `description`: Storyline overview
- `theme`: Thematic elements
- `recommended_level_range`: Suitable character levels
- `plot_points`: Story progression points
- `hooks`: Ways to introduce storyline
- `resolution_options`: Possible endings
- `rewards`: Player rewards
- `connections`: Links to other content
- `vector_embedding`: For semantic search
- `extended_properties`: Additional information
  - `inspirations`
  - `alternate_versions`

### NPC Schema
- `_id`: Unique identifier
- `name`: NPC name
- `race`: Species
- `class`: Character class
- `level`: Experience level
- `description`: Physical description
- `appearance`: Detailed physical traits
- `personality`: Character traits
- `voice`: Speech patterns
- `background`: Personal history
- `stats`: Game statistics
- `combat_style`: Fighting approach
- `relationships`: Connections to others
- `knowledge`: What they know
- `locations`: Where they can be found
- `hooks`: Adventure hooks
- `behavior_patterns`: Extracted behavior patterns
  - `interaction_patterns`: How the NPC interacts with others
    - `pattern_id`: Reference to extracted pattern
    - `pattern_type`: Type of interaction pattern
    - `trigger_conditions`: What prompts this behavior
    - `response_tendencies`: How the NPC typically responds
  - `decision_making`: How the NPC makes decisions
    - `priorities`: What the NPC values most
    - `risk_tolerance`: How the NPC handles risk
    - `moral_framework`: Ethical considerations
  - `emotional_responses`: How the NPC responds emotionally
    - `primary_emotions`: Dominant emotional states
    - `emotional_triggers`: What provokes emotional responses
    - `expression_style`: How emotions are displayed
  - `routine_behaviors`: Regular activities and habits
    - `daily_routines`: Regular activities
    - `quirks`: Distinctive behavioral quirks
    - `comfort_behaviors`: What the NPC does when comfortable
    - `stress_behaviors`: What the NPC does when stressed
  - `social_dynamics`: How the NPC behaves in groups
    - `leadership_style`: How the NPC leads or follows
    - `group_role`: Typical role in group settings
    - `status_signals`: How status is displayed or acknowledged
- `novel_extraction_metadata`: Information about pattern sources
  - `description_pattern_id`: Source of description pattern
  - `dialogue_pattern_ids`: Sources of dialogue patterns
  - `personality_pattern_id`: Source of personality pattern
  - `behavior_pattern_ids`: Sources of behavior patterns
  - `transformation_methods`: How patterns were adapted
- `vector_embedding`: For semantic search
- `extended_properties`: Additional information
  - `faction_memberships`
  - `secrets`
  - `possessions`

#### Example NPC Record with Behavior Patterns

```json
{
  "_id": "NPC-127",
  "name": "Harbormaster Selene",
  "race": "Human",
  "class": "Expert",
  "level": 5,
  "description": "Harbormaster Selene stands by the tide charts, her compact frame bent intently over the ink-marked parchment. The lantern light catches the silver in her braided hair as she traces the current patterns with a weathered finger.",
  "personality": ["practical", "authoritative", "protective", "experienced"],
  "voice": {
    "speech_pattern": "Direct and technical, using maritime terminology naturally",
    "common_phrases": ["Mark my words", "I've seen it before", "Safety first, always"],
    "tone": "Firm but not unkind"
  },
  "behavior_patterns": {
    "interaction_patterns": [
      {
        "pattern_id": "IP-042",
        "pattern_type": "authority-expertise",
        "trigger_conditions": "When safety or regulations are questioned",
        "response_tendencies": "Provides historical examples that validate her position"
      },
      {
        "pattern_id": "IP-089",
        "pattern_type": "mentorship",
        "trigger_conditions": "When interacting with inexperienced sailors",
        "response_tendencies": "Offers advice wrapped in personal anecdotes"
      }
    ],
    "decision_making": {
      "priorities": ["safety of vessels", "efficiency of harbor", "upholding regulations"],
      "risk_tolerance": "Low for others' safety, moderate for personal risk",
      "moral_framework": "Utilitarian with strong sense of duty"
    },
    "emotional_responses": {
      "primary_emotions": ["concern", "pride", "frustration"],
      "emotional_triggers": {
        "concern": "Dangerous weather or reckless behavior",
        "pride": "Well-run harbor operations, successful navigation of difficult conditions",
        "frustration": "Bureaucratic obstacles, disregard for expertise"
      },
      "expression_style": "Restrained but visible in body language and tone"
    }
  },
  "novel_extraction_metadata": {
    "description_pattern_id": "PD-127",
    "dialogue_pattern_ids": ["DP-089", "DP-142"],
    "personality_pattern_id": "PP-056",
    "behavior_pattern_ids": ["BP-042", "BP-089"],
    "transformation_methods": ["context shift", "gender variation", "role adaptation"]
  }
}
```

### Name Collection Schema
- `_id`: Unique identifier
- `category`: Name type
- `description`: Collection description
- `male_first_names`: Male names
- `female_first_names`: Female names
- `clan_names`: Family/clan names
- `name_patterns`: Naming conventions
- `naming_traditions`: Cultural naming practices
- `vector_embedding`: For semantic search

### Plot Idea Schema
- `_id`: Unique identifier
- `title`: Idea name
- `category`: Idea type
- `tags`: Classification tags
- `description`: Idea overview
- `hooks`: Ways to introduce
- `key_npcs`: Important characters
- `possible_causes`: Potential origins
- `possible_solutions`: Resolution options
- `complications`: Additional challenges
- `rewards`: Player rewards
- `adaptability`: Flexibility options
- `vector_embedding`: For semantic search

## Player Elements

### Player Account Schema
- `_id`: Unique identifier
- `username`: Account name
- `email`: Contact information
- `created_date`: Account creation date
- `last_login`: Last activity
- `preferences`: User settings
  - `theme`
  - `notification_settings`
  - `ui_settings`
  - `accessibility`
- `session_history`: Past game sessions
- `characters`: Player characters
- `extended_properties`: Additional information
  - `play_style_preferences`
  - `favorite_campaigns`
  - `notes`

### Player Character Schema
- `_id`: Unique identifier
- `name`: Character name
- `player_id`: Associated player
- `campaign_id`: Associated campaign
- `race`: Species
- `class`: Character class
- `subclass`: Class specialization
- `level`: Experience level
- `experience_points`: XP total
- `alignment`: Moral alignment
- `background`: Character origin
- `appearance`: Physical description
- `personality`: Character traits
- `stats`: Ability scores
- `saving_throws`: Save bonuses
- `skills`: Skill proficiencies
- `abilities`: Special capabilities
- `inventory`: Possessions
- `spells`: Known/prepared spells
- `companions`: Animal companions/familiars
- `background_details`: Personal history
- `relationships`: Connections to NPCs
- `quests`: Active storylines
- `journal_entries`: Character notes
- `vector_embedding`: For semantic search
- `extended_properties`: Additional information
  - `character_development_goals`
  - `personal_quests`
  - `character_hooks`

### Game Session Schema
- `_id`: Unique identifier
- `campaign_id`: Associated campaign
- `title`: Session name
- `session_number`: Sequence number
- `date`: When session occurred
- `duration_minutes`: Session length
- `players_present`: Participating players
- `location_id`: In-game location
- `summary`: Session overview
- `key_events`: Important happenings
- `storyline_progress`: Plot advancement
- `dm_notes`: DM observations
- `player_feedback`: Player responses
- `vector_embedding`: For semantic search

## Content Generation Elements

### Action-Specific Prompt Assembly Schema
- `_id`: Unique identifier
- `agent_type`: Type of agent (DMA, CMA, CRA, etc.)
- `action_category`: Category of action
- `prompt_components`: Collection of prompt elements
  - `base_templates`: Base templates for different actions
    - `template_id`: Unique template identifier
    - `template_structure`: Basic structure of the prompt
    - `required_parameters`: Parameters that must be included
    - `optional_parameters`: Parameters that can be included
  - `instruction_sets`: Sets of instructions for different actions
    - `instruction_id`: Unique instruction identifier
    - `instruction_text`: The actual instruction
    - `purpose`: What the instruction accomplishes
    - `success_rate`: How often the instruction leads to success
  - `context_elements`: Contextual information elements
    - `element_id`: Unique element identifier
    - `element_type`: Type of context element
    - `relevance_score`: How relevant the element is
    - `token_cost`: Approximate token usage
  - `parameter_sets`: Sets of parameters for different actions
    - `parameter_id`: Unique parameter identifier
    - `parameter_name`: Name of the parameter
    - `parameter_description`: Description of the parameter
    - `parameter_type`: Data type of the parameter
- `error_patterns`: Patterns of errors to avoid
  - `error_id`: Unique error identifier
  - `error_description`: Description of the error
  - `error_frequency`: How often the error occurs
  - `associated_components`: Components associated with the error
  - `avoidance_strategies`: Strategies to avoid the error
- `performance_metrics`: Metrics for evaluating performance
  - `token_efficiency`: Token usage metrics
  - `response_quality`: Quality metrics
  - `error_rate`: Error frequency metrics
  - `response_time`: Latency metrics
- `vector_embeddings`: Vector representations for retrieval
  - `component_vectors`: Vectors for prompt components
  - `error_vectors`: Vectors for error patterns
- `metadata`: Additional information
  - `creation_date`: When the assembly was created
  - `last_updated`: When the assembly was last updated
  - `version`: Version number
  - `usage_count`: How often the assembly has been used

#### Example Action-Specific Prompt Assembly Records

```json
{
  "_id": "ASPA-001",
  "agent_type": "DMA",
  "action_category": "NPC_DIALOGUE_GENERATION",
  "prompt_components": {
    "base_templates": [
      {
        "template_id": "BT-042",
        "template_structure": "You are generating dialogue for an NPC named {npc_name} who is {npc_role}. The player character {player_name} has just {player_action}. Respond with dialogue that {dialogue_purpose}.",
        "required_parameters": ["npc_name", "npc_role", "player_name", "player_action", "dialogue_purpose"],
        "optional_parameters": ["npc_mood", "location_context", "time_of_day"],
        "success_rate": 0.87
      }
    ],
    "instruction_sets": [
      {
        "instruction_id": "IS-127",
        "instruction_text": "Keep the dialogue concise and authentic to the character's personality.",
        "purpose": "Ensures dialogue quality and consistency",
        "success_rate": 0.92
      },
      {
        "instruction_id": "IS-128",
        "instruction_text": "Include one subtle reference to the NPC's background or current situation.",
        "purpose": "Adds depth and continuity to the character",
        "success_rate": 0.85
      }
    ],
    "context_elements": [
      {
        "element_id": "CE-056",
        "element_type": "NPC_PERSONALITY",
        "element_content": "{npc_name} is {personality_traits} and tends to {behavioral_pattern}.",
        "relevance_score": 0.95,
        "token_cost": 25
      }
    ]
  },
  "error_patterns": [
    {
      "error_id": "EP-023",
      "error_description": "NPC responds as if they know information they shouldn't have access to",
      "error_frequency": 0.15,
      "associated_components": ["IS-129", "CE-057"],
      "avoidance_strategies": ["Explicitly state information limitations", "Check for knowledge boundaries"]
    },
    {
      "error_id": "EP-024",
      "error_description": "Dialogue becomes repetitive with similar phrasing patterns",
      "error_frequency": 0.22,
      "associated_components": ["BT-043"],
      "avoidance_strategies": ["Vary sentence structures", "Include instruction for diverse phrasing"]
    }
  ],
  "performance_metrics": {
    "token_efficiency": {
      "average_tokens_per_call": 320,
      "token_reduction_from_baseline": 0.45
    },
    "response_quality": {
      "player_satisfaction_rating": 4.2,
      "consistency_score": 0.88,
      "variety_score": 0.76
    },
    "error_rate": {
      "overall_error_frequency": 0.08,
      "most_common_error": "EP-024"
    }
  },
  "metadata": {
    "creation_date": "2023-04-15",
    "last_updated": "2023-05-12",
    "version": "1.3",
    "usage_count": 342
  }
}
```

### Novel Extraction Schema
- `_id`: Unique identifier
- `source_novel`: Source information
  - `title`: Novel title
  - `author`: Novel author
  - `genre`: Literary genre
  - `publication_year`: Year published
- `extraction_patterns`: Extracted patterns
  - `character_description_patterns`: Character description templates
    - `pattern_structure`: Template structure
    - `focus_elements`: What the pattern emphasizes
    - `sensory_elements`: Sensory details included
  - `dialogue_patterns`: Speech pattern templates
    - `sentence_structures`: Common sentence forms
    - `vocabulary_level`: Complexity of language
    - `emotional_expressions`: How emotions are conveyed
  - `personality_patterns`: Character trait templates
    - `trait_combinations`: Sets of complementary traits
    - `behavioral_expressions`: How traits manifest
    - `decision_patterns`: How decisions are made
  - `environment_patterns`: Setting description templates
    - `description_structure`: Template structure
    - `atmosphere_elements`: Mood-setting techniques
    - `detail_focus`: What aspects are emphasized
- `transformation_methods`: How patterns are modified
  - `context_shifts`: Setting adaptation techniques
  - `detail_substitutions`: Element replacement approaches
  - `variation_techniques`: Creating diversity
- `metadata`: Additional information
  - `extraction_date`: When patterns were extracted
  - `quality_rating`: Pattern effectiveness score
  - `usage_count`: How often used
  - `success_rate`: How well patterns perform

#### Example Novel Extraction Records

```json
{
  "_id": "NE-001",
  "source_novel": {
    "title": "The Sea Captain's Journey",
    "author": "Elizabeth Harmon",
    "genre": "Maritime Fiction",
    "publication_year": 1998
  },
  "extraction_patterns": {
    "character_description_patterns": [
      {
        "pattern_id": "PD-127",
        "pattern_structure": "[CHARACTER] stood by [LOCATION_FEATURE], [PHYSICAL_ATTRIBUTE] [POSITION_DETAIL]",
        "focus_elements": ["posture", "environment interaction", "lighting"],
        "sensory_elements": ["visual", "spatial"],
        "example": "Harbor Master Selene stood by the tide charts, her compact frame bent intently over the ink-marked parchment."
      }
    ],
    "dialogue_patterns": [
      {
        "pattern_id": "DP-089",
        "structure": "threat assessment + conditional consequence + experience-based authority statement",
        "sentence_structures": ["complex-compound", "conditional"],
        "vocabulary_level": "professional-specialized",
        "emotional_expressions": ["concern", "authority", "determination"],
        "example": "The western reefs are treacherous this season. If merchant vessels attempt the direct route during the autumn squalls, we'll see wrecks piling up on the shoals."
      }
    ],
    "personality_patterns": [
      {
        "pattern_id": "PP-056",
        "trait_combinations": ["practical", "authoritative", "protective", "experienced"],
        "behavioral_expressions": ["preventative action", "reference to experience", "prioritizing safety"],
        "decision_patterns": ["cautious but firm", "based on extensive experience"],
        "example": "I've charted these waters for twenty-five years, and I won't have lives lost to save a few days' sailing time."
      }
    ]
  },
  "transformation_methods": {
    "context_shifts": ["maritime to mountain pass", "captain to caravan leader"],
    "detail_substitutions": ["ships to caravans", "reefs to narrow passes", "tides to seasonal storms"],
    "variation_techniques": ["gender variation", "age adjustment", "expertise domain shift"]
  },
  "metadata": {
    "extraction_date": "2023-05-10",
    "quality_rating": 4.8,
    "usage_count": 27,
    "success_rate": 0.92
  }
}
```

## Campaign Elements

### Campaign Package Schema
- `_id`: Unique identifier
- `name`: Campaign name
- `description`: Campaign overview
- `difficulty`: Challenge level
- `level_range`: Character level range
- `themes`: Thematic elements
- `world_id`: Associated world
- `main_storyline_id`: Primary plot
- `side_storylines`: Secondary plots
- `major_npcs`: Important characters
- `key_locations`: Important places
- `factions`: Organizations
- `starting_location`: Beginning point
- `creation_date`: When created
- `tags`: Classification tags
- `recommended_party_size`: Player count
- `pacing`: Game rhythm
- `hooks`: Introduction methods
- `key_items`: Important objects
- `secrets_and_revelations`: Hidden information
- `vector_embedding`: For semantic search
- `metadata`: Additional information
- `extended_properties`: Extra features
  - `custom_rules`
  - `handouts`

### Generation Process Schema
- `_id`: Unique identifier
- `campaign_id`: Associated campaign
- `generation_steps`: Creation process
- `generation_parameters`: Creation settings
- `generation_date`: When created
- `generation_time_seconds`: Processing time
- `ai_models_used`: AI models involved

### AI Agent Workflow Schema
- `_id`: Unique identifier
- `campaign_id`: Associated campaign
- `session_id`: Associated session
- `agent_workflows`: Agent configurations
  - `DMA`: Dungeon Master Agent - Coordinates other agents and manages overall narrative
  - `CRA`: Combat Resolution Agent - Handles combat mechanics and encounters
  - `CMA`: Character Management Agent - Manages player and NPC character data
  - `NEA`: NPC & Encounter Agent - Generates NPC interactions and encounters
  - `EEA`: Exploration Engine Agent - Manages world exploration and discovery
  - `WEA`: World & Environment Agent - Handles environment descriptions and effects
  - `MSA`: Magic System Agent - Manages magical effects and spell interactions
  - `CaMA`: Campaign Manager Agent - Tracks campaign progress and storylines
- `inter_agent_communication`: Agent interaction
- `state_tracking`: Game state management
