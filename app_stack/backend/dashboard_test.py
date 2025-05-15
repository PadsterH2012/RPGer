#!/usr/bin/env python
"""
Dashboard Test Script

This script creates a simple Flask-SocketIO server that emits test data to the dashboard.
It's designed to verify that the old Python code can output to the new dashboard windows.

Usage:
    python dashboard_test.py
"""

import os
import json
import threading
import time
import random
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('DashboardTest')

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# Enable CORS for all routes and origins
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Mock game state for testing
game_state = {
    "player": {
        "name": "Test Character",
        "race": "Human",
        "class": "Fighter",
        "level": 1,
        "hp": 10,
        "max_hp": 10,
        "stats": {"STR": 16, "DEX": 14, "CON": 15, "INT": 12, "WIS": 10, "CHA": 8}
    },
    "environment": {
        "location": "Test Dungeon",
        "description": "A dark, damp dungeon with stone walls.",
        "creatures": []
    },
    "world": {
        "time": {"day": 1, "hour": 12},
        "weather": {"condition": "Clear"},
        "light": {"level": "Dim"}
    },
    "exploration": {},
    "action_results": ["You enter the dungeon.", "You see a torch on the wall."],
    "dm_messages": ["Welcome to the test dungeon!", "This is a test message from the DM."],
    "agent_debug": ["Test script initialized", "Game state created"],
    "processing": False,
    "last_update": time.time()
}

# Mock MongoDB connection status
mongodb_connected = False
mongodb_collections = 0
mongodb_db_name = ""
mongodb_db_size = "0 MB"

# Mock Redis connection status
redis_connected = False
redis_memory = "0 MB"
redis_keys = 0
redis_uptime = 0

# Function to simulate connecting to MongoDB
def connect_to_mongodb():
    global mongodb_connected, mongodb_collections, mongodb_db_name, mongodb_db_size
    logger.info("Connecting to MongoDB...")
    # Simulate connection delay
    time.sleep(2)
    # Set connection status
    mongodb_connected = True
    mongodb_collections = random.randint(3, 10)
    mongodb_db_name = "rpger"
    mongodb_db_size = f"{random.randint(1, 100)} MB"
    logger.info(f"Connected to MongoDB. Collections: {mongodb_collections}")

# Function to simulate connecting to Redis
def connect_to_redis():
    global redis_connected, redis_memory, redis_keys, redis_uptime
    logger.info("Connecting to Redis...")
    # Simulate connection delay
    time.sleep(1)
    # Set connection status
    redis_connected = True
    redis_memory = f"{random.randint(1, 50)} MB"
    redis_keys = random.randint(10, 100)
    redis_uptime = random.randint(60, 3600)
    logger.info(f"Connected to Redis. Memory usage: {redis_memory}")

# Function to update game state periodically
def update_game_state():
    global game_state
    while True:
        # Update player HP randomly
        current_hp = game_state["player"]["hp"]
        max_hp = game_state["player"]["max_hp"]
        new_hp = max(1, min(max_hp, current_hp + random.randint(-2, 2)))
        game_state["player"]["hp"] = new_hp
        
        # Add a random message
        messages = [
            "You hear a distant sound.",
            "The torch flickers.",
            "A cold breeze blows through the dungeon.",
            "You feel like you're being watched.",
            "The ground trembles slightly."
        ]
        game_state["dm_messages"].append(random.choice(messages))
        # Keep only the last 5 messages
        game_state["dm_messages"] = game_state["dm_messages"][-5:]
        
        # Update timestamp
        game_state["last_update"] = time.time()
        
        # Emit updated game state
        logger.info("Emitting game state update")
        socketio.emit('game_state_update', game_state)
        
        # Sleep for a random interval
        time.sleep(random.randint(3, 8))

# API Routes
@app.route('/api/status')
def api_status():
    """API endpoint to check the status of services"""
    try:
        status = {
            "mongodb": {
                "connected": mongodb_connected,
                "collections": mongodb_collections,
                "databaseName": mongodb_db_name,
                "databaseSize": mongodb_db_size
            },
            "redis": {
                "connected": redis_connected,
                "usedMemory": redis_memory,
                "totalKeys": redis_keys,
                "uptime": redis_uptime
            },
            "socketio": {
                "connected": True,
                "clients": len(socketio.server.eio.sockets) if hasattr(socketio, 'server') else 0
            }
        }
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error in status endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/socketio-status')
def socketio_status():
    """Simple endpoint to check if Socket.IO server is running"""
    return jsonify({
        "status": "ok",
        "version": "5.3.6",
        "clients": len(socketio.server.eio.sockets) if hasattr(socketio, 'server') else 0
    })

# Socket.IO event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f'Client connected: {request.sid}')
    emit('response', {'message': 'Connected to Dashboard Test Server'})
    
    # Emit initial game state
    emit('game_state_update', game_state)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f'Client disconnected: {request.sid}')

@socketio.on('command')
def handle_command(data):
    """Handle player command"""
    logger.info(f'Received command from {request.sid}: {data}')
    
    command = data.get('command', '')
    if not command:
        emit('error', {'message': 'No command provided'})
        return
    
    # Add command to action results
    game_state["action_results"].append(f"You entered: {command}")
    
    # Add a mock response
    game_state["dm_messages"].append(f"The DM acknowledges your command: {command}")
    
    # Emit updated game state
    emit('game_state_update', game_state)
    emit('command_received', {'status': 'success'})

@socketio.on('get_game_state')
def handle_get_game_state():
    """Get the current game state"""
    logger.info(f'Received get_game_state request from {request.sid}')
    emit('game_state_update', game_state)

@socketio.on('widget:requestData')
def handle_widget_data_request(data):
    """Handle widget data request"""
    logger.info(f'Received widget data request from {request.sid}: {data}')
    
    widget_id = data.get('widgetId', '')
    data_source = data.get('dataSource', '')
    
    # Generate mock data based on the widget and data source
    mock_data = []
    
    if 'table' in widget_id.lower():
        # Generate mock table data
        for i in range(5):
            mock_data.append({
                'id': i + 1,
                'name': f'Item {i + 1}',
                'value': random.randint(10, 500)
            })
    
    # Emit data to the widget
    emit('widget:tableData', {
        'widgetId': widget_id,
        'data': mock_data
    })

# Main entry point
if __name__ == '__main__':
    # Start MongoDB connection in a separate thread
    mongodb_thread = threading.Thread(target=connect_to_mongodb)
    mongodb_thread.daemon = True
    mongodb_thread.start()
    
    # Start Redis connection in a separate thread
    redis_thread = threading.Thread(target=connect_to_redis)
    redis_thread.daemon = True
    redis_thread.start()
    
    # Start game state update thread
    update_thread = threading.Thread(target=update_game_state)
    update_thread.daemon = True
    update_thread.start()
    
    # Start the SocketIO server
    logger.info("Starting Flask-SocketIO server on http://0.0.0.0:5002")
    socketio.run(app, host='0.0.0.0', port=5002, debug=True, allow_unsafe_werkzeug=True)
