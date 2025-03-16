from typing import Optional, Dict, Any, List, Union
import os
import json
import logging
import asyncio
from pathlib import Path
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv
from anp_examples.utils.log_base import set_log_color_level
from anp_examples.anp_tool import ANPTool  # 导入ANPTool

# Get the absolute path to the root directory
ROOT_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(ROOT_DIR / ".env")

SEARCH_AGENT_PROMPT_TEMPLATE = """
你是一个通用智能网络数据探索工具。你的目标是通过递归访问各种格式的数据（包括JSON-LD、YAML等），找到用户需要的信息、API，以完成指定的任务。

## 当前任务
{task_description}

## 重要说明
1. 你将收到一个起始URL({initial_url})，这是一个搜索智能体的描述文件
2. 你需要理解这个搜索智能体的结构、功能和API用法
3. 你需要像网络爬虫一样，不断从中发现并访问新的URL和API端点
4. 你可以使用anp_tool工具来获取任何URL的内容
5. 该工具可以处理多种格式的响应，包括：
   - JSON格式：将直接解析为JSON对象
   - YAML格式：将返回文本内容，你需要分析其结构
   - 其他文本格式：将返回原始文本内容
6. 阅读每个文档，寻找与任务相关的信息或API端点
7. 你需要自己决定爬取路径，不要等待用户指示
8. 注意：你最多可以爬取10个URL，超过此限制后必须结束搜索

## 爬取策略
1. 首先获取初始URL内容，理解搜索智能体的结构和API
2. 识别文档中的所有URL和链接，特别是serviceEndpoint、url、@id等字段
3. 分析API文档，理解API的使用方法、参数和返回值
4. 根据API文档，构造合适的请求找到所需信息
5. 记录你访问过的所有URL，避免重复爬取
6. 总结发现的所有相关信息，提供详细的建议

## 工作流程
1. 获取起始URL内容，理解搜索智能体的功能
2. 分析内容，找出所有可能的链接和API文档
3. 解析API文档，理解API的使用方法
4. 根据任务需求，构造请求获取所需信息
5. 继续探索相关链接，直到找到足够的信息
6. 总结信息，提供最适合用户的建议

## JSON-LD数据解析提示
1. 注意@context字段，它定义了数据的语义上下文
2. @type字段表示实体类型，帮助你理解数据的含义
3. @id字段通常是一个可以进一步访问的URL
4. 寻找serviceEndpoint、url等字段，它们通常指向API或更多数据

提供详细信息和清晰解释，让用户理解你找到的信息和你的推荐理由。
"""

# 全局变量
initial_url = "https://agent-search.ai/ad.json"

# 定义可用的工具
def get_available_tools(anp_tool_instance):
    """获取可用的工具列表"""
    return [
        {
            "type": "function",
            "function": {
                "name": "anp_tool",
                "description": anp_tool_instance.description,
                "parameters": anp_tool_instance.parameters
            }
        }
    ]

async def handle_tool_call(tool_call: Any, messages: List[Dict], anp_tool: ANPTool, crawled_documents: List[Dict], visited_urls: set) -> None:
    """处理工具调用"""
    function_name = tool_call.function.name
    function_args = json.loads(tool_call.function.arguments)
    
    if function_name == "anp_tool":
        url = function_args.get("url")
        method = function_args.get("method", "GET")
        headers = function_args.get("headers", {})
        params = function_args.get("params", {})
        body = function_args.get("body")
        
        try:
            # 使用ANPTool获取URL内容
            result = await anp_tool.execute(
                url=url,
                method=method,
                headers=headers,
                params=params,
                body=body
            )
            logging.info(f"ANPTool response [url: {url}]")
            
            # 记录访问过的URL和获取到的内容
            visited_urls.add(url)
            crawled_documents.append({
                "url": url,
                "method": method,
                "content": result
            })
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result, ensure_ascii=False),
            })
        except Exception as e:
            logging.error(f"Error using ANPTool for URL {url}: {str(e)}")
            
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps({
                    "error": f"Failed to use ANPTool for URL: {url}",
                    "message": str(e)
                }),
            })

