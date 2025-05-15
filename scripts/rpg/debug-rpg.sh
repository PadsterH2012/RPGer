#!/bin/bash

# Debug RPG Web App Script
# This script runs the RPG web app with all debug options enabled

echo "Starting RPG Web App in debug mode..."

# Run the start-rpg script with all debug options
./scripts/rpg/start-rpg.sh --mode=standard --debug --show-prompt --save-state --open-client

echo "Debug environment set up successfully!"
echo "You can now interact with the RPG web app and see detailed debug information."
echo ""
echo "Debug files that will be created:"
echo "- logs/rpg_web_app.log: Main application log"
echo "- App/backend/full_prompt_debug.txt: The full prompt sent to the model"
echo "- App/backend/model_response_debug.txt: The raw response from the model"
echo "- logs/game_states/*.json: Saved game states (when using save-state.sh)"
echo ""
echo "To view logs in real-time, run: ./scripts/rpg/view-logs.sh"
