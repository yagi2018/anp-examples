import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
import asyncio
from urllib.parse import urlparse

# 将项目根目录添加到系统路径中
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from anp_examples.utils.log_base import setup_logging
from anp_examples.anp_tool import ANPTool
from web_app.backend.models import (
    QueryRequest,
    QueryResponse,
    AgentDocTreeRequest,
    AgentDocTreeResponse,
    GetDocumentRequest,
    GetDocumentResponse,
)
from anp_examples.simple_example import simple_crawl

# 设置日志
setup_logging(logging.INFO)

# 获取项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = Path(__file__).resolve().parent.parent.parent

# 初始化 FastAPI 应用
app = FastAPI(
    title="智能体网络搜索",
    description="基于 ANP 协议的智能体网络搜索应用",
    version="1.0.0",
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)

# 挂载静态文件目录
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# 获取 DID 路径
did_document_path = str(ROOT_DIR / "use_did_test_public/did.json")
private_key_path = str(ROOT_DIR / "use_did_test_public/key-1_private.pem")


@app.get("/", response_class=HTMLResponse)
async def read_root():
    """提供前端页面"""
    try:
        with open(BASE_DIR / "frontend" / "index.html", "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        logging.error(f"读取前端页面出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"读取前端页面出错: {str(e)}")


@app.get("/agent-doc-tree.html", response_class=HTMLResponse)
async def read_agent_doc_tree():
    """提供智能体文档树结构页面"""
    try:
        with open(
            BASE_DIR / "frontend" / "agent-doc-tree.html", "r", encoding="utf-8"
        ) as f:
            content = f.read()
        return content
    except Exception as e:
        logging.error(f"读取智能体文档树结构页面出错: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"读取智能体文档树结构页面出错: {str(e)}"
        )


@app.get("/jsonld-viewer", response_class=HTMLResponse)
async def read_jsonld_viewer():
    """提供JSON-LD查看器页面"""
    try:
        with open(
            BASE_DIR / "frontend" / "jsonld-viewer.html", "r", encoding="utf-8"
        ) as f:
            content = f.read()
        return content
    except Exception as e:
        logging.error(f"读取JSON-LD查看器页面出错: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"读取JSON-LD查看器页面出错: {str(e)}"
        )


@app.get("/jsonld-network", response_class=HTMLResponse)
async def read_jsonld_network():
    """提供JSON-LD网络页面"""
    try:
        with open(
            BASE_DIR / "frontend" / "jsonld-network.html", "r", encoding="utf-8"
        ) as f:
            content = f.read()
        return content
    except Exception as e:
        logging.error(f"读取JSON-LD网络页面出错: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"读取JSON-LD网络页面出错: {str(e)}"
        )


@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok", "service": "智能体网络搜索 API"}


