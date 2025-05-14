# AD&D Campaign Details Record Instructions

## Overview
This document provides instructions for creating and maintaining campaign records in the AD&D game record system. Campaign information is divided into three main categories: Campaign World Records, Location Records, and NPC and Monster Records.

## Directory Structure

The campaign information is organized in the following directory structure:
```
Campaign/
├── Campaign_World_Records/
├── Location_Records/
└── NPC_and_Monster_Records/
```

## Campaign World Records

### File Organization
Campaign World Records should be organized by category:

1. **Geography.md** - Physical world features
2. **Political.md** - Kingdoms, factions, and conflicts
3. **Cultural.md** - Languages, customs, and racial relations
4. **Religious.md** - Deities, organizations, and practices
5. **Calendar.md** - Time tracking, seasons, and important dates

For complex campaigns, create subdirectories with multiple files:
```
Campaign_World_Records/
├── Geography/
│   ├── World_Map.md
│   ├── Continents.md
│   └── Major_Features.md
├── Political/
│   ├── Kingdoms.md
│   └── Factions.md
...etc.
```

### Geography File Format
```markdown
# Campaign World Geography

## World Overview
[Brief description of the world]

## Major Geographical Features

### Mountain Ranges
- **[Mountain Range Name]** - [Description]
- **[Mountain Range Name]** - [Description]

### Forests
- **[Forest Name]** - [Description]
- **[Forest Name]** - [Description]

### Rivers and Lakes
- **[River/Lake Name]** - [Description]
- **[River/Lake Name]** - [Description]

### Seas and Oceans
- **[Sea/Ocean Name]** - [Description]
- **[Sea/Ocean Name]** - [Description]

### Deserts and Wastelands
- **[Desert/Wasteland Name]** - [Description]
- **[Desert/Wasteland Name]** - [Description]

## Climate Zones
[Description of climate zones]

## Known Travel Routes
- **[Route Name]** - [Description]
- **[Route Name]** - [Description]

## Unexplored Territories
[Description of unexplored areas]
```

### Political File Format
```markdown
# Political Structure

## Kingdoms and Realms
- **[Kingdom Name]** - [Description, ruler, government type]
- **[Kingdom Name]** - [Description, ruler, government type]

## Power Groups and Factions
- **[Faction Name]** - [Description, goals, leadership]
- **[Faction Name]** - [Description, goals, leadership]

## Current Conflicts
- **[Conflict Name]** - [Description, involved parties, status]
- **[Conflict Name]** - [Description, involved parties, status]

## Laws and Customs
[Description of legal systems and enforcement]
```

## Location Records

### File Organization
Create separate files for each major location type:

1. **Dungeon_[Name].md** - For dungeon locations
2. **Settlement_[Name].md** - For towns, cities, and villages
3. **Wilderness_[Name].md** - For wilderness areas

For complex locations, create subdirectories:
```
Location_Records/
├── Dungeons/
│   ├── Caves_of_Chaos/
│   │   ├── Map.md
│   │   ├── Room_Contents.md
│   │   └── Traps.md
│   └── [Other Dungeon]/
├── Settlements/
│   ├── Homelet/
│   │   ├── Map.md
│   │   └── Key_Locations.md
│   └── [Other Settlement]/
...etc.
```

### Dungeon File Format
```markdown
# [Dungeon Name]

## Location Overview
[Brief description and background]

## Map
[ASCII map or reference to image file]

## Entrances
- **[Entrance A]** - [Description]
- **[Entrance B]** - [Description]

## Level 1 Rooms
1. **[Room Name]** - [Description, contents, monsters]
2. **[Room Name]** - [Description, contents, monsters]

## Level 2 Rooms
1. **[Room Name]** - [Description, contents, monsters]
2. **[Room Name]** - [Description, contents, monsters]

## Traps
- **[Trap Location]** - [Description, effects, detection/disarm]
- **[Trap Location]** - [Description, effects, detection/disarm]

## Treasure
- **[Treasure Location]** - [Description, value, protection]
- **[Treasure Location]** - [Description, value, protection]

## Special Features
- **[Feature Name]** - [Description, significance]
- **[Feature Name]** - [Description, significance]
```

