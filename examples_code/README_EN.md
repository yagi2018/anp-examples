# DID Authentication Example

This directory contains example code for authentication using DID (Decentralized Identifier), demonstrating how to implement DID-based authentication middleware and client.

## Code Structure

- `server.py`: FastAPI server using DID authentication middleware
- `did_auth_middleware.py`: DID authentication middleware handling DID authentication and JWT token generation
- `client.py`: Client module authenticating with DID and obtaining access tokens
- `jwt_config.py`: JWT configuration module providing functions to read public and private keys
- `test_token.py`: Test script for testing the complete authentication flow
- `private_key.pem` and `public_key.pem`: Key pair used for JWT signing

## Installation and Environment Setup

This project uses Poetry for dependency management and virtual environment management.

### Installing Dependencies

```bash
# Install all dependencies
poetry install

# Activate the virtual environment
poetry shell
```

## How to Use

### Starting the Server

After activating the virtual environment, start the server directly using Python:

```bash
# Navigate to the examples_code directory
cd examples_code

# Start the server directly using Python
python server.py
```

Or use uvicorn:

```bash
# Start the server using uvicorn
uvicorn examples_code.server:app --host 0.0.0.0 --port 8000 --reload
```

### Running the Client

After activating the virtual environment, start the client directly using Python:

```bash
# Navigate to the examples_code directory
cd examples_code

# Start the client directly using Python
python client.py
```

Or use the module approach:

```bash
# Run the client using Python module approach
python -m examples_code.client
```

## Client Flow

`client.py` implements the following flow:

1. **Loading DID Document and Private Key**:
   - Load the DID document from the specified path (`use_did_test_public/did.json`)
   - Load the private key from the specified path (`use_did_test_public/key-1_private.pem`)

2. **Generating Authentication Header**:
   - Generate a DID authentication header using the DID document, server domain, and sign callback function
   - The sign callback function signs content using the private key

3. **Sending Authentication Request**:
   - Send a request with the DID authentication header to the server
   - Server verifies the authentication header and generates a JWT token
   - Server returns the JWT token in the response header

4. **Extracting and Using the Token**:
   - Extract the JWT token from the response header
   - Use the JWT token for subsequent requests
   - Server verifies the JWT token and processes the request

## Related Files

### JWT Key Pair

- `private_key.pem`: Private key used for JWT signing, located in the examples_code directory
- `public_key.pem`: Public key used for JWT verification, located in the examples_code directory

This key pair is used by the server to generate and verify JWT tokens.

### DID Document and Private Key

The example uses the DID document and private key located in the `use_did_test_public` folder at the project root:

- `use_did_test_public/did.json`: DID document, already registered in the DID system
- `use_did_test_public/key-1_private.pem`: Private key corresponding to the public key in the DID document

This DID document is already registered and can be used directly for testing. The DID document contains public key information, and the private key is used to generate signatures.

## Authentication Flow

1. Client generates an authentication header using DID document and private key
2. Client sends a request with the authentication header to the server
3. Server verifies the authentication header and generates a JWT token
4. Server returns the JWT token in the response header
5. Client extracts the JWT token and uses it in subsequent requests
6. Server verifies the JWT token and processes the request

## Configuration

### Server Configuration

- `EXEMPT_PATHS`: Defined in `did_auth_middleware.py`, these paths don't require authentication
- `WBA_SERVER_DOMAINS`: Defined in `did_auth_middleware.py`, list of allowed server domains

### Client Configuration

- `SERVER_URL`: Defined in `client.py`, server URL
- `TEST_ENDPOINT`: Defined in `client.py`, test endpoint
- `DID_DOCUMENT_PATH`: Defined in `client.py`, path to DID document
- `PRIVATE_KEY_PATH`: Defined in `client.py`, path to private key

## Debugging Tips

If you encounter issues, try the following:

1. Check the log output to understand problems in the authentication flow
2. Ensure the `/test` path is not in `EXEMPT_PATHS` to test the complete authentication flow
3. Check the CORS configuration to ensure the `Authorization` header is properly exposed
4. Use the `test_token.py` script for detailed debugging

## Dependencies

- FastAPI: Web framework
- PyJWT: JWT handling
- cryptography: Cryptographic operations
- aiohttp: Asynchronous HTTP client
- agent-connect: DID authentication library 