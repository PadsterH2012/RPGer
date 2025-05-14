#!/usr/bin/env python
"""
Simple Flask-SocketIO server for testing.
This script starts a Flask-SocketIO server with basic event handlers.
"""

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SimpleSocketIOServer')

# Initialize Flask app and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# Enable CORS for all origins
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# Define a basic route
@app.route('/')
def index():
    return "Simple Flask-SocketIO Server for Testing"

# SocketIO event handlers
@socketio.on('connect')
def handle_connect():
    logger.info(f"Client connected: {request.sid}")
    emit('response', {'message': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('my_event')
def handle_my_custom_event(data):
    logger.info(f"Received event from {request.sid}: {data}")
    emit('response', {'message': 'Event received', 'data': data})

@socketio.on('game_action')
def handle_game_action(data):
    logger.info(f"Received game action from {request.sid}: {data}")
    # Process the game action
    # ...

    # Send a game state update to all clients
    socketio.emit('game_state_update', {
        'game_state': {
            'player': {
                'name': 'Test Player',
                'hp': 20,
                'max_hp': 20,
                'level': 1,
                'class': 'Fighter',
                'race': 'Human'
            },
            'environment': {
                'location': 'Test Dungeon',
                'time': 'Day 1, 12:00',
                'weather': 'Clear',
                'light': 'Bright'
            }
        }
    })

@socketio.on('state_change_request')
def handle_state_change_request(data):
    logger.info(f"Received state change request from {request.sid}: {data}")
    # Process the state change request
    # ...

    # Send a state change notification to all clients
    socketio.emit('state_change', {
        'type': data.get('type', 'unknown'),
        'id': data.get('id', 'unknown'),
        'data': data.get('data', {})
    })

if __name__ == '__main__':
    logger.info("Starting Flask-SocketIO server on http://localhost:5001")
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True)
