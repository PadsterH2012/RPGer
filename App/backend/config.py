"""
Configuration module for RPGer backend.

This module loads environment variables from a .env file and provides
functions to access configuration values.
"""

import os
import logging
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger('RPGerConfig')

# Load environment variables from .env file
load_dotenv()

def get_openrouter_api_key():
    """
    Get the OpenRouter API key from environment variables.
    
    Returns:
        str: The OpenRouter API key, or None if not found.
    """
    api_key = os.getenv('OPENROUTER_API_KEY')
    
    if not api_key:
        logger.warning("OpenRouter API key not found in environment variables.")
        return None
    
    return api_key

def get_config_value(key, default=None):
    """
    Get a configuration value from environment variables.
    
    Args:
        key (str): The environment variable key.
        default: The default value to return if the key is not found.
        
    Returns:
        The value of the environment variable, or the default value if not found.
    """
    return os.getenv(key, default)