@app.post("/api/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """处理查询请求"""
    try:
        # 使用用户提供的智能体 URL 或默认 URL
        initial_url = (
            request.agent_url
            if request.agent_url
            else "https://agent-search.ai/ad.json"
        )

        # 调用 simple_crawl 函数
        result = await simple_crawl(
            user_input=request.query,
            task_type="general",
            did_document_path=did_document_path,
            private_key_path=private_key_path,
            max_documents=10,  # 最多爬取 10 个文档
            initial_url=initial_url,  # 传入用户提供的URL
        )

        return result
    except Exception as e:
        logging.error(f"查询处理时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"处理查询时出错: {str(e)}")


@app.post("/api/agent-doc-tree", response_model=AgentDocTreeResponse)
async def agent_doc_tree(request: AgentDocTreeRequest):
    """解析智能体URL及其子文档，构建文档树"""
    try:
        # 使用用户提供的智能体 URL 或默认 URL
        initial_url = (
            request.agent_url
            if request.agent_url
            else "https://agent-search.ai/ad.json"
        )

        # 初始化 ANPTool
        anp_tool = ANPTool(
            did_document_path=did_document_path, private_key_path=private_key_path
        )

        # 初始化访问过的URL和爬取的文档列表
        visited_urls = set()
        crawled_documents = []

        # 递归获取文档
        await crawl_doc_tree(
            initial_url, anp_tool, visited_urls, crawled_documents, level=0, max_level=5
        )

        # 处理文档树结构
        doc_tree = process_doc_tree(crawled_documents)

        return {
            "doc_tree": doc_tree,
            "visited_urls": list(visited_urls),
            "crawled_documents": crawled_documents,
        }
    except Exception as e:
        logging.error(f"构建文档树时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=f"构建文档树时出错: {str(e)}")


async def crawl_doc_tree(
    url, anp_tool, visited_urls, crawled_documents, level=0, max_level=5, max_docs=30
):
    """递归获取文档及其链接的函数"""
    # 如果已经访问过该URL或已达最大深度或文档数量限制，则返回
    if url in visited_urls or level >= max_level or len(crawled_documents) >= max_docs:
        return

    try:
        # 使用ANPTool获取URL内容
        result = await anp_tool.execute(url=url)

        # 记录访问的URL和获取的内容
        visited_urls.add(url)
        crawled_documents.append({"url": url, "method": "GET", "content": result})

        logging.info(f"获取文档成功: {url}, 当前深度: {level}")

        # 提取文档中的链接
        links = extract_links(result)

        # 递归获取链接的文档
        for link in links:
            if len(crawled_documents) >= max_docs:
                break

            # 跳过已经访问过的URL
            if link in visited_urls:
                continue

            await crawl_doc_tree(
                link,
                anp_tool,
                visited_urls,
                crawled_documents,
                level + 1,
                max_level,
                max_docs,
            )

    except Exception as e:
        logging.error(f"获取文档失败: {url}, 错误: {str(e)}")


def extract_links(data):
    """从JSON-LD文档中提取链接"""
    links = set()

    def traverse(obj):
        if not obj or not isinstance(obj, dict):
            return

        # 处理特定字段中的链接
        for key in ["@id", "url", "serviceEndpoint"]:
            if key in obj and isinstance(obj[key], str) and is_valid_url(obj[key]):
                links.add(obj[key])

        # 检查其他属性是否为对象或数组
        for key, value in obj.items():
            if key == "@context":
                continue  # 跳过@context

            if isinstance(value, dict):
                traverse(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        traverse(item)

    traverse(data)
    return links


def is_valid_url(url):
    """验证URL是否有效"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def process_doc_tree(documents):
    """处理文档，构建树状结构"""
    doc_tree = {"name": "根节点", "children": []}
    url_map = {}

    # 首先添加所有文档节点
    for doc in documents:
        url = doc["url"]
        node = {"name": url.split("/")[-1], "url": url, "children": [], "doc": doc}
        url_map[url] = node

        # 如果是根节点
        if doc == documents[0]:
            doc_tree["children"].append(node)

    # 然后建立连接关系
    for doc in documents[1:]:  # 跳过第一个(根)文档
        url = doc["url"]
        node = url_map[url]

        # 查找父节点
        found_parent = False
        for parent_doc in documents:
            parent_url = parent_doc["url"]
            if parent_url == url:
                continue

            # 检查父文档内容中是否包含当前URL
            try:
                content_str = str(parent_doc["content"])
                if url in content_str:
                    # 找到了可能的父节点
                    parent_node = url_map[parent_url]
                    parent_node["children"].append(node)
                    found_parent = True
                    break
            except:
                pass

        # 如果没有找到父节点，添加到根节点
        if not found_parent:
            doc_tree["children"].append(node)

    return doc_tree


@app.post("/api/get-document", response_model=GetDocumentResponse)
async def get_document(request: GetDocumentRequest):
    """根据URL获取文档内容"""
    try:
        # 获取URL
        url = request.url
        if not url:
            raise HTTPException(status_code=400, detail="URL参数不能为空")

        # 初始化ANPTool
        anp_tool = ANPTool(
            did_document_path=did_document_path, private_key_path=private_key_path
        )

        # 使用ANPTool获取URL内容
        try:
            result = await anp_tool.execute(url=url)

            return {
                "url": url,
                "content": result,
                "success": True,
                "message": "获取文档成功",
            }
        except Exception as e:
            logging.error(f"通过ANPTool获取文档失败: {url}, 错误: {str(e)}")
            return {
                "url": url,
                "content": None,
                "success": False,
                "message": f"获取文档失败: {str(e)}",
            }

    except Exception as e:
        logging.error(f"获取文档失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取文档失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    # 启动端口
    port = int(os.environ.get("PORT", 9871))

    # 启动 uvicorn 服务器
    uvicorn.run(
        "anp_examples_backend:app",
        host="0.0.0.0",
        port=port,
        reload=True,
    )
