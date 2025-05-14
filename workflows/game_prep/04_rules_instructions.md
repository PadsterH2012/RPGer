# AD&D Rules and House Rules Instructions

## Overview
This document provides instructions for creating and maintaining rules records in the AD&D game record system. Rules records document house rules, rule interpretations, and meta-game information that affect gameplay.

## Directory Structure

Rules records are stored in the following directory:
```
Rules/
└── House_Rules_and_Meta_Game/
```

## File Types

Create the following files in the House_Rules_and_Meta_Game directory:

1. **House_Rules.md** - Modifications to standard AD&D rules
2. **Rule_Interpretations.md** - Clarifications of ambiguous rules
3. **Tables.md** - Quick reference tables for common rules
4. **Meta_Game.md** - Out-of-game information like scheduling and player preferences

For complex campaigns, consider creating subdirectories:
```
House_Rules_and_Meta_Game/
├── Combat/
│   ├── Critical_Hits.md
│   └── Initiative.md
├── Character/
│   ├── Ability_Scores.md
│   └── Classes.md
...etc.
```

## House Rules File Format

The House Rules file should follow this format:

```markdown
# House Rules

## Combat Rules Modifications

### [Rule Category]
- **[Rule Name]**: [Description of modification]
- **[Rule Name]**: [Description of modification]

### [Rule Category]
- **[Rule Name]**: [Description of modification]
- **[Rule Name]**: [Description of modification]

## Character Creation Rules

### [Rule Category]
- **[Rule Name]**: [Description of modification]
- **[Rule Name]**: [Description of modification]

### [Rule Category]
- **[Rule Name]**: [Description of modification]
- **[Rule Name]**: [Description of modification]

## Magic and Spellcasting

### [Rule Category]
- **[Rule Name]**: [Description of modification]
- **[Rule Name]**: [Description of modification]

### [Rule Category]
- **[Rule Name]**: [Description of modification]
- **[Rule Name]**: [Description of modification]

## Experience and Advancement

### [Rule Category]
- **[Rule Name]**: [Description of modification]
- **[Rule Name]**: [Description of modification]

### [Rule Category]
- **[Rule Name]**: [Description of modification]
- **[Rule Name]**: [Description of modification]

## Miscellaneous Rules

### [Rule Category]
- **[Rule Name]**: [Description of modification]
- **[Rule Name]**: [Description of modification]

### [Rule Category]
- **[Rule Name]**: [Description of modification]
- **[Rule Name]**: [Description of modification]

## Optional Rules in Use

- **[Optional Rule]**: [Source, brief description]
- **[Optional Rule]**: [Source, brief description]
- **[Optional Rule]**: [Source, brief description]
```

## Rule Interpretations File Format

The Rule Interpretations file should follow this format:

```markdown
# Rule Interpretations

## Combat Interpretations

### [Rule Name]
- **Question**: [Question about the rule]
- **Interpretation**: [How the rule is interpreted in this campaign]
- **Rationale**: [Reasoning behind the interpretation]
- **Source**: [Reference to rulebook page or external source]

### [Rule Name]
- **Question**: [Question about the rule]
- **Interpretation**: [How the rule is interpreted in this campaign]
- **Rationale**: [Reasoning behind the interpretation]
- **Source**: [Reference to rulebook page or external source]

## Spell Interpretations

### [Spell Name]
- **Question**: [Question about the spell]
- **Interpretation**: [How the spell is interpreted in this campaign]
- **Rationale**: [Reasoning behind the interpretation]
- **Source**: [Reference to rulebook page or external source]

### [Spell Name]
- **Question**: [Question about the spell]
- **Interpretation**: [How the spell is interpreted in this campaign]
- **Rationale**: [Reasoning behind the interpretation]
- **Source**: [Reference to rulebook page or external source]

## Class Ability Interpretations

### [Class Ability]
- **Question**: [Question about the ability]
- **Interpretation**: [How the ability is interpreted in this campaign]
- **Rationale**: [Reasoning behind the interpretation]
- **Source**: [Reference to rulebook page or external source]

### [Class Ability]
- **Question**: [Question about the ability]
- **Interpretation**: [How the ability is interpreted in this campaign]
- **Rationale**: [Reasoning behind the interpretation]
- **Source**: [Reference to rulebook page or external source]
```

