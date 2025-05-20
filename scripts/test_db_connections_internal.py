#!/usr/bin/env python3
"""
Internal Database Connection Testing Script for RPGer

This script tests connections to MongoDB, Redis, and Chroma
from within the backend container to verify internal networking.

Usage:
    python test_db_connections_internal.py [--verbose]

Options:
    --verbose       Show detailed information about each test
"""

import os
import sys
import json
import time
import argparse
import logging
from dotenv import load_dotenv
import pymongo
import redis
try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_db_connections_internal')

# Load environment variables if .env file exists
env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        'app_stack', 'backend', '.env')
if os.path.exists(env_file):
    load_dotenv(env_file)
    logger.info(f"Loaded environment variables from {env_file}")

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_colored(text, color):
    """Print colored text to the terminal"""
    print(f"{color}{text}{Colors.END}")

def print_header(text):
    """Print a header to the terminal"""
    print("\n" + "=" * 80)
    print_colored(f" {text} ", Colors.BLUE + Colors.BOLD)
    print("=" * 80)

def print_result(name, success, message="", details=None, verbose=False):
    """Print a test result to the terminal"""
    status = f"{Colors.GREEN}PASS{Colors.END}" if success else f"{Colors.RED}FAIL{Colors.END}"
    print(f"[{status}] {name}")

    if message:
        print(f"       {message}")

    if details and verbose:
        if isinstance(details, dict) or isinstance(details, list):
            details_str = json.dumps(details, indent=2)
            print(f"       Details: {details_str}")
        else:
            print(f"       Details: {details}")

def test_mongodb_internal(verbose=False):
    """Test connection to MongoDB from within the container"""
    name = "Internal MongoDB Connection"

    # Get MongoDB connection parameters from environment or use container name
    mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://admin:password@mongodb:27017/rpger?authSource=admin')

    try:
        # Mask password in logs
        masked_uri = mongodb_uri
        if '@' in mongodb_uri:
            prefix = mongodb_uri.split('@')[0]
            suffix = mongodb_uri.split('@')[1]
            if ':' in prefix:
                masked_uri = f"{prefix.split(':')[0]}:***@{suffix}"

        # Log connection details if verbose
        if verbose:
            print(f"       Connecting to MongoDB with URI: {masked_uri}")

        start_time = time.time()
        client = pymongo.MongoClient(mongodb_uri, serverSelectionTimeoutMS=5000)
        server_info = client.server_info()
        elapsed_time = time.time() - start_time

        # Get database name from URI
        db_name = 'rpger'
        if '/' in mongodb_uri:
            path_part = mongodb_uri.split('/')[-1]
            if '?' in path_part:
                db_name = path_part.split('?')[0]
            else:
                db_name = path_part

        db = client[db_name]
        collections = db.list_collection_names()

        details = {
            "server_version": server_info.get("version", "unknown"),
            "connection_time": f"{elapsed_time:.2f}s",
            "database": db_name,
            "collections": collections
        }

        message = f"Connected to MongoDB {server_info.get('version', 'unknown')}, Time: {elapsed_time:.2f}s"
        print_result(name, True, message, details, verbose)
        return True

    except Exception as e:
        print_result(name, False, f"Error: {str(e)}")
        return False

def test_redis_internal(verbose=False):
    """Test connection to Redis from within the container"""
    name = "Internal Redis Connection"

    # Get Redis connection parameters from environment or use container name
    redis_url = os.environ.get('REDIS_URL', 'redis://:password@redis:6379')

    try:
        # Mask password in logs
        masked_url = redis_url
        if '@' in redis_url:
            prefix = redis_url.split('@')[0]
            suffix = redis_url.split('@')[1]
            if ':' in prefix and prefix.count(':') > 1:
                parts = prefix.split(':')
                masked_url = f"{parts[0]}:{parts[1]}:***@{suffix}"

        # Log connection details if verbose
        if verbose:
            print(f"       Connecting to Redis with URL: {masked_url}")

        start_time = time.time()
        client = redis.from_url(redis_url, socket_timeout=5)
        ping_result = client.ping()
        elapsed_time = time.time() - start_time

        if ping_result:
            info = client.info()
            details = {
                "redis_version": info.get("redis_version", "unknown"),
                "connection_time": f"{elapsed_time:.2f}s",
                "uptime_in_seconds": info.get("uptime_in_seconds", 0),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory_human": info.get("used_memory_human", "unknown")
            }

            message = f"Connected to Redis {info.get('redis_version', 'unknown')}, Time: {elapsed_time:.2f}s"
            print_result(name, True, message, details, verbose)
            return True
        else:
            print_result(name, False, "Redis ping failed")
            return False

    except Exception as e:
        print_result(name, False, f"Error: {str(e)}")
        return False

