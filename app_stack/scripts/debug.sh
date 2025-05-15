#!/bin/bash

# Debug script for RPGer Application
# This script shows logs for the backend

echo "=== RPGer Debug Tool ==="

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_STACK_DIR="$(dirname "$SCRIPT_DIR")"
BACKEND_DIR="$APP_STACK_DIR/backend"

# Check if log file exists
LOG_FILE="$BACKEND_DIR/rpg_web_app.log"
if [ ! -f "$LOG_FILE" ]; then
    echo "Error: Log file not found at $LOG_FILE"
    echo "Make sure the backend has been started at least once"
    exit 1
fi

# Show logs
echo "Showing logs from $LOG_FILE..."
tail -f "$LOG_FILE"
