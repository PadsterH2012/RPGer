#!/bin/bash

# Test Different Game Modes Script
# This script allows testing different game modes in the RPG web app

# Check if a mode was provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 MODE"
    echo "Available modes: standard, create_character, create_campaign, continue_campaign, random_encounter"
    exit 1
fi

# Get the mode
MODE=$1

# Validate mode
case $MODE in
  standard|create_character|create_campaign|continue_campaign|random_encounter)
    echo "Testing mode: $MODE"
    ;;
  *)
    echo "Invalid mode: $MODE"
    echo "Available modes: standard, create_character, create_campaign, continue_campaign, random_encounter"
    exit 1
    ;;
esac

# Start the RPG web app with the specified mode
./scripts/rpg/start-rpg.sh --mode=$MODE --open-client

echo "Testing $MODE mode. You can now interact with the RPG web app."
