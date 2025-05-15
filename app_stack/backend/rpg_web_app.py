import os
import json
import threading
import time
import queue
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('RPGWebApp')

# Try to import the game engine
try:
    from simple_add_test import SimpleADDTest
    logger.info("Successfully imported SimpleADDTest from simple_add_test")
except ImportError:
    try:
        from main import SimpleADDTest
        logger.info("Successfully imported SimpleADDTest from main")
    except ImportError:
        logger.warning("Could not import SimpleADDTest from simple_add_test or main. Using mock implementation.")
        # Mock implementation for testing
        class SimpleADDTest:
            def __init__(self, mode="standard"):
                self.mode = mode
                logger.info(f"Created mock SimpleADDTest with mode: {mode}")

            def get_simplified_context(self):
                return {
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
                    "exploration": {}
                }

            def process_player_input(self, input_text):
                logger.info(f"Processing mock input: {input_text}")
                return f"The DM acknowledges your command: {input_text}"

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
# Enable CORS for all routes and origins
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*", logger=True, engineio_logger=True)

# Create a queue for player inputs
player_input_queue = queue.Queue()

# Create a queue for game outputs
game_output_queue = queue.Queue()

# Command processing lock to prevent multiple commands being processed simultaneously
command_lock = threading.Lock()

# Game state for web interface
game_state = {
    "player": {},
    "environment": {
        "location": "",
        "description": "",
        "creatures": []
    },
    "world": {
        "time": {},
        "weather": {},
        "light": {},
        "resources": {}
    },
    "exploration": {},
    "action_results": [],
    "dm_messages": [],
    "agent_debug": [
        "System: Agent debug interface initialized",
        "System: Waiting for game to start..."
    ],
    "processing": False,
    "last_update": 0
}

# Flag to indicate if the game is running
game_running = False

# Game instance
game_instance = None

# Performance metrics
performance_metrics = {
    "command_processing_times": [],
    "avg_processing_time": 0,
    "total_commands": 0
}

