# AD&D Player Character Record Instructions

## Overview
This document provides instructions for creating and maintaining player character records in the AD&D game record system. Character information is divided into two main categories: Character Records (basic information, abilities, skills) and Equipment and Resources (inventory, weapons, magic items).

## File Structure

For each player character, create two files:
1. `Player_Character/Character_Records/Character_Name.md`
2. `Player_Character/Equipment_and_Resources/Character_Name_Equipment.md`

## Character Records File Format

The Character Records file should contain the following sections:

```markdown
# Character Name

## Basic Character Information
- **Race**: [Race]
- **Class**: [Class]
- **Level**: [Level]
- **Alignment**: [Alignment]
- **Age**: [Age]
- **Gender**: [Gender]
- **Height**: [Height]
- **Weight**: [Weight]
- **Physical Description**: [Brief description]
- **Background**: [Brief background story]

## Ability Scores
- **Strength**: [Score] ([Modifier])
- **Intelligence**: [Score] ([Modifier])
- **Wisdom**: [Score] ([Modifier])
- **Dexterity**: [Score] ([Modifier])
- **Constitution**: [Score] ([Modifier])
- **Charisma**: [Score] ([Modifier])

## Combat Statistics
- **Hit Points**: [Current]/[Maximum]
- **Armor Class**: [AC]
- **THAC0**: [THAC0]
- **Saving Throws**:
  - Paralyzation, Poison, Death Magic: [Value]
  - Rod, Staff, Wand: [Value]
  - Petrification, Polymorph: [Value]
  - Breath Weapon: [Value]
  - Spell: [Value]
- **Initiative Modifier**: [Modifier]
- **Weapon Proficiencies**: [List]
- **Combat Bonuses**: [List]

## Skills and Abilities
- **Racial Abilities**: [List]
- **Class Abilities**: [List]
- **Thief Skills** (if applicable): [Percentages]
- **Languages Known**: [List]

## Experience and Advancement
- **Experience Points**: [Current XP]
- **Experience for Next Level**: [XP needed]
- **Training Status**: [Status]
- **Level Advancement Progress**: [Percentage or description]
```

## Equipment and Resources File Format

The Equipment and Resources file should contain the following sections:

```markdown
# Character Name - Equipment and Resources

## Weapons and Armor
- **Weapons Carried**: [List with basic stats]
- **Weapon Damage**: [Detailed damage information]
- **Weapon Speed Factor**: [List]
- **Weapon Range**: [List for ranged weapons]
- **Armor Worn**: [Description and AC]
- **Shield Used**: [Description and AC modifier]

## Inventory
- **Backpack Contents**: [List]
- **Pouches/Containers**: [List by container]
- **Worn Items**: [List]
- **Currency**: [GP, SP, CP amounts]
- **Gems and Jewelry**: [List with values]
- **Encumbrance Total**: [Weight and category]

## Magic Items
- **Magic Weapons**: [List with properties]
- **Magic Armor/Protection**: [List with properties]
- **Potions**: [List with effects]
- **Scrolls**: [List with spells]
- **Wands/Staves/Rods**: [List with properties]
- **Rings**: [List with properties]
- **Miscellaneous Magic**: [List with properties]
- **Charges Remaining**: [List items with charges]
- **Cursed Item Effects**: [List if any]

## Spellcasting Resources (if applicable)
- **Spellbook Contents**: [List of spells by level]
- **Spells Known**: [List]
- **Spells Memorized**: [List currently prepared spells]
- **Spell Components**: [List special components]
- **Spell Research Notes**: [Any ongoing research]

## Consumables
- **Food Rations**: [Amount]
- **Water Supply**: [Amount]
- **Torches/Light Sources**: [Amount]
- **Oil Flasks**: [Amount]
- **Rope Length**: [Amount]
- **Ammunition**: [Amount by type]

## Mount and Equipment (if applicable)
- **Mount**: [Description]
- **Saddlebags**: [Contents]
- **Mount Equipment**: [List]

## Property and Investments (if applicable)
- **Property Owned**: [Description]
- **Investments**: [Description]
- **Debts**: [Description]
- **Regular Expenses**: [List]
```

## Workflow Integration

### Character Generation Workflow
- Creates initial Character Records file during Phase 9 (Final Touches)
- Creates initial Equipment and Resources file during Phase 6 (Equipment and Money)
- Links to these files should be established in the workflow documentation

### Character Advancement Workflow
- Updates Character Records file during all phases
- Updates Experience and Advancement section during Phase 1 (Experience Point Calculation)
- Updates Combat Statistics during Phase 4 (Combat Advancement)
- Updates Skills and Abilities during Phase 5 (Class Ability Advancement)

### Combat Workflow
- References Character Records for combat statistics during Phase 1-3
- Updates current Hit Points in Character Records during Phase 9 (Combat Status Updates)
- Updates ammunition and consumables in Equipment and Resources during Phase 9

### Magic and Spellcasting Workflow
- References Spellcasting Resources section during Phase 1-2
- Updates Spells Memorized during Phase 2 (Spell Preparation)
- Updates Spell Components during Phase 3 (Spell Components)
- Updates charges on magic items during Phase 8 (Magic Item Use)

### Exploration Workflow
- References Equipment and Resources for light sources during Phase 1 (Time Management)
- Updates consumables during Phase 7 (Resource Management)

### Session Workflow
- Updates current Hit Points, spell slots, and consumables at end of session
- Records any new equipment or items acquired

## Maintenance Guidelines

1. **Current Values**: Always maintain current values for hit points, experience, and consumable resources
2. **Version History**: Consider keeping a version history for significant character changes
3. **Backup**: Back up character files regularly, especially after level advancement
4. **Formatting**: Maintain consistent formatting for readability
5. **Updating**: Update both files whenever relevant changes occur in gameplay
6. **Retirement**: Move files for retired characters to an Archive directory

## Special Cases

### Multi-class Characters
- List all classes with respective levels
- Track experience for each class separately
- Note any special multi-class rules that apply

### Dual-class Characters
- Note original class and new class
- Track restrictions on original class abilities
- Note when character can use both class abilities

### Henchmen and Followers
- Create simplified versions of these files for important henchmen
- For groups of followers, create a single summary file

This structure provides a comprehensive system for tracking all aspects of AD&D player characters while maintaining flexibility for different character types and campaign styles.