def test_chroma_internal(verbose=False):
    """Test connection to Chroma from within the container"""
    name = "Internal Chroma Connection"

    if not CHROMA_AVAILABLE:
        print_result(name, False, "Chroma client not available. Install with: pip install chromadb")
        return False

    # Get Chroma connection parameters from environment or use container name
    chroma_host = os.environ.get('CHROMA_HOST', 'chroma')
    chroma_port = os.environ.get('CHROMA_PORT', '8000')

    # Log connection details if verbose
    if verbose:
        print(f"       Connecting to Chroma at {chroma_host}:{chroma_port}")

    try:
        start_time = time.time()

        # Add more verbose logging
        if verbose:
            print(f"       Attempting to create HttpClient for Chroma at {chroma_host}:{chroma_port}")

        # Create client without specifying tenant
        client = chromadb.HttpClient(
            host=chroma_host,
            port=chroma_port
        )

        if verbose:
            print(f"       HttpClient created successfully, checking heartbeat")

        # Test basic connection with heartbeat
        heartbeat = client.heartbeat()
        elapsed_time = time.time() - start_time

        if verbose:
            print(f"       Heartbeat received: {heartbeat}")

        # For testing purposes, we'll consider a successful heartbeat as a successful connection
        # This is because the tenant/database access is a separate issue
        if heartbeat:
            details = {
                "connection_time": f"{elapsed_time:.2f}s",
                "heartbeat": heartbeat,
                "note": "Heartbeat successful, but tenant/database access may require configuration"
            }

            message = f"Connected to Chroma (heartbeat only), Time: {elapsed_time:.2f}s"
            print_result(name, True, message, details, verbose)
            return True
        else:
            print_result(name, False, "Chroma heartbeat failed")
            return False

    except Exception as e:
        error_message = str(e)

        # Add troubleshooting suggestions based on the error
        troubleshooting = ""
        if "Connection refused" in error_message:
            troubleshooting = "Chroma server may not be running or not accessible from this container"
        elif "tenant" in error_message.lower():
            troubleshooting = "Chroma tenant issue. Try creating a default tenant or check Chroma configuration"
        elif "timeout" in error_message.lower():
            troubleshooting = "Connection timeout. Check network connectivity between containers"

        if troubleshooting and verbose:
            print(f"       Troubleshooting: {troubleshooting}")

        print_result(name, False, f"Error: {error_message}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Test internal database connections for RPGer')
    parser.add_argument('--verbose', action='store_true', help='Show detailed information about each test')
    args = parser.parse_args()

    print_header("RPGer Internal Database Connection Testing")
    print(f"Testing connections from within the container")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Test direct database connections
    print_header("Testing Internal Database Connections")

    mongodb_success = test_mongodb_internal(verbose=args.verbose)
    redis_success = test_redis_internal(verbose=args.verbose)
    chroma_success = test_chroma_internal(verbose=args.verbose)

    # Summary
    print_header("Test Summary")

    print(f"MongoDB Connection: {'✅ PASS' if mongodb_success else '❌ FAIL'}")
    print(f"Redis Connection: {'✅ PASS' if redis_success else '❌ FAIL'}")
    print(f"Chroma Connection: {'✅ PASS' if chroma_success else '❌ FAIL'}")

    # Overall result
    db_success = all([mongodb_success, redis_success, chroma_success])

    print("\nConclusion:")
    if db_success:
        print_colored("✅ All internal database connections are working correctly.", Colors.GREEN + Colors.BOLD)
    else:
        print_colored("❌ Some internal database connections failed.", Colors.RED + Colors.BOLD)

        # Provide troubleshooting suggestions
        print("\nTroubleshooting suggestions:")
        if not mongodb_success:
            print("- Check if MongoDB is accessible from the backend container")
            print("- Verify MongoDB connection string in .env file")
            print("- Check MongoDB logs: docker logs mongodb")

        if not redis_success:
            print("- Check if Redis is accessible from the backend container")
            print("- Verify Redis connection string in .env file")
            print("- Check Redis logs: docker logs redis")

        if not chroma_success:
            print("- Check if Chroma is accessible from the backend container")
            print("- Verify Chroma host and port in .env file")
            print("- Check Chroma logs: docker logs chroma")

    # Exit with appropriate status code
    if not db_success:
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
