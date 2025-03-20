from typing import Optional, Dict, Any, List, Union
import os
import json
import logging
import asyncio
from pathlib import Path
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv
from anp_examples.utils.log_base import set_log_color_level
from anp_examples.anp_tool import ANPTool  # Import ANPTool

# Get the absolute path to the root directory
ROOT_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(ROOT_DIR / ".env")

from datetime import datetime

current_date = datetime.now().strftime("%Y-%m-%d")

SEARCH_AGENT_PROMPT_TEMPLATE = f"""
您是一个通用的智能网络数据探索工具。您的目标是通过递归访问各种格式的数据（包括JSON-LD、YAML等）来找到用户所需的信息和API，以完成指定任务。

## 当前任务
{{task_description}}

## 重要提示
1. 您将收到一个起始URL（{{initial_url}}），这是一个搜索代理的描述文件。
2. 您需要了解该搜索代理的结构、功能和API使用方法。
3. 您需要像网络爬虫一样不断发现和访问新的URL和API端点。
4. 您可以使用anp_tool获取任何URL的内容。
5. 该工具可以处理多种格式的响应，包括：
   - JSON格式：将直接解析为JSON对象。
   - YAML格式：将返回文本内容，您需要分析其结构。
   - 其他文本格式：将返回原始文本内容。
6. 阅读每个文档以查找与任务相关的信息或API端点。
7. 您需要自行决定爬取路径，不要等待用户指示。
8. 注意：您最多可以爬取10个URL，超过此限制后必须结束搜索。

## 爬取策略
1. 首先获取起始URL的内容，了解搜索代理的结构和API。
2. 识别文档中的所有URL和链接，特别是serviceEndpoint、url、@id等字段。
3. 分析API文档以了解API的使用、参数和返回值。
4. 根据API文档构建适当的请求以找到所需信息。
5. 记录您访问过的所有URL以避免重复爬取。
6. 总结您找到的所有相关信息并提供详细建议。

## 工作流程
1. 获取起始URL的内容并了解搜索代理的功能。
2. 分析内容以找到所有可能的链接和API文档。
3. 解析API文档以了解API的使用。
4. 根据任务要求构建请求以获取所需信息。
5. 继续探索相关链接直到找到足够的信息。
6. 总结信息并为用户提供最合适的建议。

## JSON-LD数据解析提示
1. 注意@context字段，它定义了数据的语义上下文。
2. @type字段指示实体的类型，帮助您理解数据的含义。
3. @id字段通常是一个可以进一步访问的URL。
4. 查找诸如serviceEndpoint、url等字段，这些通常指向API或更多数据。

提供详细信息和清晰的解释，以帮助用户理解您找到的信息和您的建议。

## 日期
当前日期：{current_date}
"""

# Global variable
initial_url = "https://agent-search.ai/ad.json"


# Define available tools
def get_available_tools(anp_tool_instance):
    """Get the list of available tools"""
    return [
        {
            "type": "function",
            "function": {
                "name": "anp_tool",
                "description": anp_tool_instance.description,
                "parameters": anp_tool_instance.parameters,
            },
        }
    ]


async def handle_tool_call(
    tool_call: Any,
    messages: List[Dict],
    anp_tool: ANPTool,
    crawled_documents: List[Dict],
    visited_urls: set,
) -> None:
    """Handle tool call"""
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)

    if function_name == "anp_tool":
        url = function_args.get("url")
        method = function_args.get("method", "GET")
        headers = function_args.get("headers", {})
        params = function_args.get("params", {})
        body = function_args.get("body")

        try:
            # Use ANPTool to get URL content
            result = await anp_tool.execute(
                url=url, method=method, headers=headers, params=params, body=body
            )
            logging.info(f"ANPTool response [url: {url}]")

            # Record visited URLs and obtained content
            visited_urls.add(url)
            crawled_documents.append({"url": url, "method": method, "content": result})

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, ensure_ascii=False),
                }
            )
        except Exception as e:
            logging.error(f"Error using ANPTool for URL {url}: {str(e)}")

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(
                        {
                            "error": f"Failed to use ANPTool for URL: {url}",
                            "message": str(e),
                        }
                    ),
                }
            )


