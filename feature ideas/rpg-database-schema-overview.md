# RPG Database Schema Overview

This document provides a structured overview of all database schema elements for the RPG system, organized into logical groups.

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
- `vector_embedding`: For semantic search
- `extended_properties`: Additional information
  - `faction_memberships`
  - `secrets`
  - `possessions`

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
  - `DungeonMasterAgent`
  - `NPCAgent`
  - `EnvironmentAgent`
  - `CombatAgent`
- `inter_agent_communication`: Agent interaction
- `state_tracking`: Game state management