### Settlement File Format
```markdown
# [Settlement Name]

## Overview
[Brief description, population, government]

## Map
[ASCII map or reference to image file]

## Key Locations
- **[Location Name]** - [Description, NPCs, significance]
- **[Location Name]** - [Description, NPCs, significance]

## Government and Law
[Description of local government and law enforcement]

## Services Available
- **Inns/Taverns**: [List with prices]
- **Shops**: [List with notable goods]
- **Temples**: [List with deities]
- **Other Services**: [List with prices]

## Notable NPCs
- **[NPC Name]** - [Brief description, role]
- **[NPC Name]** - [Brief description, role]

## Rumors and Hooks
- [Adventure hook or rumor]
- [Adventure hook or rumor]
```

## NPC and Monster Records

### File Organization
Create separate files or sections for different types of NPCs and monsters:

1. **Important_NPCs.md** - Key non-player characters
2. **Monster_Groups.md** - Monster types and groups
3. **Henchmen_and_Followers.md** - Character followers

For campaigns with many NPCs, create individual files for major characters:
```
NPC_and_Monster_Records/
├── Important_NPCs/
│   ├── Lord_Mayor_Bertram.md
│   └── Elaria_Moonshadow.md
├── Monster_Groups/
│   ├── Goblin_Tribe.md
│   └── Orc_Warband.md
...etc.
```

### NPC File Format
```markdown
# [NPC Name]

## Basic Information
- **Race/Class/Level**: [Details]
- **Alignment**: [Alignment]
- **Description**: [Physical appearance]
- **Personality**: [Personality traits]
- **Motivations**: [Goals and desires]
- **Location**: [Where they can be found]

## Statistics
- **Ability Scores**: [STR, DEX, CON, INT, WIS, CHA]
- **HP**: [Hit Points]
- **AC**: [Armor Class]
- **Attacks**: [Attack details]
- **Spells**: [Spell list if applicable]
- **Equipment**: [Notable items]

## Relationships
- **Allies**: [List of allies]
- **Enemies**: [List of enemies]
- **Affiliations**: [Organizations]

## Notes
[Additional information, secrets, plot hooks]
```

### Monster Group File Format
```markdown
# [Monster Group Name]

## Overview
[Brief description of the group]

## Typical Members
- **[Monster Type]** - [Number], [Basic stats]
- **[Monster Type]** - [Number], [Basic stats]

## Leadership
- **[Leader Name]** - [Description, special abilities]
- **[Lieutenant Name]** - [Description, special abilities]

## Lair
- **Location**: [Where they can be found]
- **Defenses**: [Traps, guards, etc.]
- **Treasure**: [Group treasure]

## Tactics
[Description of typical combat tactics]

## Motivations
[Goals and activities]
```

## Workflow Integration

### Campaign Creation Workflow
- Creates initial Campaign World Records during Phases 1-2
- Creates initial Location Records during Phase 3
- Creates initial NPC and Monster Records during Phases 4-6
- Links to these files should be established in the workflow documentation

### Session Preparation Workflow
- References Campaign World Records during Phase 1 (Review Previous Session)
- Updates Location Records during Phase 2 (Adventure Location Preparation)
- References and updates NPC and Monster Records during Phase 3 (Encounter Preparation)

### Exploration Workflow
- References Location Records during Phases 2-3 (Movement and Mapping, Perception and Discovery)
- Updates Location Records during Phase 2 (to mark explored areas)

### Combat Workflow
- References NPC and Monster Records during Phase 1 (Combat Initiation)
- Updates NPC and Monster Records during Phase 11 (Combat Conclusion) if significant NPCs are affected

### Campaign Management Workflow
- Updates Campaign World Records during Phase 2 (World Evolution)
- Updates Location Records during Phase 8 (World Building Development)
- Updates NPC and Monster Records during Phase 7 (NPC and Monster Management)

## Maintenance Guidelines

1. **Consistency**: Maintain consistent naming and formatting across all files
2. **Updates**: Update records after significant campaign events
3. **Versioning**: Consider keeping version history for major world changes
4. **References**: Include cross-references between related files
5. **Detail Level**: Adjust detail level based on importance to the campaign
6. **Images**: Include maps and images where helpful

## Special Considerations

### Large Campaigns
For very large campaigns, consider:
- Organizing by region
- Creating an index file for each category
- Using tags or keywords for searchability

### Multiple DMs
If multiple DMs run in the same world:
- Establish clear ownership of different regions
- Create a change log for world modifications
- Set up a review process for major changes

### Campaign Evolution
As the campaign progresses:
- Archive outdated information
- Update political situations based on player actions
- Expand details for areas becoming relevant to the story

This structure provides a comprehensive system for tracking all aspects of an AD&D campaign world while maintaining flexibility for different campaign styles and complexity levels.
