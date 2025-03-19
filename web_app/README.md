# 智能体网络搜索应用

这是一个基于 Agent Network Protocol (ANP) 的智能体网络搜索应用，允许用户使用自然语言提问，并通过智能体网络获取答案。

## 功能特点

- 自然语言输入：用户可以用自然语言提问
- 智能体网络探索：使用 ANP 协议与智能体网络交互
- 实时爬取展示：在右侧边栏实时显示爬取的 URL 和内容
- 黑暗/明亮模式：支持深色和浅色主题切换
- 响应式设计：在各种设备上都能完美展示

## 快速开始

### 1. 前提条件

确保您已安装以下软件：
- Python 3.8+
- pip 包管理器或 Poetry

### 2. 安装与运行

#### 使用启动脚本

只需执行启动脚本：

```bash
./run.sh
```

#### 使用 pip 手动设置

```bash
# 安装依赖
pip install -r backend/requirements.txt

# 添加项目根目录到 PYTHONPATH
export PYTHONPATH=$(pwd)/..:$PYTHONPATH

# 启动服务器
cd backend
python main.py
```

#### 使用 Poetry 安装

如果您使用 Poetry 管理依赖，可以运行：

```bash
# 在项目根目录安装依赖
poetry install

# 使用 Poetry 环境运行服务器
cd web_app/backend
poetry run python main.py
```

### 3. 访问应用

打开浏览器，访问：

```
http://localhost:8000/
```

## 使用方法

1. 在输入框中输入您的自然语言问题，例如：
   - "我想预订杭州的酒店"
   - "帮我查找附近的景点"

2. 可选地，您可以指定一个智能体描述文档的 URL，例如：
   - `https://agent-search.ai/ad.json`

3. 点击"提交问题"按钮。

4. 在右侧边栏查看系统访问的 URL 和爬取的数据。

## 技术架构

- 前端：HTML, CSS, JavaScript, Tailwind CSS, Font Awesome
- 后端：FastAPI, Python
- 智能体交互：ANP 协议, OpenAI API
- 配置：dotenv
- 依赖管理：pip 或 Poetry

## 项目结构

```
web_app/
├── backend/            # 后端代码
│   ├── main.py         # 主服务器入口
│   ├── models.py       # 数据模型
│   ├── requirements.txt # 依赖列表
│   └── static_server.py # 静态文件服务器
├── frontend/           # 前端文件
│   └── index.html      # 主页面
├── static/             # 静态资源
├── run.sh              # 启动脚本
└── README.md           # 本文档
```

## Poetry 依赖配置

项目使用 Poetry 进行依赖管理，依赖项已在项目根目录的 `pyproject.toml` 文件中定义。主要依赖包括：

- fastapi: ^0.105.0
- uvicorn: ^0.23.2
- python-dotenv: ^1.0.0
- openai: ^1.3.7
- pydantic: ^2.4.2
- aiohttp: ^3.8.5
- pyyaml: ^6.0
- agent-connect: ^0.3.5

## 未来计划

- 增加更多智能体服务支持
- 优化搜索速度和质量
- 添加历史记录功能
- 实现多轮对话能力 