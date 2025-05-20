#!/usr/bin/env python3
"""
Database Endpoint Testing Script for RPGer

This script tests the documented endpoints for MongoDB, Redis, and Chroma
to verify that the database stack is functioning correctly.

Usage:
    python test_endpoints.py [--host HOST] [--port PORT] [--verbose]

Options:
    --host HOST     Host address of the RPG web app (default: localhost)
    --port PORT     Port of the RPG web app (default: 5002)
    --verbose       Show detailed information about each test
"""

import os
import sys
import json
import time
import argparse
import logging
import requests
from urllib.parse import urljoin
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
logger = logging.getLogger('test_endpoints')

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

def test_api_endpoint(base_url, endpoint, expected_status=200, verbose=False):
    """Test an API endpoint and return the result"""
    url = urljoin(base_url, endpoint)
    name = f"API Endpoint: {endpoint}"

    try:
        start_time = time.time()
        response = requests.get(url, timeout=5)
        elapsed_time = time.time() - start_time

        success = response.status_code == expected_status

        if success:
            message = f"Status: {response.status_code}, Time: {elapsed_time:.2f}s"
            details = response.json() if response.headers.get('content-type') == 'application/json' else response.text
        else:
            message = f"Expected status {expected_status}, got {response.status_code}, Time: {elapsed_time:.2f}s"
            details = response.text

        print_result(name, success, message, details, verbose)
        return success, response

    except requests.exceptions.RequestException as e:
        print_result(name, False, f"Error: {str(e)}")
        return False, None

def test_mongodb_direct(verbose=False):
    """Test direct connection to MongoDB"""
    name = "Direct MongoDB Connection"

    # Get MongoDB connection parameters
    # Always use localhost for direct connection testing from the host machine
    mongodb_uri = 'mongodb://admin:password@localhost:27017/rpger?authSource=admin'

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

def test_redis_direct(verbose=False):
    """Test direct connection to Redis"""
    name = "Direct Redis Connection"

    # Get Redis connection parameters
    # Always use localhost for direct connection testing from the host machine
    redis_url = 'redis://:password@localhost:6379'

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

def test_chroma_direct(verbose=False):
    """Test direct connection to Chroma"""
    name = "Direct Chroma Connection"

    if not CHROMA_AVAILABLE:
        print_result(name, False, "Chroma client not available. Install with: pip install chromadb")
        return False

    # Get Chroma connection parameters
    # Always use localhost for direct connection testing, not container name
    chroma_host = 'localhost'  # Override any env var that might have container name
    chroma_port = '8000'  # Hardcode port for consistency

    # Log connection details if verbose
    if verbose:
        print(f"       Connecting to Chroma at {chroma_host}:{chroma_port}")

    try:
        start_time = time.time()
        client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
        heartbeat = client.heartbeat()
        elapsed_time = time.time() - start_time

        if heartbeat:
            # Try to get collections
            collections = client.list_collections()
            collection_names = [c.name for c in collections]

            details = {
                "connection_time": f"{elapsed_time:.2f}s",
                "heartbeat": heartbeat,
                "collections": collection_names
            }

            message = f"Connected to Chroma, Time: {elapsed_time:.2f}s"
            print_result(name, True, message, details, verbose)
            return True
        else:
            print_result(name, False, "Chroma heartbeat failed")
            return False

    except Exception as e:
        print_result(name, False, f"Error: {str(e)}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Test database endpoints for RPGer')
    parser.add_argument('--host', default='localhost', help='Host address of the RPG web app')
    parser.add_argument('--port', default='5002', help='Port of the RPG web app')
    parser.add_argument('--verbose', action='store_true', help='Show detailed information about each test')
    args = parser.parse_args()

    base_url = f"http://{args.host}:{args.port}"

    print_header("RPGer Database Endpoint Testing")
    print(f"Testing endpoints at {base_url}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # Test API endpoints
    print_header("Testing API Endpoints")

    api_endpoints = [
        "/api/health",
        "/api/status",
        "/api/socketio-status"
    ]

    api_results = []
    for endpoint in api_endpoints:
        success, _ = test_api_endpoint(base_url, endpoint, verbose=args.verbose)
        api_results.append(success)

    # Test direct database connections
    print_header("Testing Direct Database Connections")

    mongodb_success = test_mongodb_direct(verbose=args.verbose)
    redis_success = test_redis_direct(verbose=args.verbose)
    chroma_success = test_chroma_direct(verbose=args.verbose)

    # Summary
    print_header("Test Summary")

    api_success_count = sum(api_results)
    api_success_rate = (api_success_count / len(api_results)) * 100 if api_results else 0

    print(f"API Endpoints: {api_success_count}/{len(api_results)} passed ({api_success_rate:.1f}%)")
    print(f"MongoDB Connection: {'✅ PASS' if mongodb_success else '❌ FAIL'}")
    print(f"Redis Connection: {'✅ PASS' if redis_success else '❌ FAIL'}")
    print(f"Chroma Connection: {'✅ PASS' if chroma_success else '❌ FAIL'}")

    # Overall result
    db_success = all([mongodb_success, redis_success, chroma_success])

    print("\nConclusion:")
    if db_success:
        print_colored("✅ All database connections are working correctly.", Colors.GREEN + Colors.BOLD)
        print_colored("   The issue is not with the database stack.", Colors.GREEN)
    else:
        print_colored("❌ Some database connections failed.", Colors.RED + Colors.BOLD)
        print_colored("   The issue may be with the database stack.", Colors.RED)

        # Provide troubleshooting suggestions
        print("\nTroubleshooting suggestions:")
        if not mongodb_success:
            print("- Check if MongoDB is running: docker ps | grep mongodb")
            print("- Verify MongoDB connection string in .env file")
            print("- Check MongoDB logs: docker logs mongodb")

        if not redis_success:
            print("- Check if Redis is running: docker ps | grep redis")
            print("- Verify Redis connection string in .env file")
            print("- Check Redis logs: docker logs redis")

        if not chroma_success:
            print("- Check if Chroma is running: docker ps | grep chroma")
            print("- Verify Chroma host and port in .env file")
            print("- Check Chroma logs: docker logs chroma")

    # Exit with appropriate status code
    if not db_success:
        sys.exit(1)

    sys.exit(0)

if __name__ == "__main__":
    main()
