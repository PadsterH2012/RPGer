# AI Agent System

## Overview

The RPGer application uses a multi-agent AI system to manage different aspects of the role-playing game experience. Each agent is specialized for a specific domain of the game, allowing for modular, focused AI processing that creates a rich and responsive game environment.

This document describes the roles, responsibilities, and interactions of the eight specialized AI agents that power the RPGer system.

## Agent Types and Roles

The RPGer system employs eight specialized AI agents, each with a distinct role in the game experience:

| Abbreviation | Full Name | Primary Role |
|--------------|-----------|--------------|
| DMA | Dungeon Master Agent | Orchestrates the overall game experience and player interactions |
| CRA | Combat Resolution Agent | Manages combat encounters and tactical gameplay |
| CMA | Character Management Agent | Handles character creation, advancement, and management |
| NEA | NPC & Encounter Agent | Controls non-player characters and generates encounters |
| EEA | Exploration Engine Agent | Facilitates world exploration and discovery |
| WEA | World & Environment Agent | Manages world building, settings, and environmental factors |
| MSA | Magic System Agent | Handles magical effects, spells, and magical items |
| CaMA | Campaign Manager Agent | Oversees campaign progression and long-term narrative |

## Agent Responsibilities and Restrictions

### DMA (Dungeon Master Agent)

**Responsibilities:**
- Primary interface between players and the game world
- Narrates game events and describes scenes
- Interprets player actions and determines outcomes
- Coordinates with other agents to create a cohesive experience
- Maintains game flow and pacing
- Enforces game rules and adjudicates edge cases
- Tracks game state and session progress

**Restrictions:**
- Must maintain narrative consistency
- Cannot contradict established world facts
- Must follow the game rules while allowing for creative interpretation
- Should balance challenge and player enjoyment
- Must respect player agency and choices

### CRA (Combat Resolution Agent)

**Responsibilities:**
- Manages initiative and turn order in combat
- Resolves attack rolls, damage, and combat effects
- Controls enemy tactics and decision-making
- Tracks combat status effects and conditions
- Provides dynamic combat narration
- Balances encounter difficulty in real-time
- Handles special combat maneuvers and abilities

**Restrictions:**
- Must follow combat rules precisely
- Cannot arbitrarily change enemy stats mid-combat
- Should provide appropriate challenge without being unfair
- Must maintain combat pacing to keep players engaged
- Cannot reveal hidden enemy information inappropriately

### CMA (Character Management Agent)

**Responsibilities:**
- Assists with character creation and advancement
- Validates character sheets and rule compliance
- Tracks character resources, equipment, and abilities
- Manages character progression and level-ups
- Handles skill checks and ability tests
- Provides character-specific rule guidance
- Maintains character history and development

**Restrictions:**
- Must enforce character creation and advancement rules
- Cannot modify character attributes without player consent
- Should provide options without making decisions for players
- Must maintain accurate tracking of character resources
- Cannot reveal information characters wouldn't know

### NEA (NPC & Encounter Agent)

**Responsibilities:**
- Generates and controls non-player characters
- Creates consistent NPC personalities and behaviors
- Manages NPC dialogue and interactions
- Designs balanced and thematic encounters
- Adapts NPC reactions based on player choices
- Tracks NPC relationships and motivations
- Generates random encounters appropriate to context

**Restrictions:**
- Must maintain NPC consistency across sessions
- Cannot arbitrarily change NPC attitudes without reason
- Should create encounters appropriate to the area and difficulty
- Must respect established NPC relationships and history
- Cannot make NPCs omniscient about player actions

### EEA (Exploration Engine Agent)

**Responsibilities:**
- Facilitates world exploration and discovery
- Manages travel mechanics and navigation
- Handles environmental challenges and obstacles
- Controls discovery of hidden features and secrets
- Tracks exploration progress and mapped areas
- Generates exploration-based encounters
- Manages resource consumption during travel

**Restrictions:**
- Must maintain geographical consistency
- Cannot arbitrarily change established locations
- Should balance discovery rate to maintain interest
- Must respect player navigation choices
- Cannot reveal hidden areas without appropriate checks

### WEA (World & Environment Agent)

**Responsibilities:**
- Manages world building and setting details
- Controls weather patterns and environmental conditions
- Generates terrain features and natural phenomena
- Maintains consistency in world description
- Creates immersive environmental descriptions
- Tracks time passage and seasonal changes
- Handles environmental hazards and effects

**Restrictions:**
- Must maintain world consistency
- Cannot contradict established world facts
- Should develop the world gradually to avoid overwhelming players
- Must ensure environmental challenges are fair
- Cannot arbitrarily change established environments