def run_game():
    """Run the game in a separate thread"""
    global game_running, game_instance, game_state

    # Add debug message
    game_state["agent_debug"].append("Starting game thread...")
    logger.info("Starting game thread...")

    # Create game instance with the appropriate mode
    try:
        # Get the mode from the game state
        mode = game_state.get("mode")
        game_state["agent_debug"].append(f"Creating game instance with mode: {mode}")
        logger.info(f"Creating game instance with mode: {mode}")

        # Create the game instance with the mode
        game_instance = SimpleADDTest(mode=mode)
        game_state["agent_debug"].append("Game instance created successfully")
        logger.info("Game instance created successfully")
    except Exception as e:
        error_msg = f"ERROR: Failed to create game instance: {str(e)}"
        game_state["agent_debug"].append(error_msg)
        game_state["dm_messages"].append("There was an error starting the game. Please try again.")
        logger.error(error_msg)
        game_running = False
        return

    # Store the original print function
    import builtins
    original_print = builtins.print

    def custom_print(*args, **kwargs):
        """Custom print function to capture output"""
        try:
            # Convert args to string
            output = " ".join(str(arg) for arg in args)

            # Add to debug log for troubleshooting
            if output.startswith("DEBUG:") or output.startswith("ERROR:"):
                original_print(output)
                game_state["agent_debug"].append(output)

            # Check if this is a DM message
            if output.startswith("DM:"):
                game_state["dm_messages"].append(output[3:].strip())
                # Limit to last 20 messages
                if len(game_state["dm_messages"]) > 20:
                    game_state["dm_messages"] = game_state["dm_messages"][-20:]

            # Check if this is an agent debug message
            elif any(keyword in output for keyword in ["Agent", "Requesting", "Extracted JSON", "Updating game state"]):
                # Determine the agent type and message level
                agent_prefix = "System"
                level = "info"

                # Check for agent identifiers
                if "Character Management Agent" in output or "CMA" in output:
                    agent_prefix = "CMA:"
                elif "NPC & Encounter Agent" in output or "NEA" in output:
                    agent_prefix = "NEA:"
                elif "Exploration Engine Agent" in output or "EEA" in output:
                    agent_prefix = "EEA:"
                elif "World & Environment Agent" in output or "WEA" in output:
                    agent_prefix = "WEA:"
                elif "Magic System Agent" in output or "MSA" in output:
                    agent_prefix = "MSA:"
                elif "Campaign Manager Agent" in output or "CaMA" in output:
                    agent_prefix = "CaMA:"

                # Check for message level
                if "ERROR" in output or "error" in output.lower():
                    level = "error"
                    if not output.startswith("ERROR:"):
                        output = f"ERROR: {output}"
                elif "WARNING" in output or "warning" in output.lower():
                    level = "warning"
                    if not output.startswith("WARNING:"):
                        output = f"WARNING: {output}"
                elif "SUCCESS" in output or "success" in output.lower() or "successfully" in output.lower():
                    level = "success"

                # Format the message with agent prefix if not already present
                if not output.startswith(agent_prefix):
                    output = f"{agent_prefix} {output}"

                # Add to debug messages
                game_state["agent_debug"].append(output)

                # Limit to last 50 messages (increased from 20)
                if len(game_state["agent_debug"]) > 50:
                    game_state["agent_debug"] = game_state["agent_debug"][-50:]

                # Also emit a specific debug message event for real-time updates
                try:
                    socketio.emit('debug_message', output)
                except Exception as e:
                    logger.error(f"Failed to emit debug message: {e}")

            # Check if this is a combat result
            elif "[" in output and "HP:" in output:
                # This is a combat stats line
                pass
            else:
                # Add to action results
                game_state["action_results"].append(output)
                # Limit to last 20 results
                if len(game_state["action_results"]) > 20:
                    game_state["action_results"] = game_state["action_results"][-20:]

            # Still print to console
            original_print(*args, **kwargs)

            # Put in output queue
            game_output_queue.put(output)

            # Emit the output via Socket.IO
            socketio.emit('game_output', {'output': output})

        except Exception as e:
            # If there's an error in the custom print function, use the original print
            error_msg = f"ERROR in custom_print: {str(e)}"
            original_print(error_msg)
            logger.error(error_msg)
            try:
                game_state["agent_debug"].append(error_msg)
                game_output_queue.put(error_msg)
                socketio.emit('game_output', {'output': error_msg})
            except:
                pass

    # Replace print function
    builtins.print = custom_print

    try:
        # Initialize game
        game_state["agent_debug"].append("Getting initial game context...")
        logger.info("Getting initial game context...")
        try:
            initial_context = game_instance.get_simplified_context()
            game_state["agent_debug"].append("Got initial context successfully")
            logger.info("Got initial context successfully")
        except Exception as e:
            error_msg = f"ERROR: Failed to get initial game context: {str(e)}"
            game_state["agent_debug"].append(error_msg)
            game_state["dm_messages"].append("There was an error initializing the game. Please try again.")
            logger.error(error_msg)
            game_running = False
            return

        # Update game state
        try:
            # Get player data with full character information
            player_data = initial_context.get("player", {})
            if player_data:
                # Ensure all character fields are included
                game_state["player"] = player_data

            game_state["environment"] = initial_context.get("environment", {})
            game_state["world"] = initial_context.get("world", {})
            game_state["exploration"] = initial_context.get("exploration", {})
            game_state["agent_debug"].append("Updated game state with initial context")
            logger.info("Updated game state with initial context")
        except Exception as e:
            error_msg = f"ERROR: Failed to update game state: {str(e)}"
            game_state["agent_debug"].append(error_msg)
            logger.error(error_msg)
            # Continue anyway with default values

        # Add initial description to DM messages
        try:
            if initial_context.get("environment", {}).get("description"):
                game_state["dm_messages"].append(initial_context["environment"]["description"])

                # Add creatures info if any
                if initial_context.get("environment", {}).get("creatures"):
                    creatures = [c.get("name", "Unknown") for c in initial_context["environment"]["creatures"]]
                    if creatures:
                        game_state["dm_messages"].append(f"You see: {', '.join(creatures)}")
        except Exception as e:
            error_msg = f"ERROR: Failed to add environment description: {str(e)}"
            game_state["agent_debug"].append(error_msg)
            logger.error(error_msg)
            # Continue anyway

        # Add debug info
        game_state["agent_debug"].append("Initial game state loaded")
        logger.info("Initial game state loaded")

        # Mark game as running
        game_running = True

        # Emit initial game state
        socketio.emit('game_state_update', game_state)

        # Game loop
        while game_running:
            try:
                # Check for player input (non-blocking)
                try:
                    player_input = player_input_queue.get_nowait()

                    if player_input.lower() == "exit":
                        game_running = False
                        break

                    # Mark as processing
                    game_state["processing"] = True
                    game_state["agent_debug"].append(f"Processing command: {player_input}")
                    logger.info(f"Processing command: {player_input}")

                    # Record start time for performance metrics
                    start_time = time.time()

                    # Process the player input and store the response
                    try:
                        with command_lock:
                            game_state["agent_debug"].append(f"Processing command with game instance: {player_input}")
                            dm_response = game_instance.process_player_input(player_input)
                            game_state["agent_debug"].append("Command processed successfully")
                            logger.info("Command processed successfully")
                    except Exception as e:
                        error_msg = f"ERROR: Failed to process command: {str(e)}"
                        game_state["agent_debug"].append(error_msg)
                        game_state["dm_messages"].append("There was an error processing your command. Please try again.")
                        logger.error(error_msg)
                        # Mark as no longer processing
                        game_state["processing"] = False
                        game_state["last_update"] = time.time()
                        continue

                    # Add DM response to messages
                    try:
                        if dm_response:
                            game_state["dm_messages"].append(dm_response)
                            game_state["agent_debug"].append(f"Added DM response: {dm_response[:50]}...")
                            logger.info(f"Added DM response: {dm_response[:50]}...")
                    except Exception as e:
                        error_msg = f"ERROR: Failed to add DM response: {str(e)}"
                        game_state["agent_debug"].append(error_msg)
                        logger.error(error_msg)

                    # Update game state
                    try:
                        updated_context = game_instance.get_simplified_context()
                        game_state["player"] = updated_context.get("player", {})
                        game_state["environment"] = updated_context.get("environment", {})
                        game_state["world"] = updated_context.get("world", {})
                        game_state["exploration"] = updated_context.get("exploration", {})
                        game_state["agent_debug"].append("Updated game state after command")
                        logger.info("Updated game state after command")
                    except Exception as e:
                        error_msg = f"ERROR: Failed to update game state after command: {str(e)}"
                        game_state["agent_debug"].append(error_msg)
                        logger.error(error_msg)

                    # Calculate processing time
                    processing_time = time.time() - start_time

                    # Update performance metrics
                    performance_metrics["command_processing_times"].append(processing_time)
                    performance_metrics["total_commands"] += 1

                    # Keep only the last 10 processing times
                    if len(performance_metrics["command_processing_times"]) > 10:
                        performance_metrics["command_processing_times"] = performance_metrics["command_processing_times"][-10:]

                    # Calculate average processing time
                    performance_metrics["avg_processing_time"] = sum(performance_metrics["command_processing_times"]) / len(performance_metrics["command_processing_times"])

                    # Add debug message with performance info
                    game_state["agent_debug"].append(f"Command processed in {processing_time:.2f}s (avg: {performance_metrics['avg_processing_time']:.2f}s)")
                    logger.info(f"Command processed in {processing_time:.2f}s (avg: {performance_metrics['avg_processing_time']:.2f}s)")

                    # Mark as no longer processing
                    game_state["processing"] = False
                    game_state["last_update"] = time.time()

                    # Emit updated game state
                    socketio.emit('game_state_update', game_state)

                except queue.Empty:
                    # No input, continue
                    pass

                # Update game state periodically even without commands
                if not game_state["processing"] and time.time() - game_state.get("last_update", 0) > 5:
                    # Refresh game state occasionally to catch any background changes
                    updated_context = game_instance.get_simplified_context()

                    # Update player data with full character information
                    player_data = updated_context.get("player", {})
                    if player_data:
                        # Ensure all character fields are included
                        game_state["player"] = player_data

                    game_state["environment"] = updated_context.get("environment", {})
                    game_state["world"] = updated_context.get("world", {})
                    game_state["exploration"] = updated_context.get("exploration", {})
                    game_state["last_update"] = time.time()

                    # Emit updated game state
                    socketio.emit('game_state_update', game_state)

            except Exception as e:
                # Log any errors
                error_msg = f"Error in game loop: {str(e)}"
                game_state["agent_debug"].append(error_msg)
                logger.error(error_msg)
                game_state["processing"] = False

            # Sleep to prevent CPU hogging (shorter sleep for better responsiveness)
            time.sleep(0.05)

    finally:
        # Restore original print function
        builtins.print = original_print
        game_running = False
        logger.info("Game thread stopped")

