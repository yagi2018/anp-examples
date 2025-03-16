#!/usr/bin/env python
"""
测试ANPTool和anp_agent的功能
"""

import asyncio
import logging
import argparse
from pathlib import Path
from anp_examples.anp_tool import ANPTool
from anp_examples.anp_agent import simple_crawl
from anp_examples.utils.log_base import set_log_color_level

async def test_anp_tool(did_document_path=None, private_key_path=None):
    """测试ANPTool的基本功能"""
    print("\n=== 测试ANPTool ===")
    
    # 初始化ANPTool
    tool = ANPTool(
        did_document_path=did_document_path,
        private_key_path=private_key_path
    )
    
    # 测试获取URL内容
    url = "https://agent-search.ai/ad.json"
    print(f"获取URL: {url}")
    
    try:
        result = await tool.execute(url=url)
        print(f"状态码: {result.get('status_code')}")
        print(f"内容类型: {result.get('content_type')}")
        print("获取成功!")
    except Exception as e:
        print(f"获取失败: {str(e)}")

async def test_anp_agent(did_document_path=None, private_key_path=None):
    """测试anp_agent的功能"""
    print("\n=== 测试anp_agent ===")
    
    # 测试任务
    task = {
        "input": "我需要预订杭州的一个酒店：2025年3月9日，1天的酒店，经纬度（120.026208, 30.279212）。请一步步处理：第一步，你自己选择一个不错的酒店，第二步，帮我选择一个房间。最后告诉我你选择的详细信息",
        "type": "hotel_booking"
    }
    
    print(f"用户输入: {task['input']}")
    
    try:
        # 使用简化的爬取逻辑
        result = await simple_crawl(
            task['input'], 
            task['type'],
            did_document_path=did_document_path,
            private_key_path=private_key_path,
            max_documents=5  # 测试时使用较小的值，最多爬取5个文档
        )
        
        # 打印结果
        print("\n搜索智能体响应:")
        print(result["content"])
        print("\n访问过的URL:")
        for url in result.get("visited_urls", []):
            print(url)
        print(f"\n总共爬取了 {len(result.get('crawled_documents', []))} 个文档")
    except Exception as e:
        print(f"处理失败: {str(e)}")

async def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='测试ANPTool和anp_agent')
    parser.add_argument('--did', type=str, help='DID文档路径')
    parser.add_argument('--key', type=str, help='私钥路径')
    parser.add_argument('--max-docs', type=int, default=5, help='最大爬取文档数量')
    args = parser.parse_args()
    
    # 设置日志级别
    set_log_color_level(logging.INFO)
    
    # 获取DID路径
    did_document_path = args.did
    private_key_path = args.key
    
    # 如果未提供路径，使用默认路径
    if did_document_path is None or private_key_path is None:
        # 获取项目根目录
        base_dir = Path(__file__).resolve().parent
        
        if did_document_path is None:
            did_document_path = str(base_dir / "use_did_test_public/did.json")
            print(f"使用默认DID文档路径: {did_document_path}")
            
        if private_key_path is None:
            private_key_path = str(base_dir / "use_did_test_public/key-1_private.pem")
            print(f"使用默认私钥路径: {private_key_path}")
    
    # 测试ANPTool
    await test_anp_tool(did_document_path, private_key_path)
    
    # 测试anp_agent
    await test_anp_agent(did_document_path, private_key_path)

if __name__ == "__main__":
    asyncio.run(main()) 