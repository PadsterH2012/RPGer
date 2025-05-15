#!/bin/bash

# RPG Web App Multi-Command Program (MCP)
# This script provides a unified interface for managing the RPG web app

# Function to display help
show_help() {
    echo "RPG Web App MCP - Multi-Command Program"
    echo ""
    echo "Usage: $0 COMMAND [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start [OPTIONS]       Start the RPG web app"
    echo "  debug                 Start the RPG web app in debug mode"
    echo "  test MODE             Test a specific game mode"
    echo "  logs                  View the RPG web app logs"
    echo "  save                  Save the current game state"
    echo "  stop                  Stop the RPG web app"
    echo "  status                Check the status of the RPG web app"
    echo "  help                  Show this help message"
    echo ""
    echo "Options for 'start' command:"
    echo "  -m, --mode=MODE       Set the game mode (default: standard)"
    echo "  -d, --debug           Enable debug mode"
    echo "  -p, --show-prompt     Show the prompt being used"
    echo "  -s, --save-state      Save the game state to a file"
    echo "  -o, --open-client     Open the test client in browser"
    echo "  --port=PORT           Set the port (default: 5002)"
    echo ""
    echo "Available modes: standard, create_character, create_campaign, continue_campaign, random_encounter"
    echo ""
    echo "Examples:"
    echo "  $0 start --mode=standard --open-client"
    echo "  $0 debug"
    echo "  $0 test create_character"
    echo "  $0 logs"
    echo "  $0 stop"
}

# Function to check if the RPG web app is running
is_running() {
    if pgrep -f "python3.*rpg_web_app.py" > /dev/null; then
        return 0  # Running
    else
        return 1  # Not running
    fi
}

# Function to get the PID of the RPG web app
get_pid() {
    pgrep -f "python3.*rpg_web_app.py"
}

# Check if a command was provided
if [ $# -eq 0 ]; then
    show_help
    exit 1
fi

# Get the command
COMMAND=$1
shift

# Process the command
case $COMMAND in
    start)
        # Start the RPG web app
        ./scripts/rpg/start-rpg.sh "$@"
        ;;
    debug)
        # Start the RPG web app in debug mode
        ./scripts/rpg/debug-rpg.sh
        ;;
    test)
        # Test a specific game mode
        if [ $# -eq 0 ]; then
            echo "Error: No mode specified"
            echo "Usage: $0 test MODE"
            echo "Available modes: standard, create_character, create_campaign, continue_campaign, random_encounter"
            exit 1
        fi
        ./scripts/rpg/test-modes.sh "$1"
        ;;
    logs)
        # View the RPG web app logs
        if [ -f "scripts/rpg/view-logs.sh" ]; then
            ./scripts/rpg/view-logs.sh
        else
            echo "Error: Log viewer script not found"
            echo "Run '$0 debug' first to create the log viewer script"
            exit 1
        fi
        ;;
    save)
        # Save the current game state
        if [ -f "scripts/rpg/save-state.sh" ]; then
            ./scripts/rpg/save-state.sh
        else
            echo "Error: Save state script not found"
            echo "Run '$0 start --save-state' or '$0 debug' first to create the save state script"
            exit 1
        fi
        ;;
    stop)
        # Stop the RPG web app
        if is_running; then
            PID=$(get_pid)
            echo "Stopping RPG web app (PID: $PID)..."
            kill $PID
            echo "RPG web app stopped"
        else
            echo "RPG web app is not running"
        fi
        ;;
    status)
        # Check the status of the RPG web app
        if is_running; then
            PID=$(get_pid)
            echo "RPG web app is running (PID: $PID)"
            echo "You can access it at http://localhost:5002"
        else
            echo "RPG web app is not running"
        fi
        ;;
    help)
        # Show help
        show_help
        ;;
    *)
        # Unknown command
        echo "Error: Unknown command '$COMMAND'"
        show_help
        exit 1
        ;;
esac
