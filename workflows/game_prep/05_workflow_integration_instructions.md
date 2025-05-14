# AD&D Workflow Integration Instructions

## Overview
This document provides instructions for how each AD&D workflow should interact with the game record system. It specifies which files each workflow should read from and write to during execution.

## General Integration Principles

1. **Read Before Write**: Workflows should always read the current state of relevant files before making updates
2. **Atomic Updates**: Updates to files should be complete and consistent
3. **Cross-References**: Maintain references between related files
4. **Versioning**: Consider tracking significant changes to important files
5. **Error Handling**: Have procedures for handling inconsistencies or missing data

## Interaction Workflow Integration

### Phase 0: Session Initialization
- **Reads From**:
  - `Session/Session_Records/Current_Game_State.md`
  - Most recent `Session/Session_Records/Session_YYYY_MM_DD.md`
  - `Rules/House_Rules_and_Meta_Game/Meta_Game.md`

- **Writes To**:
  - `Session/Session_Records/Current_Game_State.md` (updates workflow position)

### Phase 1-8: Core Gameplay Loop
- **Reads From**:
  - `Campaign/Location_Records/[Current Location].md`
  - `Campaign/NPC_and_Monster_Records/[Relevant NPCs].md`
  - `Player_Character/Character_Records/[Character].md`
  - `Player_Character/Equipment_and_Resources/[Character]_Equipment.md`

- **Writes To**:
  - `Session/Session_Records/Current_Game_State.md` (updates as situation changes)

### Phase 9: Record Keeping
- **Reads From**:
  - Current state of all relevant files

- **Writes To**:
  - `Player_Character/Character_Records/[Character].md` (updates status)
  - `Player_Character/Equipment_and_Resources/[Character]_Equipment.md` (updates resources)
  - `Session/Session_Records/Current_Game_State.md` (comprehensive update)

## Combat Workflow Integration

### Phase 1-3: Combat Setup
- **Reads From**:
  - `Player_Character/Character_Records/[Character].md` (combat stats)
  - `Player_Character/Equipment_and_Resources/[Character]_Equipment.md` (weapons)
  - `Campaign/NPC_and_Monster_Records/[Relevant Monsters].md`
  - `Rules/House_Rules_and_Meta_Game/House_Rules.md` (combat rules)

- **Writes To**:
  - `Session/Session_Records/Current_Game_State.md` (updates initiative order)

### Phase 4-8: Combat Resolution
- **Reads From**:
  - `Player_Character/Character_Records/[Character].md` (abilities, skills)
  - `Rules/House_Rules_and_Meta_Game/Tables.md` (combat tables)

- **Writes To**:
  - `Session/Session_Records/Current_Game_State.md` (updates positions, effects)

### Phase 9-11: Combat Conclusion
- **Reads From**:
  - Current combat state

- **Writes To**:
  - `Player_Character/Character_Records/[Character].md` (updates HP)
  - `Player_Character/Equipment_and_Resources/[Character]_Equipment.md` (updates ammunition)
  - `Session/Session_Records/Current_Game_State.md` (updates combat outcome)

## Magic and Spellcasting Workflow Integration

### Phase 1-3: Spell Preparation and Components
- **Reads From**:
  - `Player_Character/Character_Records/[Character].md` (spellcasting abilities)
  - `Player_Character/Equipment_and_Resources/[Character]_Equipment.md` (spell components)
  - `Rules/House_Rules_and_Meta_Game/House_Rules.md` (magic rules)

- **Writes To**:
  - `Player_Character/Equipment_and_Resources/[Character]_Equipment.md` (updates prepared spells)

### Phase 4-7: Spell Casting and Effects
- **Reads From**:
  - `Player_Character/Equipment_and_Resources/[Character]_Equipment.md` (prepared spells)
  - `Rules/House_Rules_and_Meta_Game/Rule_Interpretations.md` (spell interpretations)

- **Writes To**:
  - `Session/Session_Records/Current_Game_State.md` (updates spell effects)
  - `Player_Character/Equipment_and_Resources/[Character]_Equipment.md` (marks spell as cast)

### Phase 8-9: Magic Items and Special Considerations
- **Reads From**:
  - `Player_Character/Equipment_and_Resources/[Character]_Equipment.md` (magic items)

- **Writes To**:
  - `Player_Character/Equipment_and_Resources/[Character]_Equipment.md` (updates charges)
  - `Session/Session_Records/Current_Game_State.md` (updates magic effects)

## Exploration Workflow Integration

### Phase 1-2: Time Management and Movement
- **Reads From**:
  - `Campaign/Location_Records/[Current Location].md` (maps)
  - `Player_Character/Character_Records/[Character].md` (movement rates)
  - `Player_Character/Equipment_and_Resources/[Character]_Equipment.md` (light sources)

- **Writes To**:
  - `Session/Session_Records/Current_Game_State.md` (updates time, position)

### Phase 3-4: Perception and Obstacles
- **Reads From**:
  - `Campaign/Location_Records/[Current Location].md` (hidden features)
  - `Player_Character/Character_Records/[Character].md` (perception abilities)