async def simple_crawl(
    user_input: str,
    task_type: str = "general",
    did_document_path: Optional[str] = None,
    private_key_path: Optional[str] = None,
    max_documents: int = 10,
    initial_url: str = "https://agent-search.ai/ad.json",
) -> Dict[str, Any]:
    """
    Simplified crawling logic: let the model decide the crawling path autonomously

    Args:
        user_input: Task description input by the user
        task_type: Task type
        did_document_path: DID document path
        private_key_path: Private key path
        max_documents: Maximum number of documents to crawl
        initial_url: Initial URL to start crawling from

    Returns:
        Dictionary containing the crawl results
    """
    # Initialize variables
    visited_urls = set()
    crawled_documents = []

    # Initialize ANPTool
    anp_tool = ANPTool(
        did_document_path=did_document_path, private_key_path=private_key_path
    )

    # Initialize Azure OpenAI client
    client = AsyncAzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    )

    # Get initial URL content
    try:
        initial_content = await anp_tool.execute(url=initial_url)
        visited_urls.add(initial_url)
        crawled_documents.append(
            {"url": initial_url, "method": "GET", "content": initial_content}
        )

        logging.info(f"Successfully obtained initial URL: {initial_url}")
    except Exception as e:
        logging.error(f"Failed to obtain initial URL {initial_url}: {str(e)}")
        return {
            "content": f"Failed to obtain initial URL: {str(e)}",
            "type": "error",
            "visited_urls": [],
            "crawled_documents": [],
        }

    # Create initial message
    formatted_prompt = SEARCH_AGENT_PROMPT_TEMPLATE.format(
        task_description=user_input, initial_url=initial_url
    )

    messages = [
        {"role": "system", "content": formatted_prompt},
        {"role": "user", "content": user_input},
        {
            "role": "system",
            "content": f"I have obtained the content of the initial URL. Here is the description data of the search agent:\n\n```json\n{json.dumps(initial_content, ensure_ascii=False, indent=2)}\n```\n\nPlease analyze this data, understand the functions and API usage of the search agent. Find the links you need to visit, and use the anp_tool to get more information to complete the user's task.",
        },
    ]

    # Start conversation loop
    current_iteration = 0

    while current_iteration < max_documents:
        current_iteration += 1
        logging.info(f"Starting crawl iteration {current_iteration}/{max_documents}")

        # Check if the maximum number of documents to crawl has been reached
        if len(crawled_documents) >= max_documents:
            logging.info(f"Reached the maximum number of documents to crawl {max_documents}, stopping crawl")
            # Add a message to inform the model that the maximum number of crawls has been reached
            messages.append(
                {
                    "role": "system",
                    "content": f"You have crawled {len(crawled_documents)} documents, reaching the maximum crawl limit of {max_documents}. Please make a final summary based on the information obtained.",
                }
            )

        # Get model response
        completion = await client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_MODEL"),
            messages=messages,
            tools=get_available_tools(anp_tool),
            tool_choice="auto",
        )

        response_message = completion.choices[0].message
        messages.append(
            {
                "role": "assistant",
                "content": response_message.content,
                "tool_calls": response_message.tool_calls,
            }
        )

        # Check if the conversation should end
        if not response_message.tool_calls:
            logging.info("The model did not request any tool calls, ending crawl")
            break

        # Handle tool calls
        for tool_call in response_message.tool_calls:
            await handle_tool_call(
                tool_call, messages, anp_tool, crawled_documents, visited_urls
            )

            # If the maximum number of documents to crawl is reached, stop handling tool calls
            if len(crawled_documents) >= max_documents:
                break

        # If the maximum number of documents to crawl is reached, make a final summary
        if (
            len(crawled_documents) >= max_documents
            and current_iteration < max_documents
        ):
            logging.info(f"Reached the maximum number of documents to crawl {max_documents}, making final summary")
            continue

    # Create result
    result = {
        "content": response_message.content,
        "type": "text",
        "visited_urls": [doc["url"] for doc in crawled_documents],
        "crawled_documents": crawled_documents,
        "task_type": task_type,
    }

    return result


async def main():
    """Main function"""

    # Get DID path
    current_dir = Path(__file__).parent
    base_dir = current_dir.parent
    did_document_path = str(base_dir / "use_did_test_public/did.json")
    private_key_path = str(base_dir / "use_did_test_public/key-1_private.pem")

    from datetime import datetime, timedelta

    # Get the current date plus 3 days
    booking_date = (datetime.now() + timedelta(days=3)).strftime("%Y年%m月%d日")

    # Test task
    task = {
        "input": f"I need to book a hotel in Hangzhou: {booking_date}, for 1 day, coordinates (120.026208, 30.279212). Please handle it step by step: First, choose a good hotel yourself, then help me choose a room. Finally, tell me the details of your choice.",
        "type": "hotel_booking",
    }

    print(f"\n=== Test Task: {task['type']} ===")
    print(f"User Input: {task['input']}")

    # Use simplified crawling logic
    result = await simple_crawl(
        task["input"],
        task["type"],
        did_document_path=did_document_path,
        private_key_path=private_key_path,
        max_documents=10,  # Crawl up to 10 documents
    )

    # Print result
    print("\n=== Search Agent Response ===")
    print(result["content"])
    print("\n=== Visited URLs ===")
    for url in result.get("visited_urls", []):
        print(url)
    print(f"\n=== Crawled a total of {len(result.get('crawled_documents', []))} documents ===")


if __name__ == "__main__":
    set_log_color_level(logging.DEBUG)
    asyncio.run(main())
