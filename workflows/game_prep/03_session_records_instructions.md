# AD&D Session Records Instructions

## Overview
This document provides instructions for creating and maintaining session records in the AD&D game record system. Session records track what happens during each play session and maintain the current state of the game between sessions.

## Directory Structure

Session records are stored in the following directory:
```
Session/
└── Session_Records/
```

## File Types

Create two types of files in the Session_Records directory:

1. **Session_YYYY_MM_DD.md** - One file per gaming session
2. **Current_Game_State.md** - A single file that is updated after each session

## Session Record File Format

Each session record file should follow this format:

```markdown
# Session: [Date]

## Session Information
- **Date**: [Real-world date]
- **Location**: [Where the session was held]
- **DM**: [DM name]
- **Start Time**: [Start time]
- **End Time**: [End time]

## Players Present
- [Player Name] ([Character Name], [Race] [Class] [Level])
- [Player Name] ([Character Name], [Race] [Class] [Level])

## Players Absent
- [Player Name] ([Character Name]) - [Reason for absence]

## Session Summary
[A paragraph or two summarizing the key events of the session]

## Key Decisions
1. [Important decision made by the party]
2. [Important decision made by the party]

## Combat Encounters
1. **[Encounter Name]**
   - [Enemies faced]
   - Initiative: [Initiative order]
   - Outcome: [Result of combat]

2. **[Encounter Name]**
   - [Enemies faced]
   - Initiative: [Initiative order]
   - Outcome: [Result of combat]

## Discoveries
- [Important location discovered]
- [Important item found]
- [Important information learned]
- [Important NPC met]

## NPC Interactions
- **[NPC Name]**: [Summary of interaction]
- **[NPC Name]**: [Summary of interaction]

## Treasure Found
- [Gold, gems, jewelry]
- [Magic items]
- [Other valuable items]

## Experience Awarded
- Monster XP: [Amount]
- Treasure XP: [Amount]
- Roleplay/Quest XP: [Amount]
- Total: [Total amount] ([Amount per character])

## Current Game State
- **Location**: [Where the party ended the session]
- **Time**: [In-game time at end of session]
- **Party Condition**: [HP, spell slots, conditions]
- **Resources Used**: [Consumables, charges, etc.]

## Next Session Plans
- [Likely next steps for the party]
- [Pending decisions]
- [Upcoming events]

## DM Notes
- [Notes for the DM about future preparation]
- [Thoughts on pacing or balance]
- [Ideas for future development]
```

## Current Game State File Format

The Current Game State file should follow this format:

```markdown
# Current Game State

## Active Workflow Information
- **Current Workflow**: [Workflow name]
- **Current Phase**: [Phase number and name]
- **Current Step**: [Step number and description]
- **Last Completed Workflow**: [Workflow name]
- **Interrupted Workflows**: [Any workflows that were interrupted]

## Time and Location
- **Current In-Game Date**: [Date]
- **Current In-Game Time**: [Time]
- **Current Location**: [Location name and description]
- **Weather Conditions**: [Current weather]
- **Moon Phase**: [Current moon phase]
- **Light Conditions**: [Current lighting]

## Party Status

### [Character Name] ([Race] [Class] [Level])
- **Current HP**: [Current]/[Maximum]
- **Spell Effects**: [Active spells affecting character]
- **Conditions**: [Any conditions affecting character]
- **Resources Used**: [Consumables used, charges expended]
- **Position**: [Where character is in the scene]

### [Character Name] ([Race] [Class] [Level])
- **Current HP**: [Current]/[Maximum]
- **Spell Effects**: [Active spells affecting character]
- **Conditions**: [Any conditions affecting character]
- **Resources Used**: [Consumables used, charges expended]
- **Position**: [Where character is in the scene]

## Environment Description
[Detailed description of the current environment]

## Active NPCs

### Present in Scene
- **[NPC Name]**: [Brief description, current activity]
- **[NPC Name]**: [Brief description, current activity]

### Relevant but Not Present
- **[NPC Name]**: [Location, relevance to current situation]
- **[NPC Name]**: [Location, relevance to current situation]

## Active Quests and Goals
1. **[Quest Name]**
   - Status: [In progress/Complete/Failed]
   - Next Step: [What needs to be done next]

2. **[Quest Name]**
   - Status: [In progress/Complete/Failed]
   - Next Step: [What needs to be done next]

## Immediate Options
1. [Option available to the party]
2. [Option available to the party]
3. [Option available to the party]

## Recent Events Summary
[Brief summary of recent events leading to current situation]

## Pending Decisions
1. [Decision the party needs to make]
2. [Decision the party needs to make]
```

## Workflow Integration

### Interaction Workflow
- References Current_Game_State.md during Phase 0 (Session Initialization)
- Updates Current_Game_State.md during Phase 9 (Record Keeping)

### Session Preparation Workflow
- References the most recent Session_YYYY_MM_DD.md during Phase 1 (Review Previous Session)
- References Current_Game_State.md during Phase 1 (Review Previous Session)

### Combat Workflow
- References Current_Game_State.md during Phase 1 (Combat Initiation)
- Updates Current_Game_State.md during Phase 11 (Combat Conclusion)

### Exploration Workflow
- References Current_Game_State.md during Phase 1 (Time Management)
- Updates Current_Game_State.md during Phase 9 (Record Keeping)

### Campaign Management Workflow
- Creates new Session_YYYY_MM_DD.md file during Phase 1 (Session Documentation)
- Updates Current_Game_State.md during Phase 12 (Session Planning)

## Recording Guidelines

### During the Session
1. **Take Notes**: Keep brief notes during play about:
   - Key decisions and actions
   - Combat results
   - NPC interactions
   - Discoveries
   - Treasure found

2. **Track Resources**: Note consumption of:
   - Hit points
   - Spell slots
   - Potions and scrolls
   - Ammunition
   - Other consumables

3. **Record Time**: Track the passage of in-game time

### After the Session
1. **Create Session Record**: Create a new Session_YYYY_MM_DD.md file
2. **Update Game State**: Update the Current_Game_State.md file
3. **Update Character Records**: Ensure character records reflect current status
4. **Update Campaign Records**: Update any campaign records affected by the session

## Maintenance Guidelines

1. **Consistency**: Use consistent formatting across all session records
2. **Completeness**: Ensure all important events are recorded
3. **Accuracy**: Double-check HP, spell slots, and resource tracking
4. **Timeliness**: Create session records immediately after the session
5. **Backup**: Back up session records regularly

## Special Considerations

### Long Sessions
For very long sessions:
- Consider breaking the record into multiple parts
- Use clear headings to separate major segments
- Focus on the most important events

### Multiple DMs
If multiple DMs run sessions:
- Establish a consistent format
- Ensure all DMs have access to previous records
- Maintain a single Current_Game_State.md file

### Campaign Arcs
Consider creating summary files for major campaign arcs:
- Create Arc_Summary_[Name].md files
- Include key events, decisions, and outcomes
- Reference individual session files

### Player Recaps
Consider creating player-facing recaps:
- Omit DM notes and future plans
- Focus on what characters would remember
- Include only information known to the characters

This structure provides a comprehensive system for tracking AD&D sessions while maintaining the current game state for seamless continuation between sessions.
