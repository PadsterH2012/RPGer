# RPGer/backend/communication_manager.py
"""
Communication Manager for the RPGer backend.

This module provides functions for real-time communication between the server and clients
using Flask-SocketIO. It includes functions for broadcasting messages to all clients,
sending messages to specific clients, managing rooms, and notifying clients about state changes.

The module is designed to be used by other components of the RPGer backend to provide
real-time updates to connected clients.
"""

import logging
from flask_socketio import join_room as flask_join_room, leave_room as flask_leave_room

# This will be set by main.py
socketio = None

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('CommunicationManager')

def broadcast_message(event, data):
    """Broadcasts a real-time message to all connected clients using Flask-SocketIO."""
    logger.info(f"Broadcasting message: {event}")
    socketio.emit(event, data, broadcast=True)

def send_to_client(client_id, event, data):
    """Sends a message to a specific client using Flask-SocketIO."""
    logger.info(f"Sending message to client {client_id}: {event}")
    socketio.emit(event, data, room=client_id)

def join_room(client_id, room):
    """Adds a client to a specific room."""
    logger.info(f"Client {client_id} joining room: {room}")
    flask_join_room(room)

def leave_room(client_id, room):
    """Removes a client from a specific room."""
    logger.info(f"Client {client_id} leaving room: {room}")
    flask_leave_room(room)

def send_to_room(room, event, data):
    """Sends a message to all clients in a specific room."""
    logger.info(f"Sending message to room {room}: {event}")
    socketio.emit(event, data, room=room)

def update_game_state(game_state, event_type="game_state_update"):
    """
    Broadcasts a game state update to all connected clients.

    Args:
        game_state: The current game state to broadcast
        event_type: The event name to use (default: "game_state_update")
    """
    logger.info(f"Broadcasting game state update: {event_type}")
    socketio.emit(event_type, {"game_state": game_state}, broadcast=True)

def notify_state_change(change_type, entity_id, data):
    """
    Notifies clients about a specific state change.

    Args:
        change_type: Type of change (e.g., "character", "world", "npc")
        entity_id: ID of the entity that changed
        data: The changed data
    """
    logger.info(f"Notifying state change: {change_type} for {entity_id}")
    socketio.emit("state_change", {
        "type": change_type,
        "id": entity_id,
        "data": data
    }, broadcast=True)