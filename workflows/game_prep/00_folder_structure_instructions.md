# AD&D Game Record System - Folder Structure Instructions

## Overview
This document provides instructions for creating and maintaining the folder structure for AD&D game records. This structure organizes all game information in a logical hierarchy that supports the various workflows used during gameplay.

## Base Directory Structure

Create the following base directory structure:

```
Game_Play/
├── Campaign/
│   ├── Campaign_World_Records/
│   ├── Location_Records/
│   └── NPC_and_Monster_Records/
├── Player_Character/
│   ├── Character_Records/
│   └── Equipment_and_Resources/
├── Rules/
│   └── House_Rules_and_Meta_Game/
└── Session/
    └── Session_Records/
```

## Creation Instructions

1. Create the base directory structure using the following command:

```bash
mkdir -p Game_Play/{Campaign/{Campaign_World_Records,Location_Records,NPC_and_Monster_Records},Player_Character/{Character_Records,Equipment_and_Resources},Rules/House_Rules_and_Meta_Game,Session/Session_Records}
```

2. Verify the structure was created correctly:

```bash
find Game_Play -type d | sort
```

## Directory Purposes

### Campaign/
Contains all information related to the game world, locations, and NPCs.

- **Campaign_World_Records/**: World-level information including geography, politics, culture, religion, and time.
  - Create subdirectories as needed for complex campaigns (Geography/, Political/, Cultural/, etc.)

- **Location_Records/**: Information about specific locations in the game world.
  - For dungeons, create a separate file for each dungeon
  - For complex dungeons, create subdirectories with multiple files (Maps/, Room_Contents/, etc.)
  - For settlements, create a file for each major settlement

- **NPC_and_Monster_Records/**: Information about NPCs and monster groups.
  - Create separate files for important individual NPCs
  - Create files for monster groups by type or location
  - Create files for henchmen and followers

### Player_Character/
Contains all information related to player characters.

- **Character_Records/**: Basic character information, abilities, and skills.
  - Create one file per character named Character_Name.md

- **Equipment_and_Resources/**: Character equipment, inventory, and resources.
  - Create one file per character named Character_Name_Equipment.md

### Rules/
Contains house rules and meta-game information.

- **House_Rules_and_Meta_Game/**: Modified rules, tables, and meta-game information.
  - Create separate files for different categories of house rules
  - Create files for player preferences and scheduling

### Session/
Contains session records and current game state.

- **Session_Records/**: Detailed session logs and current game state.
  - Create one file per session named Session_YYYY_MM_DD.md
  - Maintain a Current_Game_State.md file that is updated after each session

## Naming Conventions

1. **Directories**: Use underscore (_) to separate words in directory names
2. **Files**: Use underscore (_) to separate words in file names
3. **Character Files**: Start with character name (e.g., Thoric_Ironhammer.md)
4. **Session Files**: Start with "Session_" followed by date in YYYY_MM_DD format
5. **Location Files**: Start with location type followed by name (e.g., Dungeon_Caves_of_Chaos.md)

## File Extensions

- Use .md (Markdown) for all text files
- Use .jpg or .png for images
- Use .pdf for reference documents

## Workflow Integration

- Each AD&D workflow should reference this structure when creating or updating files
- Workflows should specify the exact file path when referencing a file
- When a workflow creates a new file, it should follow the naming conventions above
- When a workflow updates a file, it should maintain the existing structure and formatting

## Maintenance

- Periodically archive completed adventures to an Archives/ directory
- Maintain consistent formatting within files
- Update the Current_Game_State.md file after each session
- Back up the entire Game_Play/ directory regularly

## Special Considerations

- For very large campaigns, consider creating subdirectories by region or adventure
- For campaigns with multiple player groups, create a separate Player_Group/ directory for each
- For historical records, consider creating a Campaign_History/ directory

This structure is designed to be flexible and can be expanded as needed while maintaining the core organization.