- **Writes To**:
  - `Campaign/Location_Records/[Current Location].md` (marks discovered features)
  - `Session/Session_Records/Current_Game_State.md` (updates discoveries)

### Phase 5-10: Encounters and Environment
- **Reads From**:
  - `Campaign/Location_Records/[Current Location].md` (encounter tables)
  - `Campaign/NPC_and_Monster_Records/[Potential Encounters].md`

- **Writes To**:
  - `Session/Session_Records/Current_Game_State.md` (updates encounters)
  - `Player_Character/Equipment_and_Resources/[Character]_Equipment.md` (updates resources)

## Character Advancement Workflow Integration

### Phase 1-2: Experience and Level Determination
- **Reads From**:
  - `Player_Character/Character_Records/[Character].md` (current XP)
  - `Rules/House_Rules_and_Meta_Game/Tables.md` (XP tables)
  - `Rules/House_Rules_and_Meta_Game/House_Rules.md` (advancement rules)

- **Writes To**:
  - `Player_Character/Character_Records/[Character].md` (updates XP, level)

### Phase 3-6: Character Improvements
- **Reads From**:
  - `Player_Character/Character_Records/[Character].md` (current abilities)
  - `Rules/House_Rules_and_Meta_Game/House_Rules.md` (advancement rules)

- **Writes To**:
  - `Player_Character/Character_Records/[Character].md` (updates abilities, skills)
  - `Player_Character/Equipment_and_Resources/[Character]_Equipment.md` (updates equipment options)

### Phase 7-10: Equipment and Social Advancement
- **Reads From**:
  - `Player_Character/Equipment_and_Resources/[Character]_Equipment.md` (current equipment)
  - `Campaign/NPC_and_Monster_Records/Henchmen_and_Followers.md` (if applicable)

- **Writes To**:
  - `Player_Character/Equipment_and_Resources/[Character]_Equipment.md` (updates equipment)
  - `Campaign/NPC_and_Monster_Records/Henchmen_and_Followers.md` (updates followers)

## Campaign Creation Workflow Integration

### Phase 1-2: World Creation
- **Reads From**:
  - Initial campaign concept

- **Writes To**:
  - `Campaign/Campaign_World_Records/Geography.md`
  - `Campaign/Campaign_World_Records/Political.md`
  - `Campaign/Campaign_World_Records/Cultural.md`
  - `Campaign/Campaign_World_Records/Religious.md`
  - `Campaign/Campaign_World_Records/Calendar.md`

### Phase 3: Location Creation
- **Reads From**:
  - `Campaign/Campaign_World_Records/Geography.md`

- **Writes To**:
  - `Campaign/Location_Records/[Location_Name].md` (for each location)

### Phase 4-6: NPCs and Monsters
- **Reads From**:
  - `Campaign/Campaign_World_Records/Political.md`
  - `Campaign/Location_Records/[Location_Name].md`

- **Writes To**:
  - `Campaign/NPC_and_Monster_Records/Important_NPCs.md`
  - `Campaign/NPC_and_Monster_Records/Monster_Groups.md`

### Phase 7-8: Campaign Details
- **Reads From**:
  - All previously created files

- **Writes To**:
  - `Rules/House_Rules_and_Meta_Game/Meta_Game.md` (campaign expectations)
  - `Session/Session_Records/Current_Game_State.md` (initial state)

## Character Generation Workflow Integration

### Phase 1-4: Basic Character Creation
- **Reads From**:
  - `Rules/House_Rules_and_Meta_Game/House_Rules.md` (character creation rules)
  - `Campaign/Campaign_World_Records/Cultural.md` (for background)

- **Writes To**:
  - `Player_Character/Character_Records/[Character].md` (creates file with basic info)

### Phase 5-8: Character Details
- **Reads From**:
  - `Rules/House_Rules_and_Meta_Game/Tables.md` (character tables)

- **Writes To**:
  - `Player_Character/Character_Records/[Character].md` (adds details)

### Phase 9: Equipment and Finalization
- **Reads From**:
  - `Rules/House_Rules_and_Meta_Game/House_Rules.md` (equipment rules)

- **Writes To**:
  - `Player_Character/Equipment_and_Resources/[Character]_Equipment.md` (creates file)
  - `Player_Character/Character_Records/[Character].md` (finalizes character)

## Session Preparation Workflow Integration

### Phase 1: Review Previous Session
- **Reads From**:
  - Most recent `Session/Session_Records/Session_YYYY_MM_DD.md`
  - `Session/Session_Records/Current_Game_State.md`

- **Writes To**:
  - No writes in this phase

### Phase 2-5: Adventure Preparation
- **Reads From**:
  - `Campaign/Location_Records/[Relevant_Locations].md`
  - `Campaign/NPC_and_Monster_Records/[Relevant_NPCs].md`

- **Writes To**:
  - `Campaign/Location_Records/[Location_Name].md` (updates as needed)
  - `Campaign/NPC_and_Monster_Records/[NPC_Name].md` (updates as needed)

### Phase 6-8: Session Planning
- **Reads From**:
  - `Rules/House_Rules_and_Meta_Game/Meta_Game.md` (session schedule)
  - `Player_Character/Character_Records/[Character].md` (all characters)

