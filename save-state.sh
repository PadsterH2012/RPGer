#!/bin/bash

# Save state script for RPG Web App
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
SAVE_FILE="game_state_${TIMESTAMP}.json"
echo "Saving game state to $SAVE_FILE..."
curl -s http://localhost:5002/api/socketio-status > $SAVE_FILE
echo "Game state saved to $SAVE_FILE"
