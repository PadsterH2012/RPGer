#!/usr/bin/env python3
"""
Simple script to create a default tenant in Chroma.
This script is designed to be run inside the backend container.
"""

import chromadb
import logging
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Chroma connection settings
CHROMA_HOST = "chroma"  # Container name in Docker network
CHROMA_PORT = 8000
DEFAULT_TENANT = "default_tenant"
DEFAULT_DATABASE = "default_database"

def main():
    logger.info(f"Connecting to Chroma at {CHROMA_HOST}:{CHROMA_PORT}")

    try:
        # Create client without tenant
        client = chromadb.HttpClient(
            host=CHROMA_HOST,
            port=CHROMA_PORT
        )

        # Check connection
        heartbeat = client.heartbeat()
        logger.info(f"Connected to Chroma. Heartbeat: {heartbeat}")

        # List existing tenants
        try:
            tenants = client.list_tenants()
            tenant_names = [t.name for t in tenants]
            logger.info(f"Existing tenants: {tenant_names}")

            # Check if default tenant exists
            if DEFAULT_TENANT in tenant_names:
                logger.info(f"Tenant '{DEFAULT_TENANT}' already exists.")
            else:
                # Create default tenant
                logger.info(f"Creating tenant '{DEFAULT_TENANT}'...")
                client.create_tenant(DEFAULT_TENANT)
                logger.info(f"Tenant '{DEFAULT_TENANT}' created successfully.")

            # Test tenant access
            client.set_tenant(DEFAULT_TENANT)
            logger.info(f"Set tenant to '{DEFAULT_TENANT}'")

            # Test database access
            client.set_database(DEFAULT_DATABASE)
            logger.info(f"Set database to '{DEFAULT_DATABASE}'")

            # List collections
            collections = client.list_collections()
            logger.info(f"Successfully accessed tenant '{DEFAULT_TENANT}' and database '{DEFAULT_DATABASE}'. Found {len(collections)} collections.")

            return True

        except Exception as e:
            logger.error(f"Error working with tenants: {e}")
            return False

    except Exception as e:
        logger.error(f"Failed to connect to Chroma: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
