#!/usr/bin/env python3
# scripts/ensure_chroma_defaults.py
import chromadb
import os
import logging
import time
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration for connecting to Chroma
# When running inside the container, use the container name
CHROMA_HOST_FROM_HOST = os.getenv("CHROMA_HOST_FOR_INIT", "chroma")
CHROMA_PORT = int(os.getenv("CHROMA_PORT", "8000"))
print(f"Using Chroma host: {CHROMA_HOST_FROM_HOST}:{CHROMA_PORT}")

DEFAULT_TENANT_NAME = os.getenv("CHROMA_DEFAULT_TENANT", "default_tenant")
# Chroma's HttpClient uses 'default_database' implicitly within a tenant unless specified otherwise
# DEFAULT_DATABASE_NAME = os.getenv("CHROMA_DEFAULT_DATABASE", "default_database")

MAX_RETRIES = 5
RETRY_DELAY = 10 # seconds

def main():
    client = None
    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Attempting to connect to Chroma server (Attempt {attempt + 1}/{MAX_RETRIES}) at {CHROMA_HOST_FROM_HOST}:{CHROMA_PORT}...")
            # Connect without specifying tenant first
            client = chromadb.HttpClient(
                host=CHROMA_HOST_FROM_HOST,
                port=CHROMA_PORT,
                settings=chromadb.config.Settings(allow_reset=True)
            )

            # Test basic connection with heartbeat
            heartbeat = client.heartbeat()
            logger.info(f"Successfully connected to Chroma server. Heartbeat: {heartbeat}")

            # Now try to create the tenant
            try:
                # First check if tenant exists
                logger.info(f"Checking if tenant '{DEFAULT_TENANT_NAME}' exists...")
                tenants = client.list_tenants()
                logger.info(f"Current tenants: {tenants}")

                tenant_exists = DEFAULT_TENANT_NAME in [t.name for t in tenants]

                if tenant_exists:
                    logger.info(f"Tenant '{DEFAULT_TENANT_NAME}' already exists.")
                else:
                    logger.info(f"Tenant '{DEFAULT_TENANT_NAME}' not found. Creating it...")
                    client.create_tenant(name=DEFAULT_TENANT_NAME)
                    logger.info(f"Tenant '{DEFAULT_TENANT_NAME}' created successfully.")

                # Set client context to the default tenant
                client.set_tenant(tenant=DEFAULT_TENANT_NAME)
                logger.info(f"Set client context to tenant '{DEFAULT_TENANT_NAME}'")

                # Verify access by listing collections
                collections = client.list_collections()
                logger.info(f"Successfully accessed tenant '{DEFAULT_TENANT_NAME}'. Found {len(collections)} collections.")

                logger.info("Chroma default tenant setup completed successfully.")
                return True
            except Exception as tenant_error:
                logger.error(f"Error setting up tenant: {tenant_error}")
                if attempt == MAX_RETRIES - 1:
                    raise

            break
        except Exception as e:
            logger.warning(f"Failed to connect to Chroma server: {e}. Retrying in {RETRY_DELAY} seconds...")
            if attempt == MAX_RETRIES - 1:
                logger.error("Max retries reached. Could not connect to Chroma server. Aborting initialization.")
                return False
            time.sleep(RETRY_DELAY)

    if not client:
        return False

if __name__ == "__main__":
    main()
