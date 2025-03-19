import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
import asyncio

# 将项目根目录添加到系统路径中
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from anp_examples.utils.log_base import setup_logging
from anp_examples.anp_tool import ANPTool
from web_app.backend.models import QueryRequest, QueryResponse
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


@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok", "service": "智能体网络搜索 API"}


@app.post("/api/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """处理查询请求"""
    try:
        # 使用用户提供的智能体 URL 或默认 URL
        initial_url = request.agent_url if request.agent_url else "https://agent-search.ai/ad.json"
        
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


if __name__ == "__main__":
    import uvicorn
    
    # 启动端口
    port = int(os.environ.get("PORT", 8000))
    
    # 启动 uvicorn 服务器
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
    ) 