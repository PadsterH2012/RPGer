# RPG Web App Scripts

This directory contains scripts for running and debugging the RPG web app.

## Available Scripts

### `start-rpg.sh`

The main script for starting the RPG web app with various options.

```bash
./scripts/rpg/start-rpg.sh [OPTIONS]
```

Options:
- `-m, --mode=MODE`: Set the game mode (default: standard)
- `-d, --debug`: Enable debug mode
- `-p, --show-prompt`: Show the prompt being used
- `-s, --save-state`: Save the game state to a file
- `-o, --open-client`: Open the test client in browser
- `--port=PORT`: Set the port (default: 5002)
- `-h, --help`: Show help message

Available modes:
- `standard`: Normal gameplay mode
- `create_character`: Character creation mode
- `create_campaign`: Campaign creation mode
- `continue_campaign`: Continue existing campaign mode
- `random_encounter`: Random encounter mode

Example:
```bash
./scripts/rpg/start-rpg.sh --mode=standard --debug --open-client
```

### `debug-rpg.sh`

Runs the RPG web app with all debug options enabled.

```bash
./scripts/rpg/debug-rpg.sh
```

This script:
- Starts the RPG web app in standard mode
- Enables debug mode
- Shows the prompt being used
- Enables game state saving
- Opens the test client in the browser

### `test-modes.sh`

Tests a specific game mode.

```bash
./scripts/rpg/test-modes.sh MODE
```

Example:
```bash
./scripts/rpg/test-modes.sh create_character
```

### `view-logs.sh`

Views the RPG web app logs in real-time.

```bash
./scripts/rpg/view-logs.sh
```

### `save-state.sh`

Saves the current game state to a file.

```bash
./scripts/rpg/save-state.sh
```

## Debug Files

When running in debug mode, the following files are created:

- `logs/rpg_web_app.log`: Main application log
- `App/backend/full_prompt_debug.txt`: The full prompt sent to the model
- `App/backend/model_response_debug.txt`: The raw response from the model
- `logs/game_states/*.json`: Saved game states (when using save-state.sh)

## Game Modes

The RPG web app supports multiple game modes that affect how the AI agents process player input and what functionality is available.

### Standard Mode (`standard`)

The default mode for normal gameplay. In this mode, the Dungeon Master Agent (DMA) processes player actions and coordinates with other specialized agents to provide a complete RPG experience.

### Character Creation Mode (`create_character`)

A specialized mode for creating new player characters. In this mode, the Character Management Agent (CMA) guides the player through the character creation process step by step.

### Campaign Creation Mode (`create_campaign`)

A specialized mode for creating new campaigns. In this mode, the Campaign Manager Agent (CaMA) helps the player design a campaign setting, plot, and NPCs.

### Continue Campaign Mode (`continue_campaign`)

A mode for loading and continuing an existing campaign. This mode allows players to resume a previously saved campaign.

### Random Encounter Mode (`random_encounter`)

A mode for generating and playing through random encounters. This is useful for one-off sessions or when players want a quick gameplay experience.

## Troubleshooting

### The RPG web app doesn't start

Make sure you have all the required dependencies installed:

```bash
pip install flask flask-socketio flask-cors requests python-dotenv
```

### The test client doesn't connect to the server

Check that the server is running and that the port in the test client matches the port the server is running on (default: 5002).

### The DMA doesn't follow the expected format

The system includes an automatic fallback mechanism that generates a compliant response when the model doesn't follow the expected format. You can check the `model_response_debug.txt` file to see the raw response from the model.

## Future Improvements

- Add support for switching modes during gameplay
- Create dedicated prompt files for each mode
- Implement a web-based admin interface for managing the RPG web app
- Add support for multiple concurrent games
- Integrate with a database for persistent storage
