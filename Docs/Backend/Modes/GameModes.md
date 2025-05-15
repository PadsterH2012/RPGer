# RPGer Game Modes

The RPGer system supports multiple game modes that affect how the AI agents process player input and what functionality is available. This document defines each mode and how it should be used.

## Available Modes

### 1. Standard Mode (`standard`)

**Description:**
The default mode for normal gameplay. In this mode, the Dungeon Master Agent (DMA) processes player actions and coordinates with other specialized agents to provide a complete RPG experience.

**Behavior:**
- DMA accepts player actions and provides basic responses
- DMA forwards actions to specialized agents as needed
- All standard game mechanics are available

**Prompt Requirements:**
- DMA should use the standard DMA prompt format
- DMA responses should follow the "about to happen" format
- DMA should not describe scenes, provide options, or resolve actions

**Example:**
```
Player: "I attack the goblin with my sword"
DMA: "You prepare to strike at the goblin. [ACTION:COMBAT|TARGET:goblin|WEAPON:sword]"
```

### 2. Character Creation Mode (`create_character`)

**Description:**
A specialized mode for creating new player characters. In this mode, the Character Management Agent (CMA) guides the player through the character creation process step by step.

**Behavior:**
- CMA takes the lead in processing player input
- DMA acts as a facilitator, forwarding requests to the CMA
- The system walks the player through each step of character creation

**Prompt Requirements:**
- CMA should use a specialized character creation prompt
- DMA should recognize character creation commands and forward them to the CMA
- Responses should be instructional and guide the player through the process

**Example:**
```
Player: "I want to create a human fighter"
DMA: "The Character Management Agent will help you create your character."
CMA: "Let's create a human fighter. First, let's roll for your ability scores..."
```

### 3. Campaign Creation Mode (`create_campaign`)

**Description:**
A specialized mode for creating new campaigns. In this mode, the Campaign Manager Agent (CaMA) helps the player design a campaign setting, plot, and NPCs.

**Behavior:**
- CaMA takes the lead in processing player input
- DMA acts as a facilitator, forwarding requests to the CaMA
- The system guides the player through campaign creation steps

**Prompt Requirements:**
- CaMA should use a specialized campaign creation prompt
- DMA should recognize campaign creation commands and forward them to the CaMA
- Responses should help the player develop campaign elements

**Example:**
```
Player: "I want to create a desert-themed campaign"
DMA: "The Campaign Manager Agent will help you create your campaign."
CaMA: "A desert-themed campaign sounds interesting! Let's start by defining the major locations..."
```

### 4. Continue Campaign Mode (`continue_campaign`)

**Description:**
A mode for loading and continuing an existing campaign. This mode allows players to resume a previously saved campaign.

**Behavior:**
- System loads campaign data from storage
- DMA and other agents use the loaded campaign context
- Normal gameplay resumes from where it was left off

**Prompt Requirements:**
- All agents should incorporate the loaded campaign context
- DMA should acknowledge the continuation of the campaign
- Responses should maintain continuity with the previous session

**Example:**
```
Player: "Continue the Forest of Shadows campaign"
System: "Loading the Forest of Shadows campaign..."
DMA: "Welcome back to the Forest of Shadows. When we last left off, your party had just discovered the hidden entrance to the ancient temple..."
```

### 5. Random Encounter Mode (`random_encounter`)

**Description:**
A mode for generating and playing through random encounters. This is useful for one-off sessions or when players want a quick gameplay experience.

**Behavior:**
- System generates a random encounter appropriate for the party
- DMA introduces the encounter and manages the gameplay
- Specialized agents handle their respective aspects of the encounter

**Prompt Requirements:**
- DMA should introduce the randomly generated encounter
- Combat Resolution Agent should be prepared to handle combat
- Responses should focus on the immediate encounter

**Example:**
```
Player: "Generate a random encounter"
System: "Generating random encounter..."
DMA: "As you travel along the forest path, you suddenly hear rustling in the bushes. Three goblins leap out with weapons drawn! What do you do?"
```

## Mode Selection and Switching

### Setting the Initial Mode

The initial mode is set when starting the game:

```javascript
// Client-side
socket.emit('start_game', { mode: 'standard' });
```

### Switching Modes

Currently, the system does not support switching modes during gameplay. To change modes, the game must be restarted with the new mode:

1. Stop the current game
2. Start a new game with the desired mode

## Mode-Specific Prompt Handling

Each mode may require different prompt handling:

1. **Standard Mode**: Uses the standard DMA prompt with "about to happen" response format
2. **Character Creation Mode**: Uses specialized CMA prompts for character creation
3. **Campaign Creation Mode**: Uses specialized CaMA prompts for campaign creation
4. **Continue Campaign Mode**: Uses standard prompts but with loaded campaign context
5. **Random Encounter Mode**: Uses standard prompts with focus on the generated encounter

## Future Improvements

1. **Mode Switching**: Add support for switching modes during gameplay
2. **Mode-Specific UI**: Customize the UI based on the current mode
3. **Mode-Specific Prompts**: Create dedicated prompt files for each mode
4. **Mode Persistence**: Save and restore the current mode when reloading the application
