# RPGer Agent Prompts

This directory contains all the prompts used by the various specialized agents in the RPGer system.

## Prompt Naming Convention

Prompts follow a specific naming convention:

```
{agent_code}_{tier}_prompt.txt
```

Where:
- `agent_code` is the lowercase code for the agent (e.g., dma, cma, cra)
- `tier` is the tier level (tier1, tier2, tier3)

Examples:
- `dma_tier1_prompt.txt` - Tier 1 prompt for the Dungeon Master Agent
- `cma_tier2_prompt.txt` - Tier 2 prompt for the Character Management Agent

## Agent Types

The system uses the following specialized agents:

- **DMA**: Dungeon Master Agent - Main narrative and game flow
- **CRA**: Combat Resolution Agent - Handles attacks and damage
- **CMA**: Character Management Agent - Handles character stats and abilities
- **NEA**: NPC & Encounter Agent - Manages NPCs, monsters, and treasure
- **EEA**: Exploration Engine Agent - Handles movement, searching, and obstacles
- **WEA**: World & Environment Agent - Manages time, weather, and resources
- **MSA**: Magic System Agent - Manages spells, magic items, and magical effects
- **CaMA**: Campaign Manager Agent - Handles campaign creation and management

## Tier System

The system uses a tiered approach to agent prompts:

- **Tier 1**: Basic functionality, minimal context, used for simple tasks
- **Tier 2**: More detailed functionality, more context, used for moderate complexity tasks
- **Tier 3**: Advanced functionality, full context, used for complex tasks

The system will automatically escalate to higher tiers if needed based on confidence thresholds.

## Prompt Structure

Each prompt should follow a consistent structure:

1. **Role Definition**: Clear statement of the agent's role and responsibilities
2. **Task Guidelines**: Specific instructions for handling different types of tasks
3. **Response Format**: Expected format for responses (JSON, narrative text, etc.)
4. **Examples**: Examples of correct and incorrect responses

## Modifying Prompts

When modifying prompts:

1. Test changes thoroughly using the test scripts in `App/backend/`
2. Ensure the prompt maintains the correct response format
3. Keep prompts focused on the specific role of each agent
4. Document any significant changes

## Important Notes

- All prompts must be placed in this directory (`App/prompts/`)
- The system will automatically load all files with the `_prompt.txt` suffix
- Changes to prompts will take effect when the application is restarted
