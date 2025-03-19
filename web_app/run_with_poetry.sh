#!/bin/bash

# 设置工作目录
cd "$(dirname "$0")"

# 获取当前目录
CURRENT_DIR="$(pwd)"
PROJECT_ROOT="$(dirname "$CURRENT_DIR")"

# 确保在项目根目录有最新的依赖
cd "$PROJECT_ROOT"
echo "正在安装依赖..."
poetry install

# 启动服务器
echo "正在启动智能体网络搜索服务..."
cd "$CURRENT_DIR/backend"
poetry run python main.py 