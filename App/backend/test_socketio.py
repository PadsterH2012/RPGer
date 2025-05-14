#!/usr/bin/env python
"""
Test script for Flask-SocketIO in RPGer backend.
This script tests the Socket.IO connection and event handling.
"""

import sys
import time
import socketio
import logging
import json
from argparse import ArgumentParser

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('SocketIOTest')

def create_socketio_client(server_url='http://localhost:5001'):
    """Create a Socket.IO client and connect to the server."""
    sio = socketio.Client()

    @sio.event
    def connect():
        logger.info(f"Connected to server: {server_url}")

    @sio.event
    def disconnect():
        logger.info("Disconnected from server")

    @sio.event
    def connect_error(data):
        logger.error(f"Connection error: {data}")

    @sio.on('response')
    def on_response(data):
        logger.info(f"Received response: {json.dumps(data, indent=2)}")

    @sio.on('state_change')
    def on_state_change(data):
        logger.info(f"Received state change: {json.dumps(data, indent=2)}")

    @sio.on('game_state_update')
    def on_game_state_update(data):
        logger.info(f"Received game state update: {json.dumps(data, indent=2)}")

    return sio

def run_test(server_url='http://localhost:5001', test_duration=10):
    """Run a test of the Socket.IO connection and event handling."""
    sio = create_socketio_client(server_url)

    try:
        # Connect to the server
        logger.info(f"Connecting to server: {server_url}")
        sio.connect(server_url)

        # Send a custom event
        event_data = {
            'message': 'Hello from test script',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        logger.info(f"Sending event: {json.dumps(event_data, indent=2)}")
        sio.emit('my_event', event_data)

        # Wait for responses
        logger.info(f"Waiting for {test_duration} seconds to receive responses...")
        time.sleep(test_duration)

    except Exception as e:
        logger.error(f"Error during test: {e}")
    finally:
        # Disconnect from the server
        if sio.connected:
            logger.info("Disconnecting from server")
            sio.disconnect()

def main():
    """Main entry point for the script."""
    parser = ArgumentParser(description='Test Flask-SocketIO connection')
    parser.add_argument('--url', default='http://localhost:5001', help='Server URL (default: http://localhost:5001)')
    parser.add_argument('--duration', type=int, default=10, help='Test duration in seconds (default: 10)')
    args = parser.parse_args()

    run_test(args.url, args.duration)

if __name__ == '__main__':
    main()
