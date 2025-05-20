#!/usr/bin/env python3
"""
Chroma Database Initialization Script for RPGer

This script initializes the Chroma vector database with the required
tenant and database configuration.

Usage:
    python init_chroma.py [--host HOST] [--port PORT] [--verbose]

Options:
    --host HOST     Host address of the Chroma server (default: localhost)
    --port PORT     Port of the Chroma server (default: 8000)
    --verbose       Show detailed information
"""

import os
import sys
import argparse
import logging
import time
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('init_chroma')

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

def initialize_chroma(host, port, verbose=False):
    """Initialize Chroma with required configuration"""
    if not CHROMA_AVAILABLE:
        print_colored("Chroma client not available. Install with: pip install chromadb", Colors.RED)
        return False

    try:
        if verbose:
            print(f"Connecting to Chroma at {host}:{port}")

        # Connect to Chroma as admin client
        # Based on Chroma documentation, we need to use AdminClient for tenant management
        try:
            from chromadb.config import Settings
            settings = Settings(
                chroma_api_impl="chromadb.api.fastapi.FastAPI",
                chroma_server_host=host,
                chroma_server_http_port=port
            )

            if verbose:
                print("Creating admin client...")

            # Try to create an admin client
            admin_client = chromadb.AdminClient(settings)

            if verbose:
                print("Admin client created successfully")

            # Check if connection works
            heartbeat = admin_client.heartbeat()
            if verbose:
                print(f"Connected to Chroma. Heartbeat: {heartbeat}")

            # Create default tenant
            if verbose:
                print("Creating default_tenant...")

            try:
                admin_client.create_tenant("default_tenant")
                if verbose:
                    print("default_tenant created successfully")
            except Exception as e:
                if "already exists" in str(e).lower():
                    if verbose:
                        print("default_tenant already exists")
                else:
                    raise e

            # Create default database
            if verbose:
                print("Creating default_database in default_tenant...")

            try:
                admin_client.create_database("default_database", "default_tenant")
                if verbose:
                    print("default_database created successfully")
            except Exception as e:
                if "already exists" in str(e).lower():
                    if verbose:
                        print("default_database already exists")
                else:
                    raise e

        except Exception as admin_e:
            if verbose:
                print(f"Admin client approach failed: {str(admin_e)}")
                print("Falling back to standard HttpClient...")

            # Connect to Chroma using standard HttpClient
            client = chromadb.HttpClient(host=host, port=port)

            # Check if connection works
            heartbeat = client.heartbeat()
            if verbose:
                print(f"Connected to Chroma. Heartbeat: {heartbeat}")

            # Try to create default tenant if it doesn't exist
            try:
                if verbose:
                    print("Checking for default_tenant...")

                # This will throw an exception if the tenant doesn't exist
                client.get_tenant("default_tenant")

                if verbose:
                    print("default_tenant already exists")
            except Exception as e:
                if "Could not find tenant" in str(e) or "not found" in str(e).lower():
                    if verbose:
                        print("Creating default_tenant...")

                    # Create the default tenant
                    client.create_tenant("default_tenant")

                    if verbose:
                        print("default_tenant created successfully")
                else:
                    # Some other error occurred
                    raise e

            # Try to create default database if it doesn't exist
            try:
                if verbose:
                    print("Checking for default_database...")

                # This will throw an exception if the database doesn't exist
                client.get_database("default_database", "default_tenant")

                if verbose:
                    print("default_database already exists")
            except Exception as e:
                if "Could not find database" in str(e) or "not found" in str(e).lower():
                    if verbose:
                        print("Creating default_database...")

                    # Create the default database
                    client.create_database("default_database", "default_tenant")

                    if verbose:
                        print("default_database created successfully")
                else:
                    # Some other error occurred
                    raise e

        # Create a test collection to verify everything works
        try:
            if verbose:
                print("Creating test collection...")

            # Create a standard client to work with collections
            standard_client = chromadb.HttpClient(host=host, port=port)

            # Set the tenant and database
            standard_client.set_tenant("default_tenant")

            if verbose:
                print("Set tenant to default_tenant")

            # Create a test collection
            try:
                collection = standard_client.create_collection("test_collection")

                if verbose:
                    print("Test collection created")

                # Add a test item
                collection.add(
                    documents=["This is a test document"],
                    metadatas=[{"source": "initialization"}],
                    ids=["test1"]
                )

                if verbose:
                    print("Added test document to collection")

                # Query to verify it works
                results = collection.query(
                    query_texts=["test"],
                    n_results=1
                )

                if verbose:
                    print(f"Test collection queried successfully: {results}")

                # Clean up the test collection
                standard_client.delete_collection("test_collection")

                if verbose:
                    print("Test collection deleted")
            except Exception as coll_e:
                if verbose:
                    print(f"Error with test collection: {str(coll_e)}")
                    print("This is not critical - tenant and database were created")
        except Exception as e:
            if verbose:
                print(f"Error testing collection: {str(e)}")
                print("This is not critical - tenant and database were created")

        print_colored("Chroma initialization completed successfully!", Colors.GREEN)
        return True

    except Exception as e:
        print_colored(f"Error initializing Chroma: {str(e)}", Colors.RED)
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Initialize Chroma for RPGer')
    parser.add_argument('--host', default='localhost', help='Host address of the Chroma server')
    parser.add_argument('--port', default='8000', help='Port of the Chroma server')
    parser.add_argument('--verbose', action='store_true', help='Show detailed information')
    args = parser.parse_args()

    print_header("RPGer Chroma Initialization")
    print(f"Initializing Chroma at {args.host}:{args.port}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    success = initialize_chroma(args.host, args.port, args.verbose)

    if success:
        print_colored("\nChroma initialization completed successfully!", Colors.GREEN)
        sys.exit(0)
    else:
        print_colored("\nChroma initialization failed.", Colors.RED)
        sys.exit(1)

if __name__ == "__main__":
    main()