### MSA (Magic System Agent)

**Responsibilities:**
- Interprets and resolves magical effects
- Manages spell casting and magical abilities
- Controls magical item properties and effects
- Handles magical research and development
- Creates consistent magical phenomena
- Tracks spell components and magical resources
- Manages magical side effects and consequences

**Restrictions:**
- Must follow established magic system rules
- Cannot arbitrarily change how spells function
- Should maintain balance in magical effects
- Must ensure magical challenges are fair
- Cannot reveal hidden magical information inappropriately

### CaMA (Campaign Manager Agent)

**Responsibilities:**
- Oversees campaign progression and story arcs
- Manages long-term narrative development
- Tracks campaign milestones and achievements
- Adapts campaign based on player choices
- Maintains campaign continuity and consistency
- Generates campaign-specific content and hooks
- Balances different storylines and plot threads

**Restrictions:**
- Must maintain narrative consistency
- Cannot invalidate player choices and achievements
- Should balance different storylines for all players
- Must ensure campaign pacing is appropriate
- Cannot force players down predetermined paths

## Agent Workflow and Interaction

### Player Action Processing Flow

```
Player Action
    │
    ▼
┌─────────┐     ┌─────────────────────┐
│   DMA   │◄────┤ Context & Game State│
└────┬────┘     └─────────────────────┘
     │
     ▼
┌────────────────────┐
│ Action Type Analysis│
└─────────┬──────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
▼                     ▼                    ▼                      ▼
┌─────────┐     ┌─────────┐          ┌─────────┐           ┌─────────┐
│   CRA   │     │   NEA   │          │   EEA   │           │   WEA   │
└────┬────┘     └────┬────┘          └────┬────┘           └────┬────┘
     │               │                    │                     │
     ▼               ▼                    ▼                     ▼
┌─────────┐     ┌─────────┐          ┌─────────┐           ┌─────────┐
│ Combat  │     │  NPC    │          │Exploration│          │Environment│
│Processing│     │Processing│          │Processing│          │Processing│
└────┬────┘     └────┬────┘          └────┬────┘           └────┬────┘
     │               │                    │                     │
     └───────────────┴────────────────────┴─────────────────────┘
                     │
                     ▼
                ┌─────────┐
                │   MSA   │◄─── If magical elements are involved
                └────┬────┘
                     │
                     ▼
                ┌─────────┐
                │   CMA   │◄─── If character updates are needed
                └────┬────┘
                     │
                     ▼
                ┌─────────┐
                │  CaMA   │◄─── For campaign progression updates
                └────┬────┘
                     │
                     ▼
                ┌─────────┐
                │   DMA   │
                └────┬────┘
                     │
                     ▼
               Player Response
```

### Agent Communication Protocol

Agents communicate through a structured protocol that ensures consistent information flow and prevents conflicts:

1. **Request-Response Pattern**: Agents use a standardized request-response pattern for inter-agent communication
2. **Context Sharing**: All agents have access to a shared context object that contains relevant game state
3. **Priority System**: Agents have defined priority levels for conflict resolution
4. **State Updates**: Agents publish state updates to a central state manager
5. **Event Broadcasting**: Important events are broadcast to all relevant agents

## Agent Prompt Structure

Each agent uses a specialized prompt structure that defines its behavior and capabilities:

```
[AGENT_TYPE]: You are the [FULL_AGENT_NAME] for AD&D 1st Edition.

[ROLE_DESCRIPTION]: Detailed description of the agent's role and responsibilities.

[CONSTRAINTS]: List of restrictions and limitations on the agent's behavior.

[CONTEXT]: Current game state, player information, and relevant history.

[INSTRUCTIONS]: Specific instructions for processing the current request.

[EXAMPLES]: Example inputs and outputs to guide the agent's responses.

[QUERY]: The specific request or action to process.
```

## Agent Implementation

The agents are implemented in the backend system using the OpenRouter API to access various AI models. The implementation follows these key principles:

1. **Modularity**: Each agent is implemented as a separate module with clear interfaces
2. **Tiered Model Approach**: Different complexity tasks use different AI models
3. **Prompt Engineering**: Carefully crafted prompts guide each agent's behavior
4. **Context Management**: Efficient context handling maximizes available token space
5. **Error Handling**: Robust error handling ensures system resilience

## Conclusion

The multi-agent AI system is the core of the RPGer application, providing a flexible, modular approach to managing the complex interactions of a role-playing game. By dividing responsibilities among specialized agents, the system can deliver a rich, responsive game experience while maintaining consistency and balance.

Future enhancements to the agent system will focus on improving inter-agent coordination, expanding agent capabilities, and optimizing performance.
