#!/usr/bin/env python
"""
Socket.IO Test Client (Mock Mode)

This script simulates a Socket.IO client that would connect to the dashboard test server.
Since we're having issues with the real server, this script will use mock data to demonstrate
how the communication would work if the server was running.

Usage:
    python test_client.py
"""

import time
import json
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('TestClient')

# Mock Socket.IO client
class MockSocketIO:
    def __init__(self):
        self.connected = False
        self.event_handlers = {}

    def on(self, event, handler=None):
        if handler is None:
            def decorator(f):
                self.event_handlers[event] = f
                return f
            return decorator
        else:
            self.event_handlers[event] = handler

    def emit(self, event, data=None):
        logger.info(f"Emitting event: {event}")
        logger.info(f"Data: {data}")

        # Simulate server response
        if event == 'get_game_state':
            self._trigger_event('game_state_update', self._mock_game_state())
        elif event == 'command':
            self._trigger_event('command_received', {'status': 'success'})
            self._trigger_event('game_state_update', self._mock_game_state())
        elif event == 'widget:requestData':
            self._trigger_event('widget:tableData', {
                'widgetId': data.get('widgetId', 'unknown'),
                'data': self._mock_table_data()
            })

    def connect(self, url):
        logger.info(f"Connecting to: {url}")
        self.connected = True
        self._trigger_event('connect')
        self._trigger_event('response', {'message': 'Connected to Mock Server'})

    def disconnect(self):
        logger.info("Disconnecting")
        self.connected = False
        self._trigger_event('disconnect')

    def _trigger_event(self, event, data=None):
        if event in self.event_handlers:
            if data is not None:
                self.event_handlers[event](data)
            else:
                self.event_handlers[event]()

    def _mock_game_state(self):
        return {
            "player": {
                "name": "Test Character",
                "race": "Human",
                "class": "Fighter",
                "level": 1,
                "hp": 8,
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

    def _mock_table_data(self):
        return [
            {'id': 1, 'name': 'Item 1', 'value': 100},
            {'id': 2, 'name': 'Item 2', 'value': 200},
            {'id': 3, 'name': 'Item 3', 'value': 300},
            {'id': 4, 'name': 'Item 4', 'value': 400},
            {'id': 5, 'name': 'Item 5', 'value': 500}
        ]

# Create a mock Socket.IO client
sio = MockSocketIO()

# Event handlers
def connect_handler():
    logger.info('Connected to server')
sio.on('connect', connect_handler)

def disconnect_handler():
    logger.info('Disconnected from server')
sio.on('disconnect', disconnect_handler)

def response_handler(data):
    logger.info(f'Received response: {data}')
sio.on('response', response_handler)

def game_state_update_handler(data):
    logger.info('Received game state update')
    # Print a summary of the game state
    if 'player' in data:
        player = data['player']
        logger.info(f"Player: {player.get('name', 'Unknown')}, HP: {player.get('hp', 0)}/{player.get('max_hp', 0)}")

    if 'environment' in data:
        env = data['environment']
        logger.info(f"Location: {env.get('location', 'Unknown')}")

    if 'dm_messages' in data:
        messages = data['dm_messages']
        if messages:
            logger.info(f"Latest DM message: {messages[-1]}")
sio.on('game_state_update', game_state_update_handler)

def widget_table_data_handler(data):
    logger.info(f"Received table data for widget: {data.get('widgetId', 'Unknown')}")
    logger.info(f"Data: {data.get('data', [])}")
sio.on('widget:tableData', widget_table_data_handler)

def error_handler(data):
    logger.error(f"Received error: {data}")
sio.on('error', error_handler)

# Function to mock API status
def mock_api_status():
    logger.info("Mocking API status...")
    status = {
        "mongodb": {
            "connected": True,
            "collections": 7,
            "databaseName": "rpger",
            "databaseSize": "25 MB"
        },
        "redis": {
            "connected": True,
            "usedMemory": "12 MB",
            "totalKeys": 42,
            "uptime": 3600
        },
        "socketio": {
            "connected": True,
            "clients": 1
        }
    }
    logger.info("API Status:")
    logger.info(f"MongoDB: {status['mongodb']['connected']}")
    logger.info(f"Redis: {status['redis']['connected']}")
    logger.info(f"SocketIO: {status['socketio']['connected']}")
    return status

# Function to mock Socket.IO status
def mock_socketio_status():
    logger.info("Mocking Socket.IO status...")
    status = {
        "status": "ok",
        "version": "5.3.6",
        "clients": 1
    }
    logger.info(f"Socket.IO Status: {status}")
    return status

# Function to send a test command
def send_test_command():
    try:
        logger.info("Sending test command...")
        sio.emit('command', {'command': 'look around'})
        logger.info("Test command sent")
    except Exception as e:
        logger.error(f"Error sending test command: {e}")

# Function to request widget data
def request_widget_data():
    try:
        logger.info("Requesting widget data...")
        sio.emit('widget:requestData', {
            'widgetId': 'test-table-widget',
            'dataSource': 'test'
        })
        logger.info("Widget data request sent")
    except Exception as e:
        logger.error(f"Error requesting widget data: {e}")

# Main function
def main():
    try:
        # Mock API status
        mock_api_status()

        # Mock Socket.IO status
        mock_socketio_status()

        # Connect to the mock server
        logger.info("Connecting to mock Socket.IO server...")
        sio.connect('http://localhost:5002')

        # Wait for a moment to simulate initial events
        logger.info("Waiting for initial events...")
        time.sleep(2)

        # Request game state
        logger.info("Requesting game state...")
        sio.emit('get_game_state')

        # Wait for a moment to simulate receiving game state
        time.sleep(1)

        # Send a test command
        send_test_command()

        # Wait for a moment to simulate receiving command response
        time.sleep(1)

        # Request widget data
        request_widget_data()

        # Wait for a moment to simulate receiving widget data
        time.sleep(1)

        # Simulate periodic game state updates
        logger.info("Simulating periodic game state updates...")
        for i in range(3):
            time.sleep(2)
            logger.info(f"Simulating game state update {i+1}...")
            sio._trigger_event('game_state_update', sio._mock_game_state())

        logger.info("Test client demonstration completed.")

    except KeyboardInterrupt:
        logger.info("Test client stopped by user")
    except Exception as e:
        logger.error(f"Error in main function: {e}")
    finally:
        # Disconnect from the server
        if sio.connected:
            sio.disconnect()

if __name__ == '__main__':
    main()
