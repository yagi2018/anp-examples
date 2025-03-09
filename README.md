# ANP Examples

Agent Network Protocol (ANP) example code.

## Project Structure

```
anp-examples/
├── anp_examples/         # Main package directory
│   ├── __init__.py
│   └── utils/            # Utility functions
│       ├── __init__.py
│       └── auth_jwt.py   # JWT authentication tools
├── examples_code/        # Example code
│   └── did_auth_middleware.py
├── pyproject.toml        # Poetry project configuration
└── README.md             # Project documentation
```

## Managing the Project with Poetry

This project uses Poetry for dependency management and virtual environment management.

### Installing Poetry

If you haven't installed Poetry yet, please follow the [official documentation](https://python-poetry.org/docs/#installation) for installation.

### Installing Project Dependencies

```bash
# Install all dependencies
poetry install

# Activate the virtual environment
poetry shell

# Or run commands directly in the virtual environment
poetry run python your_script.py
```

### Adding New Dependencies

```bash
# Add a new dependency
poetry add package_name

# Add a development dependency
poetry add --group dev package_name
```

### Updating Dependencies

```bash
# Update all dependencies
poetry update

# Update a specific dependency
poetry update package_name
```

## Project Description

Develop an ANP example application consisting of two parts:

1. **ANP Agent**
   The entry point of the agent is an agent description document. Through this document, connections to internal agent data can be established. The agent description document, combined with internal data such as additional JSON files, images, and interface files, constitutes the public information of the agent. It is recommended to use a hotel agent as an example. Construct the agent's data, including a hotel description, services provided by the hotel, customer service details, and booking interfaces. Use FastAPI to return the relevant documents based on requests.

2. **ANP Client**
   Develop a client that accesses the ANP agent. The client will feature a page that accepts a URL pointing to an agent description document. With this document URL, the client can access all information from the agent, including services, products, and API endpoints like hotel booking interfaces. The page should clearly display which URLs the client accessed and the content retrieved, allowing users to visually follow the interaction process.

## License

Please refer to the LICENSE file.

# anp-examples
anp-examples

Develop an ANP example application

It consists of two parts:

1. **ANP Agent**
The entry point of the agent is an agent description document. Through this document, connections to internal agent data can be established. The agent description document, combined with internal data such as additional JSON files, images, and interface files, constitutes the public information of the agent. It is recommended to use a hotel agent as an example. Construct the agent's data, including a hotel description, services provided by the hotel, customer service details, and booking interfaces. Use FastAPI to return the relevant documents based on requests. I can provide sample documents for the hotel agent.

2. **ANP Client**
Develop a client that accesses the ANP agent. The client will feature a page that accepts a URL pointing to an agent description document. With this document URL, the client can access all information from the agent, including services, products, and API endpoints like hotel booking interfaces. The page should clearly display which URLs the client accessed and the content retrieved, allowing users to visually follow the interaction process.


