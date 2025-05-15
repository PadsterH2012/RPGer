# RPG Web App Multi-Command Program (MCP)

This Multi-Command Program (MCP) provides a unified interface for managing the RPG web app.

## Installation

1. Make sure you have all the required dependencies installed:

```bash
pip install flask flask-socketio flask-cors requests python-dotenv
```

2. Make the MCP script executable:

```bash
chmod +x rpg-mcp.sh
```

## Usage

```bash
./rpg-mcp.sh COMMAND [OPTIONS]
```

## Commands

### `start [OPTIONS]`

Start the RPG web app.

Options:
- `-m, --mode=MODE`: Set the game mode (default: standard)
- `-d, --debug`: Enable debug mode
- `-p, --show-prompt`: Show the prompt being used
- `-s, --save-state`: Save the game state to a file
- `-o, --open-client`: Open the test client in browser
- `--port=PORT`: Set the port (default: 5002)

Example:
```bash
./rpg-mcp.sh start --mode=standard --open-client
```

### `debug`

Start the RPG web app in debug mode with all debug options enabled.

```bash
./rpg-mcp.sh debug
```

### `test MODE`

Test a specific game mode.

```bash
./rpg-mcp.sh test create_character
```

### `logs`

View the RPG web app logs in real-time.

```bash
./rpg-mcp.sh logs
```

### `save`

Save the current game state to a file.

```bash
./rpg-mcp.sh save
```

### `stop`

Stop the RPG web app.

```bash
./rpg-mcp.sh stop
```

### `status`

Check the status of the RPG web app.

```bash
./rpg-mcp.sh status
```

### `help`

Show help message.

```bash
./rpg-mcp.sh help
```

## Game Modes

The RPG web app supports multiple game modes:

- `standard`: Normal gameplay mode
- `create_character`: Character creation mode
- `create_campaign`: Campaign creation mode
- `continue_campaign`: Continue existing campaign mode
- `random_encounter`: Random encounter mode

## Debug Files

When running in debug mode, the following files are created:

- `logs/rpg_web_app.log`: Main application log
- `App/backend/full_prompt_debug.txt`: The full prompt sent to the model
- `App/backend/model_response_debug.txt`: The raw response from the model
- `logs/game_states/*.json`: Saved game states

## Examples

Start the RPG web app in standard mode and open the test client:
```bash
./rpg-mcp.sh start --mode=standard --open-client
```

Start the RPG web app in debug mode:
```bash
./rpg-mcp.sh debug
```

Test the character creation mode:
```bash
./rpg-mcp.sh test create_character
```

View the logs:
```bash
./rpg-mcp.sh logs
```

Save the current game state:
```bash
./rpg-mcp.sh save
```

Stop the RPG web app:
```bash
./rpg-mcp.sh stop
```

Check the status of the RPG web app:
```bash
./rpg-mcp.sh status
```
