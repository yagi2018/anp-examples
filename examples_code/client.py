"""
Client module for accessing the server with DID authentication.
"""

import os
import json
import logging
import asyncio
import aiohttp
from pathlib import Path
from typing import Tuple, Dict, Optional, Callable, Any
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes

# Import agent_connect for DID authentication
from agent_connect.authentication.did_wba import (
    generate_auth_header
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
SERVER_URL = "http://localhost:8000"
TEST_ENDPOINT = "/test"
DID_DOCUMENT_PATH = "use_did_test_public/did.json"
PRIVATE_KEY_PATH = "use_did_test_public/key-1_private.pem"

def load_did_document() -> Dict:
    """
    Load the DID document from file.
    
    Returns:
        Dict: The DID document
    """
    try:
        # Get the absolute path to the DID document
        base_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        did_path = base_dir / DID_DOCUMENT_PATH
        
        with open(did_path, 'r') as f:
            did_document = json.load(f)
        
        logger.info(f"Loaded DID document from {did_path}")
        return did_document
    except Exception as e:
        logger.error(f"Error loading DID document: {e}")
        raise

def load_private_key() -> ec.EllipticCurvePrivateKey:
    """
    Load the private key from file.
    
    Returns:
        ec.EllipticCurvePrivateKey: The private key
    """
    try:
        # Get the absolute path to the private key
        base_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        key_path = base_dir / PRIVATE_KEY_PATH
        
        with open(key_path, 'rb') as f:
            private_key_data = f.read()
        
        private_key = serialization.load_pem_private_key(
            private_key_data,
            password=None
        )
        
        logger.info(f"Loaded private key from {key_path}")
        return private_key
    except Exception as e:
        logger.error(f"Error loading private key: {e}")
        raise

def sign_callback(content: bytes, method_fragment: str) -> bytes:
    """
    Callback function for signing content with the private key.
    
    Args:
        content: Content to sign
        method_fragment: Method fragment from the DID document
        
    Returns:
        bytes: The signature
    """
    try:
        private_key = load_private_key()
        
        # 使用正确的哈希算法
        signature = private_key.sign(
            content,
            ec.ECDSA(hashes.SHA256())
        )
        
        logger.info(f"Signed content with method fragment: {method_fragment}")
        return signature
    except Exception as e:
        logger.error(f"Error signing content: {e}")
        raise

async def test_did_auth(url: str, auth_header: str) -> Tuple[bool, Optional[str]]:
    """
    Test DID authentication and get token.
    
    Args:
        url: URL to test
        auth_header: Authentication header
        
    Returns:
        Tuple[bool, Optional[str]]: (success, token)
    """
    try:
        headers = {"Authorization": auth_header}
        logger.info(f"Sending request to {url} with Authorization header: {auth_header[:50]}...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                logger.info(f"Received response with status code: {response.status}")
                logger.info(f"Response headers: {response.headers}")
                
                if response.status == 200:
                    # Extract token from response headers
                    token = response.headers.get("Authorization")
                    logger.info(f"Authorization header in response: {token}")
                    
                    if token and token.lower().startswith("bearer "):
                        token = token[7:]  # Remove "Bearer " prefix
                        logger.info(f"Successfully authenticated and received token: {token[:30]}...")
                        return True, token
                    else:
                        logger.warning("Authentication successful but no token received or token format incorrect")
                        logger.warning(f"Response headers: {response.headers}")
                        return True, None
                else:
                    response_text = await response.text()
                    logger.error(f"Authentication failed with status code: {response.status}")
                    logger.error(f"Response: {response_text}")
                    return False, None
    except Exception as e:
        logger.error(f"Error during authentication test: {e}")
        logger.error("Stack trace:", exc_info=True)
        return False, None

async def verify_token(url: str, token: str) -> bool:
    """
    Verify token by making a request with it.
    
    Args:
        url: URL to test
        token: Token to verify
        
    Returns:
        bool: Whether the token is valid
    """
    try:
        headers = {"Authorization": f"Bearer {token}"}
        logger.info(f"Verifying token at {url} with Authorization header: Bearer {token[:30]}...")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                logger.info(f"Received response with status code: {response.status}")
                logger.info(f"Response headers: {response.headers}")
                
                if response.status == 200:
                    logger.info("Token verification successful")
                    return True
                else:
                    response_text = await response.text()
                    logger.error(f"Token verification failed with status code: {response.status}")
                    logger.error(f"Response: {response_text}")
                    return False
    except Exception as e:
        logger.error(f"Error during token verification: {e}")
        logger.error("Stack trace:", exc_info=True)
        return False

async def main():
    """Main function to run the client."""
    try:
        # 1. Load DID document
        did_document = load_did_document()
        did = did_document["id"]
        logger.info(f"Using DID: {did}")
        
        # 2. Extract server domain from SERVER_URL
        from urllib.parse import urlparse
        parsed_url = urlparse(SERVER_URL)
        server_domain = parsed_url.netloc
        # Remove port from server_domain if present
        server_domain = server_domain.split(':')[0]
        logger.info(f"Server domain: {server_domain}")
        
        # 3. Generate authentication header
        logger.info("Generating authentication header...")
        logger.info(f"DID document: {did_document}")
        auth_header = generate_auth_header(
            did_document,
            server_domain,
            sign_callback
        )
        logger.info(f"Generated authentication header: {auth_header[:50]}...")
        
        # 4. Test DID authentication and get token
        test_url = f"{SERVER_URL}{TEST_ENDPOINT}"
        logger.info(f"Testing DID authentication at {test_url}")
        auth_success, token = await test_did_auth(test_url, auth_header)
        
        if not auth_success:
            logger.error("DID authentication test failed")
            return
            
        logger.info("DID authentication test successful")
        
        # 5. Verify token by making another request (if token was received)
        if token:
            logger.info(f"Received token from server: {token[:30]}...")
            logger.info("Verifying token...")
            token_valid = await verify_token(test_url, token)
            
            if token_valid:
                logger.info("Token verification successful")
            else:
                logger.error("Token verification failed")
        else:
            logger.warning("No token received from server, skipping token verification")
            logger.info("This is expected if the test endpoint is in EXEMPT_PATHS")
            logger.info("To test token generation, remove /test from EXEMPT_PATHS in did_auth_middleware.py")
            
    except Exception as e:
        logger.error(f"Error in main function: {e}")
        logger.error("Stack trace:", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main()) 