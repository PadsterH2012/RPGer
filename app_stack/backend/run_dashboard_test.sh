#!/bin/bash
# Run the dashboard test script

echo "Starting Dashboard Test Server..."
echo "This script will start a Flask-SocketIO server that emits test data to the dashboard."
echo "Make sure the React frontend is running in another terminal."
echo ""
echo "The server will run on port 5002, which should match the port configured in the frontend."
echo "Press Ctrl+C to stop the server."
echo ""

# Make the script executable if it's not already
chmod +x dashboard_test.py

# Run the script
python dashboard_test.py
