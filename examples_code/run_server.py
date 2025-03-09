#!/usr/bin/env python
"""
Script to run the server.
"""

import os
import sys
import argparse
import uvicorn
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def main():
    """Parse command-line arguments and run the server."""
    parser = argparse.ArgumentParser(
        description="Run the DID authentication server"
    )
    
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to bind to (default: 8000)"
    )
    
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on code changes"
    )
    
    args = parser.parse_args()
    
    logger.info(f"Starting server on {args.host}:{args.port}")
    
    # Run the server
    uvicorn.run(
        "examples_code.server:app",
        host=args.host,
        port=args.port,
        reload=args.reload
    )
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 