## Tables File Format

The Tables file should follow this format:

```markdown
# Quick Reference Tables

## Combat Tables

### [Table Name]
```
[ASCII table or markdown table]
```

### [Table Name]
```
[ASCII table or markdown table]
```

## Saving Throw Tables

### [Table Name]
```
[ASCII table or markdown table]
```

### [Table Name]
```
[ASCII table or markdown table]
```

## Experience Tables

### [Table Name]
```
[ASCII table or markdown table]
```

### [Table Name]
```
[ASCII table or markdown table]
```

## Miscellaneous Tables

### [Table Name]
```
[ASCII table or markdown table]
```

### [Table Name]
```
[ASCII table or markdown table]
```
```

## Meta Game File Format

The Meta Game file should follow this format:

```markdown
# Meta Game Information

## Session Schedule
- **Regular Time**: [Day of week, time]
- **Location**: [Where sessions are held]
- **Duration**: [Typical session length]
- **Frequency**: [How often sessions are held]

## Player Information
- **[Player Name]**
  - Contact: [Email or phone]
  - Availability: [Any regular conflicts]
  - Preferences: [Play style, focus areas]

- **[Player Name]**
  - Contact: [Email or phone]
  - Availability: [Any regular conflicts]
  - Preferences: [Play style, focus areas]

## Absence Policy
- [How to handle player absences]
- [How to handle character absences]
- [Minimum players needed for a session]

## Table Etiquette
- [Expectations for player behavior]
- [Phone/device policy]
- [Food and drink policy]
- [Cross-talk policy]

## Campaign Expectations
- [Campaign tone and themes]
- [Content boundaries]
- [Player vs. character knowledge]
- [Retcon policy]
```

## Workflow Integration

### Character Generation Workflow
- References House_Rules.md during all phases
- References Tables.md for character creation tables

### Combat Workflow
- References House_Rules.md during all phases
- References Rule_Interpretations.md for combat rule clarifications
- References Tables.md for combat tables

### Magic and Spellcasting Workflow
- References House_Rules.md for spell modifications
- References Rule_Interpretations.md for spell clarifications

### Character Advancement Workflow
- References House_Rules.md for advancement modifications
- References Tables.md for experience tables

### Campaign Management Workflow
- References Meta_Game.md during Phase 10 (Player Management)
- Updates Rule_Interpretations.md during Phase 11 (Rules Management)

### Session Preparation Workflow
- References Meta_Game.md during Phase 12 (Session Planning)

## Maintenance Guidelines

1. **Consistency**: Ensure house rules are applied consistently
2. **Documentation**: Document new rule interpretations as they arise
3. **Player Agreement**: Ensure all players understand and agree to house rules
4. **Version Control**: Note when rules are changed and why
5. **Accessibility**: Make sure rules are easily accessible during play

## Special Considerations

### Rule Changes
When changing rules mid-campaign:
- Document the change clearly
- Note the effective date
- Explain the rationale
- Consider grandfathering existing characters

### Controversial Rules
For potentially controversial rules:
- Get player input before implementation
- Consider a trial period
- Have a clear process for revision
- Be willing to revert if the rule doesn't work

### Rules References
Include references to official sources:
- Page numbers in rulebooks
- Citations from official errata
- References to designer clarifications

### House Rule Categories
Common categories for house rules include:
- Character creation and advancement
- Combat mechanics
- Spell effects and limitations
- Class abilities
- Equipment and encumbrance
- Healing and recovery
- Death and dying

This structure provides a comprehensive system for tracking AD&D rules modifications and interpretations while maintaining clarity and consistency for all players.
