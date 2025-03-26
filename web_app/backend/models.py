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


class AgentDocTreeRequest(BaseModel):
    """智能体文档树请求模型"""

    agent_url: Optional[str] = Field(None, description="智能体描述 JSON 文档的 URL")


class DocumentNode(BaseModel):
    """文档节点模型"""

    name: str = Field(..., description="节点名称")
    url: str = Field(..., description="节点URL")
    children: List["DocumentNode"] = Field(default=[], description="子节点列表")
    doc: Optional[Dict[str, Any]] = Field(None, description="文档内容")


# 更新递归引用
DocumentNode.model_rebuild()


class DocumentTree(BaseModel):
    """文档树模型"""

    name: str = Field(..., description="树根名称")
    children: List[DocumentNode] = Field(default=[], description="子节点列表")


class AgentDocTreeResponse(BaseModel):
    """智能体文档树响应模型"""

    doc_tree: DocumentTree = Field(..., description="文档树结构")
    visited_urls: List[str] = Field(..., description="访问过的 URL 列表")
    crawled_documents: List[CrawledDocument] = Field(..., description="爬取的文档列表")


class GetDocumentRequest(BaseModel):
    """获取文档请求模型"""

    url: str = Field(..., description="需要获取内容的URL")


class GetDocumentResponse(BaseModel):
    """获取文档响应模型"""

    url: str = Field(..., description="请求的URL")
    content: Optional[Any] = Field(None, description="文档内容")
    success: bool = Field(..., description="是否成功获取文档")
    message: str = Field(..., description="处理结果消息")