- **Writes To**:
  - No direct writes, but prepares materials for session

## Campaign Management Workflow Integration

### Phase 1-4: Session Documentation and World Evolution
- **Reads From**:
  - Session notes
  - `Session/Session_Records/Current_Game_State.md`

- **Writes To**:
  - `Session/Session_Records/Session_YYYY_MM_DD.md` (creates new file)
  - `Campaign/Campaign_World_Records/[Relevant_Files].md` (updates)
  - `Campaign/NPC_and_Monster_Records/[Relevant_NPCs].md` (updates)

### Phase 5-8: Experience and World Building
- **Reads From**:
  - `Session/Session_Records/Session_YYYY_MM_DD.md`
  - `Rules/House_Rules_and_Meta_Game/House_Rules.md` (XP rules)

- **Writes To**:
  - `Player_Character/Character_Records/[Character].md` (updates XP)
  - `Campaign/Location_Records/[Location_Name].md` (adds new locations)

### Phase 9-12: Record Keeping and Planning
- **Reads From**:
  - All relevant files

- **Writes To**:
  - `Session/Session_Records/Current_Game_State.md` (updates for next session)
  - `Rules/House_Rules_and_Meta_Game/Rule_Interpretations.md` (updates as needed)

## Special Situations Workflow Integration

### Phase 1-5: Special Rules Resolution
- **Reads From**:
  - `Player_Character/Character_Records/[Character].md` (abilities)
  - `Rules/House_Rules_and_Meta_Game/House_Rules.md` (special rules)
  - `Rules/House_Rules_and_Meta_Game/Rule_Interpretations.md` (clarifications)

- **Writes To**:
  - `Session/Session_Records/Current_Game_State.md` (updates results)

### Phase 6-10: Special Circumstances
- **Reads From**:
  - `Campaign/NPC_and_Monster_Records/Henchmen_and_Followers.md` (if relevant)
  - `Player_Character/Character_Records/[Character].md` (special abilities)

- **Writes To**:
  - `Player_Character/Character_Records/[Character].md` (updates conditions)
  - `Campaign/NPC_and_Monster_Records/Henchmen_and_Followers.md` (updates if relevant)

## Wilderness Adventure Workflow Integration

### Phase 1-4: Travel Preparation and Navigation
- **Reads From**:
  - `Campaign/Campaign_World_Records/Geography.md`
  - `Player_Character/Equipment_and_Resources/[Character]_Equipment.md` (supplies)

- **Writes To**:
  - `Session/Session_Records/Current_Game_State.md` (updates position, time)

### Phase 5-8: Wilderness Survival and Features
- **Reads From**:
  - `Campaign/Campaign_World_Records/Calendar.md` (weather)
  - `Player_Character/Equipment_and_Resources/[Character]_Equipment.md` (supplies)

- **Writes To**:
  - `Player_Character/Equipment_and_Resources/[Character]_Equipment.md` (updates supplies)
  - `Session/Session_Records/Current_Game_State.md` (updates conditions)

### Phase 9-12: Wilderness Encounters and Return
- **Reads From**:
  - `Campaign/Campaign_World_Records/Geography.md` (encounter tables)
  - `Campaign/NPC_and_Monster_Records/[Potential_Encounters].md`

- **Writes To**:
  - `Campaign/Campaign_World_Records/Geography.md` (updates discovered locations)
  - `Session/Session_Records/Current_Game_State.md` (updates encounters)

## Implementation Guidelines

1. **File Paths**: Use relative paths from the Game_Play directory
2. **Error Handling**: Check if files exist before reading
3. **File Creation**: Create parent directories if they don't exist
4. **Backups**: Consider creating backups before significant updates
5. **Formatting**: Maintain consistent markdown formatting
6. **References**: Use consistent naming for cross-references

## Example Integration Code

```python
# Example pseudocode for workflow integration

def combat_workflow_phase1():
    # Read character combat stats
    for character in party:
        character_file = f"Player_Character/Character_Records/{character}.md"
        character_data = read_file(character_file)
        equipment_file = f"Player_Character/Equipment_and_Resources/{character}_Equipment.md"
        equipment_data = read_file(equipment_file)
        
        # Process combat setup
        # ...
    
    # Read monster stats
    for monster in encounter:
        monster_file = f"Campaign/NPC_and_Monster_Records/{monster}.md"
        monster_data = read_file(monster_file)
        
        # Process monster setup
        # ...
    
    # Read house rules for combat
    rules_file = "Rules/House_Rules_and_Meta_Game/House_Rules.md"
    rules_data = read_file(rules_file)
    
    # Apply rules
    # ...
    
    # Update game state with initiative order
    game_state_file = "Session/Session_Records/Current_Game_State.md"
    game_state_data = read_file(game_state_file)
    game_state_data = update_initiative(game_state_data, initiative_order)
    write_file(game_state_file, game_state_data)
```

This structure provides a comprehensive system for integrating AD&D workflows with the game record system, ensuring consistent data management across all aspects of gameplay.
