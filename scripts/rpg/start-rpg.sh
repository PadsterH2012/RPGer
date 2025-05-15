#!/bin/bash

# RPG Web App Starter Script
# This script starts the RPG web app with various options

# Default settings
MODE="standard"
DEBUG=false
SHOW_PROMPT=false
SAVE_STATE=false
OPEN_CLIENT=false
PORT=5002

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --mode=*)
      MODE="${1#*=}"
      shift
      ;;
    -m|--mode)
      MODE="$2"
      shift 2
      ;;
    --debug)
      DEBUG=true
      shift
      ;;
    -d)
      DEBUG=true
      shift
      ;;
    --show-prompt)
      SHOW_PROMPT=true
      shift
      ;;
    -p)
      SHOW_PROMPT=true
      shift
      ;;
    --save-state)
      SAVE_STATE=true
      shift
      ;;
    -s)
      SAVE_STATE=true
      shift
      ;;
    --open-client)
      OPEN_CLIENT=true
      shift
      ;;
    -o)
      OPEN_CLIENT=true
      shift
      ;;
    --port=*)
      PORT="${1#*=}"
      shift
      ;;
    --port)
      PORT="$2"
      shift 2
      ;;
    -h|--help)
      echo "Usage: $0 [OPTIONS]"
      echo "Options:"
      echo "  -m, --mode=MODE       Set the game mode (default: standard)"
      echo "  -d, --debug           Enable debug mode"
      echo "  -p, --show-prompt     Show the prompt being used"
      echo "  -s, --save-state      Save the game state to a file"
      echo "  -o, --open-client     Open the test client in browser"
      echo "  --port=PORT           Set the port (default: 5002)"
      echo "  -h, --help            Show this help message"
      echo ""
      echo "Available modes: standard, create_character, create_campaign, continue_campaign, random_encounter"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use --help for usage information"
      exit 1
      ;;
  esac
done

# Validate mode
case $MODE in
  standard|create_character|create_campaign|continue_campaign|random_encounter)
    echo "Using mode: $MODE"
    ;;
  *)
    echo "Invalid mode: $MODE"
    echo "Available modes: standard, create_character, create_campaign, continue_campaign, random_encounter"
    exit 1
    ;;
esac

# Show debug info
if [ "$DEBUG" = true ]; then
  echo "Debug mode: enabled"
fi

# Show prompt info
if [ "$SHOW_PROMPT" = true ]; then
  echo "Show prompt: enabled"
fi

# Show save state info
if [ "$SAVE_STATE" = true ]; then
  echo "Save state: enabled"
fi

# Show client info
if [ "$OPEN_CLIENT" = true ]; then
  echo "Open client: enabled"
fi

echo "Restarting RPG Web App in $MODE mode on port $PORT..."

# Check if the app is running
if pgrep -f "python3.*rpg_web_app.py" > /dev/null; then
    echo "Stopping existing RPG Web App process..."
    pkill -f "python3.*rpg_web_app.py"
    sleep 2
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Verify prompts
echo "Verifying prompt files..."
python3 App/backend/verify_prompts.py
if [ $? -ne 0 ]; then
    echo "Warning: Prompt verification failed. Continuing anyway..."
fi

# Show the prompt if requested
if [ "$SHOW_PROMPT" = true ]; then
    PROMPT_PATH="App/prompts/dma_tier1_prompt.txt"
    if [ -f "$PROMPT_PATH" ]; then
        echo "========== DMA PROMPT =========="
        cat "$PROMPT_PATH"
        echo "==============================="
        echo ""
    else
        echo "Warning: Could not find prompt file at $PROMPT_PATH"
    fi
fi

# Create a debug script if debug mode is enabled
if [ "$DEBUG" = true ]; then
    DEBUG_SCRIPT="scripts/rpg/view-logs.sh"
    echo "#!/bin/bash" > $DEBUG_SCRIPT
    echo "" >> $DEBUG_SCRIPT
    echo "# Debug script for RPG Web App" >> $DEBUG_SCRIPT
    echo "echo \"Showing logs for RPG Web App...\"" >> $DEBUG_SCRIPT
    echo "tail -f logs/rpg_web_app.log" >> $DEBUG_SCRIPT
    chmod +x $DEBUG_SCRIPT
    echo "Created debug script: $DEBUG_SCRIPT"
fi

# Create a save state script if save state is enabled
if [ "$SAVE_STATE" = true ]; then
    SAVE_SCRIPT="scripts/rpg/save-state.sh"
    echo "#!/bin/bash" > $SAVE_SCRIPT
    echo "" >> $SAVE_SCRIPT
    echo "# Save state script for RPG Web App" >> $SAVE_SCRIPT
    echo "TIMESTAMP=\$(date +\"%Y%m%d_%H%M%S\")" >> $SAVE_SCRIPT
    echo "SAVE_DIR=\"logs/game_states\"" >> $SAVE_SCRIPT
    echo "mkdir -p \$SAVE_DIR" >> $SAVE_SCRIPT
    echo "SAVE_FILE=\"\$SAVE_DIR/game_state_\${TIMESTAMP}.json\"" >> $SAVE_SCRIPT
    echo "echo \"Saving game state to \$SAVE_FILE...\"" >> $SAVE_SCRIPT
    echo "curl -s http://localhost:$PORT/api/socketio-status > \$SAVE_FILE" >> $SAVE_SCRIPT
    echo "echo \"Game state saved to \$SAVE_FILE\"" >> $SAVE_SCRIPT
    chmod +x $SAVE_SCRIPT
    echo "Created save state script: $SAVE_SCRIPT"
fi

# Start the app
echo "Starting RPG Web App..."
cd App/backend
python3 rpg_web_app.py --port=$PORT --mode=$MODE --log-file=../../logs/rpg_web_app.log &
APP_PID=$!
cd ../..

echo "RPG Web App started with PID: $APP_PID"
echo "You can access the app at http://localhost:$PORT"
echo ""
echo "To start a game in $MODE mode, use the 'Start Game' button and select '$MODE' mode"
echo "To stop the app, run: kill $APP_PID"

# Show additional instructions based on enabled options
if [ "$DEBUG" = true ]; then
    echo "To view debug logs, run: ./scripts/rpg/view-logs.sh"
fi

if [ "$SAVE_STATE" = true ]; then
    echo "To save the game state, run: ./scripts/rpg/save-state.sh"
fi

# Open the test client if requested
if [ "$OPEN_CLIENT" = true ]; then
    echo "Opening test client..."
    sleep 2  # Give the server a moment to start
    
    # Get the absolute path to the test client
    TEST_CLIENT_PATH="$(pwd)/App/test-client.html"
    
    # Check if the file exists
    if [ ! -f "$TEST_CLIENT_PATH" ]; then
        echo "Error: Test client not found at $TEST_CLIENT_PATH"
        exit 1
    fi
    
    # Open the test client in the default browser
    echo "Opening $TEST_CLIENT_PATH in your default browser..."
    
    # Try different commands based on the OS
    if command -v xdg-open > /dev/null; then
        xdg-open "file://$TEST_CLIENT_PATH"
    elif command -v open > /dev/null; then
        open "file://$TEST_CLIENT_PATH"
    elif command -v start > /dev/null; then
        start "file://$TEST_CLIENT_PATH"
    else
        echo "Error: Could not open browser. Please open the file manually:"
        echo "file://$TEST_CLIENT_PATH"
    fi
fi
