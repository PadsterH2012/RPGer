#!/bin/bash

# Script to install dependencies for the RPGer backend

echo "Installing dependencies for RPGer backend..."

# Check if we're in a virtual environment
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "WARNING: Not running in a virtual environment. It's recommended to activate your venv first."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborted. Please activate your virtual environment and try again."
        exit 1
    fi
fi

# Install dependencies
echo "Installing packages from requirements.txt..."
pip install -r requirements.txt

# Check for specific packages that might cause issues
echo "Checking for critical packages..."

# Check for eventlet
if ! pip show eventlet > /dev/null 2>&1; then
    echo "Installing eventlet separately..."
    pip install eventlet==0.33.3
fi

# Check for gevent
if ! pip show gevent > /dev/null 2>&1; then
    echo "Installing gevent separately..."
    pip install gevent==23.9.1
fi

# Check for gevent-websocket
if ! pip show gevent-websocket > /dev/null 2>&1; then
    echo "Installing gevent-websocket separately..."
    pip install gevent-websocket==0.10.1
fi

# Check for simple-websocket
if ! pip show simple-websocket > /dev/null 2>&1; then
    echo "Installing simple-websocket separately..."
    pip install simple-websocket==1.0.0
fi

# Check for redis
if ! pip show redis > /dev/null 2>&1; then
    echo "Installing redis separately..."
    pip install redis==5.0.0
fi

# Check for psutil
if ! pip show psutil > /dev/null 2>&1; then
    echo "Installing psutil separately..."
    pip install psutil==5.9.5
fi

echo "All dependencies installed successfully!"
echo "You can now run the backend server with: python rpg_web_app.py"
