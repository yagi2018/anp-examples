"""
Client module for accessing the server with DID authentication.
"""

import os
import json
import logging
import asyncio
import aiohttp
from pathlib import Path
from typing import Dict, Optional
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
from urllib.parse import urlparse

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

class DIDAuthClient:
    """
    简化的DID认证客户端，提供HTTP认证头部
    """
    
    def __init__(self, did_document_path: str, private_key_path: str):
        """
        初始化DID认证客户端
        
        Args:
            did_document_path: DID文档路径
            private_key_path: 私钥路径
        """
        self.did_document_path = did_document_path
        self.private_key_path = private_key_path
        
        # 状态变量
        self.did_document = None
        self.auth_headers = {}  # 按domain存储DID认证头
        self.tokens = {}  # 按domain存储token
        
        logger.info("DIDAuthClient初始化完成")
    
    def _get_domain(self, server_url: str) -> str:
        """从URL获取域名"""
        parsed_url = urlparse(server_url)
        domain = parsed_url.netloc.split(':')[0]
        return domain
    
    def _load_did_document(self) -> Dict:
        """加载DID文档"""
        try:
            if self.did_document:
                return self.did_document
                
            base_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            did_path = base_dir / self.did_document_path
            
            with open(did_path, 'r') as f:
                did_document = json.load(f)
            
            self.did_document = did_document
            logger.info(f"已加载DID文档: {did_path}")
            return did_document
        except Exception as e:
            logger.error(f"加载DID文档出错: {e}")
            raise
    
    def _load_private_key(self) -> ec.EllipticCurvePrivateKey:
        """加载私钥"""
        try:
            base_dir = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            key_path = base_dir / self.private_key_path
            
            with open(key_path, 'rb') as f:
                private_key_data = f.read()
            
            private_key = serialization.load_pem_private_key(
                private_key_data,
                password=None
            )
            
            logger.debug(f"已加载私钥: {key_path}")
            return private_key
        except Exception as e:
            logger.error(f"加载私钥出错: {e}")
            raise
    
    def _sign_callback(self, content: bytes, method_fragment: str) -> bytes:
        """签名回调函数"""
        try:
            private_key = self._load_private_key()
            signature = private_key.sign(
                content,
                ec.ECDSA(hashes.SHA256())
            )
            
            logger.debug(f"已签名内容，方法片段: {method_fragment}")
            return signature
        except Exception as e:
            logger.error(f"签名内容出错: {e}")
            raise
    
    def _generate_auth_header(self, domain: str) -> str:
        """生成DID认证头"""
        try:
            did_document = self._load_did_document()
            
            auth_header = generate_auth_header(
                did_document,
                domain,
                self._sign_callback
            )
            
            logger.info(f"已为域名 {domain} 生成认证头: {auth_header[:30]}...")
            return auth_header
        except Exception as e:
            logger.error(f"生成认证头出错: {e}")
            raise
    
    def get_auth_header(self, server_url: str, force_new: bool = False) -> Dict[str, str]:
        """
        获取认证头部
        
        Args:
            server_url: 服务器URL
            force_new: 是否强制生成新的DID认证头
            
        Returns:
            Dict[str, str]: HTTP头部字典
        """
        domain = self._get_domain(server_url)
        
        # 如果有token且不强制生成新的认证头，则返回token
        if domain in self.tokens and not force_new:
            token = self.tokens[domain]
            logger.info(f"使用域名 {domain} 的已有token")
            return {"Authorization": f"Bearer {token}"}
        
        # 否则生成或使用已有的DID认证头
        if domain not in self.auth_headers or force_new:
            self.auth_headers[domain] = self._generate_auth_header(domain)
        
        logger.info(f"使用域名 {domain} 的DID认证头")
        return {"Authorization": self.auth_headers[domain]}
    
    def update_token(self, server_url: str, headers: Dict[str, str]) -> Optional[str]:
        """
        从响应头中更新token
        
        Args:
            server_url: 服务器URL
            headers: 响应头字典
            
        Returns:
            Optional[str]: 更新的token，如果没有有效token则返回None
        """
        domain = self._get_domain(server_url)
        auth_header = headers.get("Authorization")
        
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header[7:]  # 移除"Bearer "前缀
            self.tokens[domain] = token
            logger.info(f"已更新域名 {domain} 的token: {token[:30]}...")
            return token
        else:
            logger.debug(f"响应头中没有域名 {domain} 的有效token")
            return None
    
    def clear_token(self, server_url: str) -> None:
        """
        清除指定域名的token
        
        Args:
            server_url: 服务器URL
        """
        domain = self._get_domain(server_url)
        if domain in self.tokens:
            del self.tokens[domain]
            logger.info(f"已清除域名 {domain} 的token")
        else:
            logger.debug(f"域名 {domain} 没有存储的token")
    
    def clear_all_tokens(self) -> None:
        """清除所有域名的token"""
        self.tokens.clear()
        logger.info("已清除所有域名的token")

# 示例用法
async def example_usage():
    # 创建客户端
    client = DIDAuthClient(
        did_document_path="use_did_test_public/did.json",
        private_key_path="use_did_test_public/key-1_private.pem"
    )
    
    server_url = "http://localhost:9870"
    
    # 获取认证头部（首次调用，返回DID认证头）
    headers = client.get_auth_header(server_url)
    
    # 发送请求
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{server_url}/agents/travel/hotel/ad/ph/12345/ad.json", 
            headers=headers
        ) as response:
            # 检查响应
            print(f"状态码: {response.status}")
            
            # 如果认证成功，更新token
            if response.status == 200:
                client.update_token(server_url, dict(response.headers))
            
            # 如果认证失败且使用的是token，清除token并重试
            elif response.status == 401:
                print("Token无效，清除并使用DID认证")
                client.clear_token(server_url)
                # 这里可以重试请求
    
    # 再次获取认证头部（如果上一步获取了token，这里会返回token认证头）
    headers = client.get_auth_header(server_url)
    print(f"第二次请求的头部: {headers}")
    
    # 强制使用DID认证头
    headers = client.get_auth_header(server_url, force_new=True)
    print(f"强制使用DID认证头: {headers}")
    
    # 测试不同域名
    another_server_url = "http://api.example.com"
    headers = client.get_auth_header(another_server_url)
    print(f"另一个域名的头部: {headers}")

if __name__ == "__main__":
    asyncio.run(example_usage()) 