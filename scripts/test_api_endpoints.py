#!/usr/bin/env python3
"""
API Endpoint Testing Script for RPGer

This script tests all documented API endpoints to verify they are working correctly.

Usage:
    python test_api_endpoints.py [--host HOST] [--port PORT] [--verbose]

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
import socket
import random
import string

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_api_endpoints')

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

def test_api_endpoint(base_url, endpoint, method="GET", data=None, expected_status=200, verbose=False):
    """Test an API endpoint and return the result"""
    url = urljoin(base_url, endpoint)
    name = f"API Endpoint: {method} {endpoint}"
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=5)
        elif method == "DELETE":
            response = requests.delete(url, timeout=5)
        else:
            print_result(name, False, f"Unsupported method: {method}")
            return False, None
        
        elapsed_time = time.time() - start_time
        
        success = response.status_code == expected_status
        
        if success:
            message = f"Status: {response.status_code}, Time: {elapsed_time:.2f}s"
            try:
                details = response.json() if response.headers.get('content-type') == 'application/json' else response.text
            except:
                details = response.text
        else:
            message = f"Expected status {expected_status}, got {response.status_code}, Time: {elapsed_time:.2f}s"
            details = response.text
        
        print_result(name, success, message, details, verbose)
        return success, response
    
    except requests.exceptions.RequestException as e:
        print_result(name, False, f"Error: {str(e)}")
        return False, None

def test_socketio_connection(host, port, verbose=False):
    """Test Socket.IO connection"""
    name = "Socket.IO Connection"
    
    try:
        # Try to connect to the Socket.IO server using a raw socket
        # This is a simple check to see if the port is open
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        
        start_time = time.time()
        result = sock.connect_ex((host, int(port)))
        elapsed_time = time.time() - start_time
        
        sock.close()
        
        if result == 0:
            message = f"Socket.IO port is open, Time: {elapsed_time:.2f}s"
            print_result(name, True, message, None, verbose)
            return True
        else:
            message = f"Socket.IO port is closed, Time: {elapsed_time:.2f}s"
            print_result(name, False, message, None, verbose)
            return False
    
    except Exception as e:
        print_result(name, False, f"Error: {str(e)}")
        return False

def test_mongodb_api(base_url, verbose=False):
    """Test MongoDB-related API endpoints"""
    print_header("Testing MongoDB API Endpoints")
    
    endpoints = [
        "/api/status",  # General status endpoint that includes MongoDB status
        "/api/collections",  # List collections
        "/api/collections/monsters"  # Get monsters collection
    ]
    
    results = []
    for endpoint in endpoints:
        success, _ = test_api_endpoint(base_url, endpoint, verbose=verbose)
        results.append(success)
    
    return results

def test_redis_api(base_url, verbose=False):
    """Test Redis-related API endpoints"""
    print_header("Testing Redis API Endpoints")
    
    endpoints = [
        "/api/status",  # General status endpoint that includes Redis status
        "/api/socketio-status"  # Socket.IO status (uses Redis for pub/sub)
    ]
    
    results = []
    for endpoint in endpoints:
        success, _ = test_api_endpoint(base_url, endpoint, verbose=verbose)
        results.append(success)
    
    return results

def test_chroma_api(base_url, verbose=False):
    """Test Chroma-related API endpoints"""
    print_header("Testing Chroma API Endpoints")
    
    endpoints = [
        "/api/status"  # General status endpoint that includes Chroma status
    ]
    
    results = []
    for endpoint in endpoints:
        success, _ = test_api_endpoint(base_url, endpoint, verbose=verbose)
        results.append(success)
    
    return results

def test_health_api(base_url, verbose=False):
    """Test health-related API endpoints"""
    print_header("Testing Health API Endpoints")
    
    endpoints = [
        "/api/health",
        "/api/status",
        "/api/socketio-status"
    ]
    
    results = []
    for endpoint in endpoints:
        success, _ = test_api_endpoint(base_url, endpoint, verbose=verbose)
        results.append(success)
    
    return results

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Test API endpoints for RPGer')
    parser.add_argument('--host', default='localhost', help='Host address of the RPG web app')
    parser.add_argument('--port', default='5002', help='Port of the RPG web app')
    parser.add_argument('--verbose', action='store_true', help='Show detailed information about each test')
    args = parser.parse_args()
    
    base_url = f"http://{args.host}:{args.port}"
    
    print_header("RPGer API Endpoint Testing")
    print(f"Testing endpoints at {base_url}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test Socket.IO connection
    socketio_success = test_socketio_connection(args.host, args.port, verbose=args.verbose)
    
    # Test health API endpoints
    health_results = test_health_api(base_url, verbose=args.verbose)
    
    # Test MongoDB API endpoints
    mongodb_results = test_mongodb_api(base_url, verbose=args.verbose)
    
    # Test Redis API endpoints
    redis_results = test_redis_api(base_url, verbose=args.verbose)
    
    # Test Chroma API endpoints
    chroma_results = test_chroma_api(base_url, verbose=args.verbose)
    
    # Summary
    print_header("Test Summary")
    
    health_success_count = sum(health_results)
    health_success_rate = (health_success_count / len(health_results)) * 100 if health_results else 0
    
    mongodb_success_count = sum(mongodb_results)
    mongodb_success_rate = (mongodb_success_count / len(mongodb_results)) * 100 if mongodb_results else 0
    
    redis_success_count = sum(redis_results)
    redis_success_rate = (redis_success_count / len(redis_results)) * 100 if redis_results else 0
    
    chroma_success_count = sum(chroma_results)
    chroma_success_rate = (chroma_success_count / len(chroma_results)) * 100 if chroma_results else 0
    
    print(f"Socket.IO Connection: {'✅ PASS' if socketio_success else '❌ FAIL'}")
    print(f"Health API Endpoints: {health_success_count}/{len(health_results)} passed ({health_success_rate:.1f}%)")
    print(f"MongoDB API Endpoints: {mongodb_success_count}/{len(mongodb_results)} passed ({mongodb_success_rate:.1f}%)")
    print(f"Redis API Endpoints: {redis_success_count}/{len(redis_results)} passed ({redis_success_rate:.1f}%)")
    print(f"Chroma API Endpoints: {chroma_success_count}/{len(chroma_results)} passed ({chroma_success_rate:.1f}%)")
    
    # Overall result
    all_results = health_results + mongodb_results + redis_results + chroma_results
    all_success_count = sum(all_results)
    all_success_rate = (all_success_count / len(all_results)) * 100 if all_results else 0
    
    print(f"\nOverall: {all_success_count}/{len(all_results)} passed ({all_success_rate:.1f}%)")
    
    # Conclusion
    print("\nConclusion:")
    if all_success_rate >= 90:
        print_colored("✅ API endpoints are working correctly.", Colors.GREEN + Colors.BOLD)
        if not socketio_success:
            print_colored("⚠️ Socket.IO connection failed, but other endpoints are working.", Colors.YELLOW)
    elif all_success_rate >= 50:
        print_colored("⚠️ Some API endpoints are working, but there are issues.", Colors.YELLOW + Colors.BOLD)
    else:
        print_colored("❌ Most API endpoints are not working.", Colors.RED + Colors.BOLD)
    
    # Database-specific conclusions
    if mongodb_success_rate < 50:
        print_colored("❌ MongoDB API endpoints are not working correctly.", Colors.RED)
        print("   This suggests issues with the MongoDB connection.")
    
    if redis_success_rate < 50:
        print_colored("❌ Redis API endpoints are not working correctly.", Colors.RED)
        print("   This suggests issues with the Redis connection.")
    
    if chroma_success_rate < 50:
        print_colored("❌ Chroma API endpoints are not working correctly.", Colors.RED)
        print("   This suggests issues with the Chroma connection.")
    
    # Exit with appropriate status code
    if all_success_rate < 50:
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()
