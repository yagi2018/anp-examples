#!/usr/bin/env python
"""
Command-line tool to run the client.
"""

import os
import sys
import argparse
import asyncio
import logging
import examples_code.client as client

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Parse command-line arguments and run the client."""
    parser = argparse.ArgumentParser(
        description="Run the DID authentication client"
    )
    
    parser.add_argument(
        "--server-url",
        default="http://localhost:8000",
        help="URL of the server (default: http://localhost:8000)"
    )
    
    parser.add_argument(
        "--endpoint",
        default="/test",
        help="Endpoint to test (default: /test)"
    )
    
    args = parser.parse_args()
    
    # Update client configuration
    client.SERVER_URL = args.server_url
    client.TEST_ENDPOINT = args.endpoint
    
    logger.info(f"Using server URL: {client.SERVER_URL}")
    logger.info(f"Using endpoint: {client.TEST_ENDPOINT}")
    
    # Run the client
    asyncio.run(client.main())
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 