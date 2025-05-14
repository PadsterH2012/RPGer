# Spell Descriptions Format

*Extracted from the AD&D 1st Edition Player's Handbook*

## Overview

Spell descriptions in AD&D follow a standardized format that provides all the necessary information for casting and adjudicating spells. Understanding this format is essential for both players and Dungeon Masters to properly implement spells in the game.

## Standard Format Elements

Each spell description contains the following elements, typically in this order:

### 1. Spell Name

The official name of the spell, sometimes including the name of the wizard who created it (e.g., Tenser's Floating Disc, Bigby's Crushing Hand).

### 2. Level Information

Indicates which class can cast the spell and at what level:
- For single-class spells: "Level: X Magic-User/Cleric/Druid/Illusionist Spell"
- For multi-class spells: "Level: X Magic-User, Y Illusionist Spell"

### 3. Components

Lists the components required to cast the spell:
- **V**: Verbal component (spoken words or sounds)
- **S**: Somatic component (gestures and movements)
- **M**: Material component (physical items)

Example: "Components: V, S, M"

### 4. Range

The maximum distance from the caster at which the spell can be targeted:
- Measured in inches (1" = 10 feet indoors, 10 yards outdoors)
- "Touch" requires physical contact with the target
- "0" indicates the spell affects only the caster
- Some spells have variable ranges based on caster level

Example: "Range: 6" + 1"/level"

### 5. Duration

How long the spell's effects last:
- Measured in segments, rounds, turns, hours, days, etc.
- "Instantaneous" means the effect happens and ends immediately
- "Permanent" means the effect lasts until dispelled
- Some durations depend on caster level

Example: "Duration: 1 round/level"

### 6. Casting Time

How long it takes to cast the spell:
- Measured in segments (10 segments = 1 round)
- Affects when the spell takes effect in combat
- Longer casting times increase vulnerability during casting

Example: "Casting Time: 3 segments"

### 7. Saving Throw

Whether targets get a chance to resist or reduce the spell's effects:
- "None" means no saving throw is allowed
- "Negates" means a successful save completely negates the effect
- "½" means a successful save reduces damage by half
- May specify which saving throw category applies

Example: "Saving Throw: ½"

### 8. Area of Effect

The space or targets affected by the spell:
- May be a specific volume (cube, sphere, cone)
- May be a number of creatures or objects
- May be a specific area (radius, line, etc.)

Example: "Area of Effect: 20' radius sphere"

### 9. Explanation

A detailed description of what the spell does, including:
- Specific effects and mechanics
- How the spell interacts with other spells or situations
- Any limitations or special cases
- How the spell scales with caster level (if applicable)

### 10. Material Components

A detailed description of any material components required:
- What specific items are needed
- Whether they are consumed in casting
- Any preparation required
- Monetary value if significant

## Example Spell Description

```
Magic Missile
Level: 1st Level Magic-User Spell
Components: V, S
Range: 6" + 1"/level
Duration: Instantaneous
Casting Time: 1 segment
Saving Throw: None
Area of Effect: 1 or more creatures in a 10' square area

Explanation: This spell creates a missile of magical energy that unerringly strikes its target, dealing 1d4+1 points of damage. For every two levels of experience, the magic-user gains an additional missile (2 missiles at 3rd level, 3 missiles at 5th level, etc.) to a maximum of 5 missiles at 9th level. Multiple missiles can be directed at a single target or at different targets, but all missiles must be aimed at targets within a 10' square area.
```

## Special Format Considerations

### Reversible Spells

Some spells can be cast in reverse, creating an opposite effect:
- Indicated by "(Reversible)" after the spell name
- Both versions are learned when the spell is learned
- Clerics must be of appropriate alignment to use certain versions
- Reverse versions may have different material components

Example:
```
Cure Light Wounds (Reversible)
...
Explanation: This spell cures 1d8 points of damage in a living creature. The reverse, Cause Light Wounds, inflicts 1d8 points of damage.
```

### Variable Effects by Class

Some spells have different effects depending on the caster's class:
- Indicated in the level information and explanation
- May have different ranges, durations, or effects
- Material components may vary by class

### Progressive Effects

Spells that increase in power with caster level:
- Clearly stated in the explanation section
- May affect damage, duration, range, or number of targets
- Usually has a maximum effect level

Example: "The spell creates one missile at 1st level, two at 3rd level, three at 5th level, etc."

### Concentration Requirements

Spells that require ongoing concentration:
- Specified in the duration section
- Explanation details what breaks concentration
- May limit the caster's other actions

Example: "Duration: Concentration, maximum 1 round/level"

## Reading Spell Descriptions

### Range Interpretation

- Indoor/Dungeon: 1" = 10 feet
- Outdoor: 1" = 10 yards
- Some spells specify different indoor and outdoor ranges

### Duration Timing

- Segment: 1/10 of a round (6 seconds)
- Round: 1 minute
- Turn: 10 minutes
- Hour/Day/etc.: Standard time measurements

### Area of Effect Measurements

- Linear measurements (10', 30', etc.) represent actual distances
- Volume measurements (cubic feet, etc.) represent total space affected
- Radius/diameter measurements represent distance from center point

## Special Types of Spells

### Detection Spells

Spells that reveal information:
- Usually have a specific detection range
- May require concentration
- Often have a narrow focus (detect magic, detect evil, etc.)

### Divination Spells

Spells that provide knowledge:
- Often have material components related to the information sought
- May have percentage chance of success
- Higher level versions typically provide more detailed information

### Conjuration/Summoning Spells

Spells that bring creatures or objects:
- Specify what can be summoned
- Detail the control the caster has over summoned entities
- Often have expensive or rare material components

### Enchantment/Charm Spells

Spells that affect minds:
- Usually allow saving throws
- Specify the exact nature of control or influence
- Often have duration based on target's Intelligence

### Illusion/Phantasm Spells

Spells that create false sensory impressions:
- Detail which senses are affected
- Explain how interaction affects the illusion
- May allow saving throws for disbelief

## Spell Preparation and Use

### Preparing Spells

- Magic-users and illusionists must study their spellbooks
- Clerics and druids must pray or meditate
- Preparation time varies by class and spell level
- Specific spells must be chosen during preparation

### Casting Prepared Spells

- Components must be available
- Casting time must be observed
- Concentration must be maintained
- Line of sight to target is typically required

### Spell Failure Conditions

- Taking damage during casting
- Failed concentration check
- Missing or incorrect components
- Target out of range or not visible

## Interpreting Ambiguities

When spell descriptions contain ambiguities or edge cases:

### General Principles

1. The Dungeon Master has final authority on spell interpretation
2. Consider the spell's level and intended power
3. Compare with similar spells for precedent
4. Balance game impact against literal interpretation

### Common Ambiguities

- Interaction between multiple magical effects
- Whether a spell affects magical creatures or items
- Precise definitions of terms like "creature," "object," etc.
- How spells function in unusual environments

## Spell Description Terminology

Understanding specific terminology used in spell descriptions:

### "Up To"

Indicates a maximum value that the caster can choose not to use fully:
- "Up to 1 creature per level" means the caster can affect fewer creatures if desired
- "Range: Up to 10" + 1"/level" means the caster can target something closer

### "Per Level"

Refers to the caster's experience level:
- "1d6 damage per level" for a 5th level caster means 5d6 damage
- "Duration: 1 round per level" for a 7th level caster means 7 rounds

### "At Will"

Indicates an effect the caster can control without additional casting:
- "The caster can extinguish the light at will"
- "The invisible servant can be dismissed at will"