# API Routes
@app.route('/api/status')
def api_status():
    """API endpoint to check the status of services"""
    try:
        import pymongo
        import redis
        import requests

        status = {
            "mongodb": {
                "connected": False,
                "collections": 0,
                "databaseName": "",
                "databaseSize": "0 MB"
            },
            "redis": {
                "connected": False,
                "usedMemory": "0 MB",
                "totalKeys": 0,
                "uptime": 0
            },
            "chroma": {
                "connected": False,
                "collections": 0,
                "embeddings": 0,
                "version": ""
            },
            "socketio": {
                "connected": True,
                "clients": len(socketio.server.eio.sockets) if hasattr(socketio, 'server') else 0
            }
        }

        # Check MongoDB connection
        try:
            mongodb_uri = os.environ.get('MONGODB_URI', "mongodb://admin:password@mongodb:27017/rpger?authSource=admin")
            mongo_client = pymongo.MongoClient(mongodb_uri, serverSelectionTimeoutMS=2000)
            mongo_client.server_info()  # Will raise exception if cannot connect
            db = mongo_client["rpger"]

            # Get collections
            collections = db.list_collection_names()

            status["mongodb"]["connected"] = True
            status["mongodb"]["collections"] = len(collections)
            status["mongodb"]["databaseName"] = "rpger"

            # Estimate database size (this is approximate)
            db_stats = db.command("dbStats")
            size_mb = round(db_stats.get("storageSize", 0) / (1024 * 1024), 2)
            status["mongodb"]["databaseSize"] = f"{size_mb} MB"

        except Exception as e:
            logger.error(f"MongoDB connection error: {e}")

        # Check Redis connection
        try:
            redis_url = os.environ.get('REDIS_URL', "redis://:password@redis:6379")
            redis_client = redis.from_url(redis_url, socket_timeout=2)
            if redis_client.ping():
                status["redis"]["connected"] = True

                # Get Redis info
                info = redis_client.info()
                status["redis"]["usedMemory"] = info.get("used_memory_human", "0 MB")
                status["redis"]["uptime"] = info.get("uptime_in_seconds", 0)

                # Get total keys
                status["redis"]["totalKeys"] = redis_client.dbsize()
        except Exception as e:
            logger.error(f"Redis connection error: {e}")

        # Check Chroma connection
        try:
            # Chroma API endpoint for heartbeat
            chroma_response = requests.get("http://chroma:8000/api/v2/heartbeat", timeout=2)

            if chroma_response.status_code == 200:
                status["chroma"]["connected"] = True
                status["chroma"]["version"] = "latest"  # Chroma doesn't expose version in API

                # Try to get collections info
                try:
                    collections_response = requests.get("http://chroma:8000/api/v2/collections", timeout=2)
                    if collections_response.status_code == 200:
                        collections_data = collections_response.json()
                        status["chroma"]["collections"] = len(collections_data)

                        # Count total embeddings across all collections
                        total_embeddings = 0
                        for collection in collections_data:
                            try:
                                collection_id = collection.get("id")
                                if collection_id:
                                    count_response = requests.get(f"http://chroma:8000/api/v2/collections/{collection_id}/count", timeout=2)
                                    if count_response.status_code == 200:
                                        count_data = count_response.json()
                                        total_embeddings += count_data.get("count", 0)
                            except Exception as e:
                                logger.error(f"Error getting collection count: {e}")

                        status["chroma"]["embeddings"] = total_embeddings
                except Exception as e:
                    logger.error(f"Error getting Chroma collections: {e}")
        except Exception as e:
            logger.error(f"Chroma connection error: {e}")

        return jsonify(status)
    except Exception as e:
        logger.error(f"Error in status endpoint: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/socketio-status')
def socketio_status():
    """Simple endpoint to check if Socket.IO server is running"""
    return jsonify({
        "status": "ok",
        "version": "5.3.6",  # Hardcoded version from requirements.txt
        "clients": len(socketio.server.eio.sockets) if hasattr(socketio, 'server') else 0
    })

# Socket.IO event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f'Client connected: {request.sid}')
    emit('response', {'message': 'Connected to RPGer backend'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f'Client disconnected: {request.sid}')

@socketio.on('command')
def handle_command(data):
    """Handle player command"""
    global game_running, game_instance

    logger.info(f'Received command from {request.sid}: {data}')
    logger.info(f'Game running: {game_running}, Game instance exists: {game_instance is not None}')

    if not game_running or not game_instance:
        logger.warning(f'Game not running or game instance is None. Starting game automatically.')

        # Auto-start the game with default mode
        game_state["dm_messages"].append(f"The DM acknowledges your command: {data.get('command', '')}")
        game_state["dm_messages"].append(f"Starting a new game session...")

        # Initialize game state with some default values if they don't exist
        if "player" not in game_state:
            game_state["player"] = {
                "name": "Test Character",
                "race": "Human",
                "class": "Fighter",
                "level": 1,
                "hp": 10,
                "max_hp": 10,
                "stats": {"STR": 16, "DEX": 14, "CON": 15, "INT": 12, "WIS": 10, "CHA": 8}
            }

        if "environment" not in game_state:
            game_state["environment"] = {
                "location": "Test Dungeon",
                "description": "A dark, damp dungeon with stone walls.",
                "creatures": []
            }

        if "world" not in game_state:
            game_state["world"] = {
                "time": {"day": 1, "hour": 12},
                "weather": {"condition": "Clear"},
                "light": {"level": "Dim"}
            }

        # Add some initial DM messages if there aren't any
        if len(game_state["dm_messages"]) < 3:
            game_state["dm_messages"].append("You feel like you're being watched.")
            game_state["dm_messages"].append("The torch flickers.")
            game_state["dm_messages"].append("A cold breeze blows through the dungeon.")

        # Emit updated game state
        logger.info(f"Emitting initial game state with {len(game_state['dm_messages'])} DM messages")
        socketio.emit('game_state_update', game_state)
        logger.info("Initial game state update emitted")

        # Try to start the game
        try:
            # Create a game thread and start it
            game_state["mode"] = "standard"  # Set the mode

            # Start game in a separate thread
            game_thread = threading.Thread(target=run_game)
            game_thread.daemon = True
            game_thread.start()

            logger.info("Game started successfully")
            game_state["dm_messages"].append("Game started successfully. You can now interact with the world.")
            socketio.emit('game_state_update', game_state)
        except Exception as e:
            logger.error(f"Failed to start game: {str(e)}")
            game_state["dm_messages"].append(f"There was an issue starting the game, but you can still interact with the DM.")
            socketio.emit('game_state_update', game_state)

        # Continue processing the command
        command = data.get('command', '')
        if not command:
            emit('error', {'message': 'No command provided'})
            return

    command = data.get('command', '')
    if not command:
        emit('error', {'message': 'No command provided'})
        return

    try:
        # Add command to debug log
        game_state["agent_debug"].append(f"Command received: {command}")

        # Add DM response directly to game state
        game_state["dm_messages"].append(f"The DM acknowledges your command: {command}")
        logger.info(f"Added DM message: The DM acknowledges your command: {command}")
        logger.info(f"Current DM messages: {game_state['dm_messages']}")

        # Put command in queue
        player_input_queue.put(command)

        # Emit updated game state immediately
        logger.info(f"Emitting game state update with {len(game_state['dm_messages'])} DM messages")
        socketio.emit('game_state_update', game_state)
        logger.info("Game state update emitted")

        emit('command_received', {'status': 'success'})
    except Exception as e:
        error_msg = f'Error processing command: {str(e)}'
        logger.error(error_msg)
        emit('error', {'message': error_msg})

@socketio.on('start_game')
def handle_start_game(data):
    """Start the game"""
    global game_running, game_state, game_instance

    logger.info(f'Received start_game request from {request.sid}: {data}')

    # If a game is already running, stop it first
    if game_running:
        logger.info("Game already running, stopping it first")
        game_running = False
        # Wait a moment for the game thread to clean up
        time.sleep(0.5)
        # Reset game instance
        game_instance = None
        logger.info("Game instance reset")

    # Get mode from request
    try:
        mode = data.get('mode', 'standard')
        logger.info(f"Starting game with mode: {mode}")
    except Exception as e:
        error_msg = f"ERROR parsing request data: {str(e)}"
        logger.error(error_msg)
        emit('error', {'message': error_msg})
        return

    if not game_running:
        # Reset game state
        game_state = {
            "player": {},
            "environment": {
                "location": "",
                "description": "",
                "creatures": []
            },
            "world": {
                "time": {},
                "weather": {},
                "light": {},
                "resources": {}
            },
            "exploration": {},
            "action_results": [],
            "dm_messages": ["Welcome to AD&D 1st Edition! The Dungeon Master will guide you through your adventure."],
            "agent_debug": [
                "System: Game initialization started...",
                "System: Preparing agent debug interface...",
                "System: Agent debug interface ready"
            ],
            "mode": mode,  # Store the mode in the game state
            "processing": False,  # Initialize processing flag
            "last_update": time.time()  # Initialize last update timestamp
        }

        # Add mode-specific welcome messages
        if mode == 'create_character':
            game_state["dm_messages"].append("You've selected Character Creation. The system will guide you through creating your AD&D character step by step.")
        elif mode == 'create_campaign':
            game_state["dm_messages"].append("You've selected Campaign Creation. The system will guide you through creating your AD&D campaign.")
        elif mode == 'continue_campaign':
            game_state["dm_messages"].append("You've selected Continue Campaign. The system will help you load and continue an existing campaign.")
        elif mode == 'random_encounter':
            game_state["dm_messages"].append("You've selected Random Encounter. The system will generate a random encounter for you to play through.")

        # Start game in a separate thread
        try:
            game_state["agent_debug"].append(f"Starting game thread with mode: {mode}")
            logger.info(f"Starting game thread with mode: {mode}")

            # Create the thread
            game_thread = threading.Thread(target=run_game)
            game_thread.daemon = True

            # Start the thread
            logger.info("Starting game thread...")
            game_thread.start()

            # Check if thread started
            if game_thread.is_alive():
                logger.info("Game thread is alive")
                game_state["agent_debug"].append("Game thread started successfully and is alive")
            else:
                logger.warning("Game thread started but is not alive")
                game_state["agent_debug"].append("WARNING: Game thread started but is not alive")

            # Add more debug info
            game_state["agent_debug"].append(f"Thread ID: {game_thread.ident}")
            logger.info(f"Thread ID: {game_thread.ident}")
        except Exception as e:
            error_msg = f"ERROR: Failed to start game thread: {str(e)}"
            game_state["agent_debug"].append(error_msg)
            logger.error(error_msg)
            import traceback
            trace = traceback.format_exc()
            game_state["agent_debug"].append(f"Traceback: {trace}")
            logger.error(trace)
            emit('error', {'message': f"Failed to start game: {str(e)}"})
            return

        # Wait for game to initialize
        max_wait = 15  # seconds
        start_time = time.time()
        initialized = False

        game_state["agent_debug"].append(f"Waiting for game to initialize (timeout: {max_wait}s)")
        logger.info(f"Waiting for game to initialize (timeout: {max_wait}s)")

        wait_iterations = 0
        while time.time() - start_time < max_wait:
            wait_iterations += 1

            # Log progress every few iterations
            if wait_iterations % 5 == 0:
                elapsed = time.time() - start_time
                logger.info(f"Still waiting for initialization... {elapsed:.1f}s elapsed")
                game_state["agent_debug"].append(f"Still waiting... {elapsed:.1f}s elapsed")

            # Check if player data is available or if we're in a special mode
            if (game_state.get("player") and game_state["player"].get("name")) or mode in ['create_campaign', 'create_character', 'continue_campaign', 'random_encounter']:
                initialized = True
                game_state["agent_debug"].append("Game initialized successfully")
                logger.info("Game initialized successfully")
                break

            # Check if game thread is still alive
            if not game_thread.is_alive():
                error_msg = "ERROR: Game thread died during initialization"
                game_state["agent_debug"].append(error_msg)
                logger.error(error_msg)
                emit('error', {'message': "Game thread died during initialization"})
                return

            time.sleep(0.5)

        if initialized:
            game_state["agent_debug"].append("Game initialized successfully!")
            logger.info("Game initialized successfully!")

            # Add more detailed success information
            success_response = {
                "status": "success",
                "message": "Game started",
                "mode": mode,
                "thread_alive": game_thread.is_alive(),
                "thread_id": game_thread.ident,
                "initialization_time": time.time() - start_time
            }

            logger.info(f"Returning success response: {success_response}")
            emit('game_started', success_response)
        else:
            error_msg = "Game initialization timed out!"
            game_state["agent_debug"].append(error_msg)
            logger.error(error_msg)

            # Add more detailed error information
            error_response = {
                "status": "error",
                "message": "Game initialization timed out",
                "thread_alive": game_thread.is_alive() if 'game_thread' in locals() else False,
                "elapsed_time": time.time() - start_time,
                "debug_messages": game_state.get("agent_debug", [])[-5:] # Last 5 debug messages
            }

            logger.info(f"Returning error response: {error_response}")
            emit('error', error_response)
    else:
        error_msg = "Game already running"
        logger.error(error_msg)
        emit('error', {'message': error_msg})

@socketio.on('get_game_state')
def handle_get_game_state():
    """Get the current game state"""
    logger.info(f'Received get_game_state request from {request.sid}')

    # Add performance metrics
    response_state = dict(game_state)
    response_state["performance"] = {
        "avg_processing_time": performance_metrics["avg_processing_time"],
        "total_commands": performance_metrics["total_commands"],
        "is_processing": game_state.get("processing", False)
    }

    # Add server timestamp
    response_state["server_time"] = time.time()

    emit('game_state_update', response_state)

# Add a debug message endpoint
@app.route('/api/debug', methods=['POST'])
def add_debug_message():
    """API endpoint to add a debug message"""
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({"error": "No message provided"}), 400

        message = data['message']
        agent = data.get('agent', 'System')
        level = data.get('level', 'info')

        # Format the message
        if agent != 'System':
            formatted_message = f"{agent}: {message}"
        else:
            formatted_message = f"System: {message}"

        # Add level prefix if not already present
        if level == 'error' and not formatted_message.startswith('ERROR:'):
            formatted_message = f"ERROR: {formatted_message}"
        elif level == 'warning' and not formatted_message.startswith('WARNING:'):
            formatted_message = f"WARNING: {formatted_message}"

        # Add to game state
        game_state["agent_debug"].append(formatted_message)

        # Limit to last 50 messages
        if len(game_state["agent_debug"]) > 50:
            game_state["agent_debug"] = game_state["agent_debug"][-50:]

        # Emit via Socket.IO
        socketio.emit('debug_message', formatted_message)

        return jsonify({"status": "success", "message": "Debug message added"})
    except Exception as e:
        logger.error(f"Error adding debug message: {e}")
        return jsonify({"error": str(e)}), 500

# Socket.IO event handler for debug messages
@socketio.on('send_debug')
def handle_debug_message(data):
    """Handle debug message from client"""
    try:
        if not data or 'message' not in data:
            emit('error', {'message': 'No message provided'})
            return

        message = data['message']
        agent = data.get('agent', 'System')
        level = data.get('level', 'info')

        # Format the message
        if agent != 'System':
            formatted_message = f"{agent}: {message}"
        else:
            formatted_message = f"System: {message}"

        # Add level prefix if not already present
        if level == 'error' and not formatted_message.startswith('ERROR:'):
            formatted_message = f"ERROR: {formatted_message}"
        elif level == 'warning' and not formatted_message.startswith('WARNING:'):
            formatted_message = f"WARNING: {formatted_message}"

        # Add to game state
        game_state["agent_debug"].append(formatted_message)

        # Limit to last 50 messages
        if len(game_state["agent_debug"]) > 50:
            game_state["agent_debug"] = game_state["agent_debug"][-50:]

        # Emit to all clients
        socketio.emit('debug_message', formatted_message)

        emit('response', {'status': 'success', 'message': 'Debug message sent'})
    except Exception as e:
        logger.error(f"Error handling debug message: {e}")
        emit('error', {'message': str(e)})

# Main entry point
if __name__ == '__main__':
    # Start the SocketIO server
    logger.info("Starting Flask-SocketIO server on http://0.0.0.0:5002")
    socketio.run(app, host='0.0.0.0', port=5002, debug=True, allow_unsafe_werkzeug=True)
