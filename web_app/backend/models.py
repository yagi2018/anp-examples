from typing import List, Dict, Any, Optional
from pydantic import BaseModel, HttpUrl, Field


class QueryRequest(BaseModel):
    """输入查询请求模型"""
    query: str = Field(..., description="用户的自然语言查询")
    agent_url: Optional[str] = Field(None, description="智能体描述 JSON 文档的 URL")


class CrawledDocument(BaseModel):
    """爬取的文档信息"""
    url: str = Field(..., description="爬取的 URL")
    method: str = Field(..., description="HTTP 方法")
    content: Dict[str, Any] = Field(..., description="响应内容")


class QueryResponse(BaseModel):
    """查询响应模型"""
    content: str = Field(..., description="模型返回的回答内容")
    type: str = Field(..., description="响应类型")
    visited_urls: List[str] = Field(..., description="访问过的 URL 列表")
    crawled_documents: List[CrawledDocument] = Field(..., description="爬取的文档列表")
    task_type: Optional[str] = Field(None, description="任务类型") 