async def simple_crawl(
    user_input: str, 
    task_type: str = "general", 
    did_document_path: Optional[str] = None, 
    private_key_path: Optional[str] = None,
    max_documents: int = 10
) -> Dict[str, Any]:
    """
    简化的爬取逻辑：让模型自主决定爬取路径
    
    Args:
        user_input: 用户输入的任务描述
        task_type: 任务类型
        did_document_path: DID文档路径
        private_key_path: 私钥路径
        max_documents: 最大爬取文档数量
        
    Returns:
        包含爬取结果的字典
    """
    # 初始化变量
    visited_urls = set()
    crawled_documents = []
    
    # 初始化ANPTool
    anp_tool = ANPTool(
        did_document_path=did_document_path,
        private_key_path=private_key_path
    )
    
    # 初始化Azure OpenAI客户端
    client = AsyncAzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT"),
    )
    
    # 获取初始URL内容
    try:
        initial_content = await anp_tool.execute(url=initial_url)
        visited_urls.add(initial_url)
        crawled_documents.append({
            "url": initial_url,
            "method": "GET",
            "content": initial_content
        })
        
        logging.info(f"成功获取初始URL: {initial_url}")
    except Exception as e:
        logging.error(f"获取初始URL {initial_url} 失败: {str(e)}")
        return {
            "content": f"获取初始URL失败: {str(e)}",
            "type": "error",
            "visited_urls": [],
            "crawled_documents": []
        }
    
    # 创建初始消息
    formatted_prompt = SEARCH_AGENT_PROMPT_TEMPLATE.format(
        task_description=user_input,
        initial_url=initial_url
    )
    
    messages = [
        {"role": "system", "content": formatted_prompt},
        {"role": "user", "content": user_input},
        {"role": "system", "content": f"我已经获取了初始URL的内容。以下是搜索智能体的描述数据:\n\n```json\n{json.dumps(initial_content, ensure_ascii=False, indent=2)}\n```\n\n请分析这个数据，理解搜索智能体的功能和API用法。找出你需要访问的链接，通过anp_tool工具来获取更多信息，完成用户的任务。"}
    ]
    
    # 开始对话循环
    current_iteration = 0
    
    while current_iteration < max_documents:
        current_iteration += 1
        logging.info(f"开始第 {current_iteration}/{max_documents} 次爬取")
        
        # 检查是否已达到最大爬取文档数
        if len(crawled_documents) >= max_documents:
            logging.info(f"已达到最大爬取文档数 {max_documents}，停止爬取")
            # 添加一条消息告知模型已达到最大爬取数
            messages.append({
                "role": "system", 
                "content": f"你已经爬取了 {len(crawled_documents)} 个文档，已达到最大爬取数量限制 {max_documents}。请根据已获取的信息做出最终总结。"
            })
        
        # 获取模型响应
        completion = await client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_MODEL"),
            messages=messages,
            tools=get_available_tools(anp_tool),
            tool_choice="auto",
        )
        
        response_message = completion.choices[0].message
        messages.append({
            "role": "assistant",
            "content": response_message.content,
            "tool_calls": response_message.tool_calls
        })
        
        # 检查是否结束对话
        if not response_message.tool_calls:
            logging.info("模型未请求任何工具调用，结束爬取")
            break
        
        # 处理工具调用
        for tool_call in response_message.tool_calls:
            await handle_tool_call(tool_call, messages, anp_tool, crawled_documents, visited_urls)
            
            # 如果达到最大爬取文档数，停止处理工具调用
            if len(crawled_documents) >= max_documents:
                break
        
        # 如果达到最大爬取文档数，进行一次最终的总结
        if len(crawled_documents) >= max_documents and current_iteration < max_documents:
            logging.info(f"已达到最大爬取文档数 {max_documents}，进行最终总结")
            continue
    
    # 创建结果
    result = {
        "content": response_message.content,
        "type": "text",
        "visited_urls": list(visited_urls),
        "crawled_documents": crawled_documents,
        "task_type": task_type
    }
    
    return result

async def main():
    """主函数"""
    
    # 获取DID路径
    current_dir = Path(__file__).parent
    base_dir = current_dir.parent
    did_document_path = str(base_dir / "use_did_test_public/did.json")
    private_key_path = str(base_dir / "use_did_test_public/key-1_private.pem")
    
    from datetime import datetime, timedelta

    # 获取当前日期加3天
    booking_date = (datetime.now() + timedelta(days=3)).strftime('%Y年%m月%d日')

    # 测试任务
    task = {
        "input": f"我需要预订杭州的一个酒店：{booking_date}，1天的酒店，经纬度（120.026208, 30.279212）。请一步步处理：第一步，你自己选择一个不错的酒店，第二步，帮我选择一个房间。最后告诉我你选择的详细信息",
        "type": "hotel_booking"
    }
    
    print(f"\n=== 测试任务: {task['type']} ===")
    print(f"用户输入: {task['input']}")
    
    # 使用简化的爬取逻辑
    result = await simple_crawl(
        task['input'], 
        task['type'],
        did_document_path=did_document_path,
        private_key_path=private_key_path,
        max_documents=10  # 最多爬取10个文档
    )
    
    # 打印结果
    print("\n=== 搜索智能体响应 ===")
    print(result["content"])
    print("\n=== 访问过的URL ===")
    for url in result.get("visited_urls", []):
        print(url)
    print(f"\n=== 总共爬取了 {len(result.get('crawled_documents', []))} 个文档 ===")

if __name__ == "__main__":
    set_log_color_level(logging.DEBUG)
    asyncio.run(main())
