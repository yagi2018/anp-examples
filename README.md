# ANP Examples

Agent Network Protocol (ANP) example code.

## Project Structure

```
anp-examples/
├── anp_examples/         # Main package directory
│   ├── __init__.py
│   ├── anp_agent.py      # ANP Agent implementation
│   ├── anp_tool.py       # ANP Tool for DID authentication
│   └── utils/            # Utility functions
│       ├── __init__.py
│       └── auth_jwt.py   # JWT authentication tools
├── examples_code/        # Example code
│   └── did_auth_middleware.py
├── use_did_test_public/  # DID authentication files
│   ├── did.json          # DID document
│   └── key-1_private.pem # Private key for DID authentication
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

# 使用官方镜像源更新依赖（推荐）
# Configure Poetry to use the official PyPI mirror
poetry config repositories.pypi https://pypi.org/simple

# Update all dependencies without using cache
poetry update --no-cache
```

### 安装必要的依赖

`agent-connect`包依赖于`openai`包，但它可能不会自动安装。如果运行时遇到`ModuleNotFoundError: No module named 'openai'`错误，请手动安装：

```bash
# 安装openai包
poetry add openai
```

## 使用ANPTool

ANPTool是一个用于与其他智能体进行交互的工具，它使用DID（去中心化标识符）进行身份验证。这是项目中唯一用于获取URL内容的工具。

### 基本用法

```python
from anp_examples.anp_tool import ANPTool

# 初始化ANPTool（使用默认DID路径）
tool = ANPTool()

# 或者指定DID路径
tool = ANPTool(
    did_document_path="/path/to/did.json",
    private_key_path="/path/to/private_key.pem"
)

# 使用ANPTool获取URL内容
async def fetch_data():
    result = await tool.execute(
        url="https://agent-search.ai/ad.json",
        method="GET",
        headers={},
        params={},
        body=None
    )
    print(result)

# 运行异步函数
import asyncio
asyncio.run(fetch_data())
```

### 使用简化的爬取逻辑

`anp_agent.py`文件提供了一个简化的爬取逻辑`simple_crawl`，它让模型自主决定爬取路径：

```python
from anp_examples.anp_agent import simple_crawl

# 使用简化的爬取逻辑
async def crawl_data():
    result = await simple_crawl(
        "我需要预订杭州的一个酒店",
        "hotel_booking",
        max_documents=10  # 最多爬取10个文档
    )
    print(result["content"])
    print(f"总共爬取了 {len(result.get('crawled_documents', []))} 个文档")

# 运行异步函数
import asyncio
asyncio.run(crawl_data())
```

### 简化的爬取逻辑特点

1. 模型自主决定爬取路径，无需人工干预
2. 设置了最大爬取文档数量限制，默认为10个文档
3. 记录所有爬取的文档URL和内容
4. 简洁的代码结构，易于理解和维护

### 指定DID路径

可以通过以下方式指定DID路径：

```python
# 指定DID路径
result = await simple_crawl(
    "我需要预订杭州的一个酒店",
    "hotel_booking",
    did_document_path="/path/to/did.json",
    private_key_path="/path/to/private_key.pem",
    max_documents=10
)
```

### 使用环境变量指定DID路径

您也可以通过环境变量来指定DID路径：

```bash
# 设置环境变量
export DID_DOCUMENT_PATH="/path/to/did.json"
export DID_PRIVATE_KEY_PATH="/path/to/private_key.pem"

# 然后运行您的脚本
poetry run python your_script.py
```

### 测试ANPTool

项目根目录下提供了一个测试脚本`test_anp_tool.py`，可以用来测试ANPTool和简化的爬取逻辑：

```bash
# 使用默认DID路径运行测试脚本
poetry run python test_anp_tool.py

# 或者指定DID路径和最大爬取文档数
poetry run python test_anp_tool.py --did /path/to/did.json --key /path/to/private_key.pem --max-docs 5
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


