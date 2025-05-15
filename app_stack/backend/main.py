# RPGer/backend/main.py
"""
Main entry point for the RPGer backend server.
This module initializes a Flask application with Flask-SocketIO integration
for real-time bidirectional communication between the server and clients.
CORS is enabled to allow connections from any origin, which is particularly
useful for development and testing with file:// URLs.

This module also exports the SimpleADDTest class for use by other modules.
"""

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import communication_manager

# Import the SimpleADDTest class
from simple_add_test import SimpleADDTest

# Initialize Flask app and SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# Enable CORS for all origins
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# Set the socketio instance in communication_manager
communication_manager.socketio = socketio

# Define a basic route
@app.route('/')
def index():
    return "RPGer Backend with Flask-SocketIO"

# Example SocketIO event handler for client connection
@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('response', {'message': 'Connected to RPGer backend'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

# Example event handler for a custom event
@socketio.on('my_event')
def handle_my_custom_event(data):
    print('Received event:', data)
    emit('response', {'message': 'Event received'})

if __name__ == '__main__':
    # Start the SocketIO server
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)