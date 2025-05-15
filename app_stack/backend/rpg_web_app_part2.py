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
    
    if not game_running or not game_instance:
        emit('error', {'message': 'Game not running'})
        return
    
    command = data.get('command', '')
    if not command:
        emit('error', {'message': 'No command provided'})
        return
    
    try:
        # Add command to debug log
        game_state["agent_debug"].append(f"Command received: {command}")
        
        # Put command in queue
        player_input_queue.put(command)
        
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
            "agent_debug": ["Game initialization started..."],
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

# Main entry point
if __name__ == '__main__':
    # Start the SocketIO server
    logger.info("Starting Flask-SocketIO server on http://0.0.0.0:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
