#!/usr/bin/env python3
"""
Direct Chroma Initialization Script for RPGer

This script directly initializes the Chroma vector database with the required
tenant and database configuration using a simplified approach.

Usage:
    python direct_init_chroma.py [--host HOST] [--port PORT] [--verbose]

Options:
    --host HOST     Host address of the Chroma server (default: chroma)
    --port PORT     Port of the Chroma server (default: 8000)
    --verbose       Show detailed information
"""

import sys
import argparse
import logging
import time
import requests
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('direct_init_chroma')

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

def initialize_chroma_direct(host, port, verbose=False):
    """Initialize Chroma with required configuration using direct API calls"""
    try:
        base_url = f"http://{host}:{port}"
        
        if verbose:
            print(f"Connecting to Chroma at {base_url}")
        
        # Check if Chroma is running
        try:
            heartbeat_url = f"{base_url}/api/v2/heartbeat"
            response = requests.get(heartbeat_url)
            response.raise_for_status()
            
            if verbose:
                print(f"Chroma is running. Heartbeat: {response.json()}")
        except Exception as e:
            print_colored(f"Error connecting to Chroma: {str(e)}", Colors.RED)
            return False
        
        # Create default tenant
        try:
            tenant_url = f"{base_url}/api/v2/tenants"
            tenant_data = {"name": "default_tenant"}
            
            if verbose:
                print(f"Creating default_tenant...")
            
            response = requests.post(tenant_url, json=tenant_data)
            
            if response.status_code == 200 or response.status_code == 201:
                if verbose:
                    print("default_tenant created successfully")
            elif response.status_code == 409:
                if verbose:
                    print("default_tenant already exists")
            else:
                response.raise_for_status()
        except Exception as e:
            if "already exists" in str(e).lower():
                if verbose:
                    print("default_tenant already exists")
            else:
                print_colored(f"Error creating default_tenant: {str(e)}", Colors.RED)
                # Continue anyway, as the tenant might already exist
        
        # Create default database
        try:
            database_url = f"{base_url}/api/v2/tenants/default_tenant/databases"
            database_data = {"name": "default_database"}
            
            if verbose:
                print(f"Creating default_database...")
            
            response = requests.post(database_url, json=database_data)
            
            if response.status_code == 200 or response.status_code == 201:
                if verbose:
                    print("default_database created successfully")
            elif response.status_code == 409:
                if verbose:
                    print("default_database already exists")
            else:
                response.raise_for_status()
        except Exception as e:
            if "already exists" in str(e).lower():
                if verbose:
                    print("default_database already exists")
            else:
                print_colored(f"Error creating default_database: {str(e)}", Colors.RED)
                # Continue anyway, as the database might already exist
        
        # Verify that tenant and database exist
        try:
            tenant_url = f"{base_url}/api/v2/tenants/default_tenant"
            response = requests.get(tenant_url)
            response.raise_for_status()
            
            if verbose:
                print("Verified default_tenant exists")
            
            database_url = f"{base_url}/api/v2/tenants/default_tenant/databases/default_database"
            response = requests.get(database_url)
            response.raise_for_status()
            
            if verbose:
                print("Verified default_database exists")
        except Exception as e:
            print_colored(f"Error verifying tenant/database: {str(e)}", Colors.RED)
            return False
        
        print_colored("Chroma initialization completed successfully!", Colors.GREEN)
        return True
    
    except Exception as e:
        print_colored(f"Error initializing Chroma: {str(e)}", Colors.RED)
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Initialize Chroma for RPGer')
    parser.add_argument('--host', default='chroma', help='Host address of the Chroma server')
    parser.add_argument('--port', default='8000', help='Port of the Chroma server')
    parser.add_argument('--verbose', action='store_true', help='Show detailed information')
    args = parser.parse_args()
    
    print_header("RPGer Direct Chroma Initialization")
    print(f"Initializing Chroma at {args.host}:{args.port}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = initialize_chroma_direct(args.host, args.port, args.verbose)
    
    if success:
        print_colored("\nChroma initialization completed successfully!", Colors.GREEN)
        sys.exit(0)
    else:
        print_colored("\nChroma initialization failed.", Colors.RED)
        sys.exit(1)

if __name__ == "__main__":
    main()
